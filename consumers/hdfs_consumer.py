import os
import json
import time
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Kafka Configuration
KAFKA_TOPIC = "prediction_results"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
CONSUMER_GROUP_ID = "casting-defect-consumers"

def create_consumer():
    """
    Creates and returns a KafkaConsumer instance.
    Retries connection if Kafka is not available yet.
    """
    while True:
        try:
            print("Attempting to connect to Kafka...")
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest', # Start reading at the earliest message
                group_id=CONSUMER_GROUP_ID,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            print("Successfully connected to Kafka.")
            return consumer
        except KafkaError as e:
            print(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def main():
    """
    Main function to run the Kafka consumer.
    """
    consumer = create_consumer()
    
    print(f"Listening for messages on topic '{KAFKA_TOPIC}'...")
    
    # Loop forever and process messages
    for message in consumer:
        # In a real scenario, this is where you would write to HDFS.
        # For now, we just print the message to the console.
        print(f"Received message: {message.value}")
        print(f"  - Topic: {message.topic}")
        print(f"  - Partition: {message.partition}")
        print(f"  - Offset: {message.offset}")
        print("-" * 20)

if __name__ == "__main__":
    main()
