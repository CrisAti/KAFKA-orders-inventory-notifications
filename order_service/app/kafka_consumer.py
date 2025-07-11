from confluent_kafka import Consumer
from db import SessionLocal
from models import Order
import json, os

consumer = Consumer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    'group.id': 'order-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(["inventory", "notifications"])

print("📦 [ORDER] Escuchando eventos de 'inventory' y 'notifications'...")

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print("❌ Error Kafka:", msg.error())
        continue

    event = json.loads(msg.value().decode("utf-8"))
    print(f"🔍 [ORDER] Evento recibido: {event}")

    db = SessionLocal()
    data = event.get("data", {})
    order = db.query(Order).filter(Order.id == data.get("id")).first()
    if not order:
        print(f"⚠️ Orden {data.get('id')} no encontrada")
        continue

    if event["type"] == "inventory_updated":
        status = data.get("status")
        if status == "success":
            order.status = "accepted"
        else:
            order.status = f"failed:{data.get('error', 'unknown')}"
        print(f"📝 [ORDER] Estado actualizado por inventario: {order.status}")

    elif event["type"] == "notification_sent":
        if data.get("status") == "success":
            order.status = "notified"
        else:
            order.status = "notification_failed"
        print(f"📨 [ORDER] Estado actualizado por notificación: {order.status}")

    db.commit()
