from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
import tensorflow as tf
from PIL import Image
import numpy as np
import io
import asyncio
from contextlib import asynccontextmanager
from typing import List

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

# --- Model Loading ---
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = 'models/casting_defect_detection_model.keras'
    ml_models['defect_detector'] = tf.keras.models.load_model(model_path)
    print(f"Model {model_path} loaded successfully.")
    yield
    ml_models.clear()
    print("Models cleared.")

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
            # Keep connection alive
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

    model = ml_models.get('defect_detector')
    if model is None: return {"error": "Model is not loaded."}

    prediction = await run_in_threadpool(model.predict, image_array)
    score = float(prediction[0][0])

    if score < 0.5:
        predicted_class = CLASS_NAMES[0]
        confidence = 1 - score
        # Broadcast defect detection to all connected clients
        await manager.broadcast(f'{{"type": "defect_detected", "filename": "{file.filename}"}}')
    else:
        predicted_class = CLASS_NAMES[1]
        confidence = score

    return {
        "filename": file.filename,
        "prediction": predicted_class,
        "confidence": f"{confidence:.2%}"
    }