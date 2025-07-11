from confluent_kafka import Producer
import json, os

producer = Producer({'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")})

def send_inventory_event(inventory_data):
    event = {"type": "inventory_updated", "data": inventory_data}
    print(f"📤 [INVENTORY] Enviando evento: {event}")
    producer.produce("inventory", json.dumps(event).encode("utf-8"))
    producer.flush()
