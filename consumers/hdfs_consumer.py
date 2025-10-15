import os
import json
import time
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from hdfs import InsecureClient

# Kafka Configuration
KAFKA_TOPIC = "prediction_results"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
CONSUMER_GROUP_ID = "casting-defect-consumers"

# HDFS Configuration
HDFS_NAMENODE_URL = "http://namenode:9870"
HDFS_USER = "root"

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
                auto_offset_reset='earliest',
                group_id=CONSUMER_GROUP_ID,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            print("Successfully connected to Kafka.")
            return consumer
        except KafkaError as e:
            print(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def get_hdfs_client():
    """
    Creates and returns an HDFS client.
    """
    return InsecureClient(HDFS_NAMENODE_URL, user=HDFS_USER)

def main():
    """
    Main function to run the Kafka consumer and write to HDFS.
    """
    consumer = create_consumer()
    hdfs_client = get_hdfs_client()

    print(f"Listening for messages on topic '{KAFKA_TOPIC}'...")

    for message in consumer:
        try:
            prediction_data = message.value
            filename = f"/predictions/{message.offset}.json"
            
            # Ensure the /predictions directory exists
            if not hdfs_client.status("/predictions", strict=False):
                hdfs_client.makedirs("/predictions")

            with hdfs_client.write(filename, encoding='utf-8') as writer:
                json.dump(prediction_data, writer)
            
            print(f"Successfully wrote message with offset {message.offset} to HDFS at {filename}")

        except Exception as e:
            print(f"Error processing message or writing to HDFS: {e}")

if __name__ == "__main__":
    main()