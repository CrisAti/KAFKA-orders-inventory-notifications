from confluent_kafka import Producer
import json, os

producer = Producer({'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")})

def send_order_event(order_data):
    event = {"type": "order_created", "data": order_data}
    print(f"📤 [ORDER] Enviando evento: {event}")
    producer.produce("orders", json.dumps(event).encode("utf-8"))
    producer.flush()
