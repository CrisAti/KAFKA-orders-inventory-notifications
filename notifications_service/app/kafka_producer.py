from confluent_kafka import Producer
import json, os

producer = Producer({'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")})

def send_notification_event(data):
    event = {"type": "notification_sent", "data": data}
    print(f"📤 [NOTIFICATION] Enviando evento: {event}")
    producer.produce("notifications", json.dumps(event).encode("utf-8"))
    producer.flush()
