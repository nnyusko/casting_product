import os
import json
import io
import asyncio
from contextlib import asynccontextmanager
from typing import List
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
import tensorflow as tf
from PIL import Image
import numpy as np
from kafka import KafkaProducer
from kafka.errors import KafkaError

# --- Kafka Configuration ---
KAFKA_TOPIC = "prediction_results"
# Get Kafka bootstrap servers from environment variable, default to localhost for local running
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# --- Connection Manager for WebSockets ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- App Context (Model & Kafka Producer) ---
app_context = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML Model
    model_path = 'models/casting_defect_detection_model.keras'
    app_context['defect_detector'] = tf.keras.models.load_model(model_path)
    print(f"Model {model_path} loaded successfully.")

    # Initialize Kafka Producer with retry logic
    print(f"Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}...")
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=5,
                acks='all'
            )
            app_context['kafka_producer'] = producer
            print("Successfully connected to Kafka.")
            break  # Exit the loop on successful connection
        except KafkaError as e:
            print(f"Could not connect to Kafka: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

    yield

    # Clean up resources
    print("Clearing resources...")
    if app_context.get('kafka_producer'):
        app_context['kafka_producer'].close()
        print("Kafka producer closed.")
    app_context.clear()
    print("App context cleared.")


app = FastAPI(lifespan=lifespan)

# Mount static files directory
app.mount("/static", StaticFiles(directory="api/static"), name="static")

CLASS_NAMES = ['def_front', 'ok_front']

# --- HTML Frontend Route ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("api/static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("A client disconnected.")

# --- Prediction Endpoint ---
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception:
        return {"error": "Could not read image file."}

    image = image.convert('L').resize((300, 300))
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=[0, -1])

    model = app_context.get('defect_detector')
    if model is None: return {"error": "Model is not loaded."}

    prediction = await run_in_threadpool(model.predict, image_array)
    score = float(prediction[0][0])

    if score < 0.5:
        predicted_class = CLASS_NAMES[0]
        confidence = 1 - score
        await manager.broadcast(f'{{"type": "defect_detected", "filename": "{file.filename}"}}')
    else:
        predicted_class = CLASS_NAMES[1]
        confidence = score

    # --- Produce message to Kafka ---
    producer = app_context.get('kafka_producer')
    if producer:
        prediction_data = {
            "filename": file.filename,
            "prediction": predicted_class,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        try:
            producer.send(KAFKA_TOPIC, value=prediction_data)
            producer.flush() # Ensure message is sent
            print(f"Message sent to Kafka topic '{KAFKA_TOPIC}': {prediction_data}")
        except KafkaError as e:
            print(f"Failed to send message to Kafka: {e}")
    else:
        print("Kafka producer not available. Skipping message send.")
    # --- End Kafka integration ---

    return {
        "filename": file.filename,
        "prediction": predicted_class,
        "confidence": f"{confidence:.2%}"
    }