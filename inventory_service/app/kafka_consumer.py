from confluent_kafka import Consumer
from db import SessionLocal
from models import Inventory
from kafka_producer import send_inventory_event
import json, os

consumer = Consumer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    'group.id': 'inventory-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(["orders"])
print("📦 [INVENTORY] Escuchando eventos de 'orders'...")

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print("❌ Error Kafka:", msg.error())
        continue

    event = json.loads(msg.value().decode("utf-8"))
    print(f"🔍 [INVENTORY] Evento recibido: {event}")

    if event["type"] == "order_created":
        data = event["data"]
        db = SessionLocal()
        item = db.query(Inventory).filter(Inventory.item == data["item"]).first()

        if not item:
            print(f"❌ [INVENTORY] Producto '{data['item']}' no encontrado")
            send_inventory_event({
                "id": data["id"],
                "item": data["item"],
                "quantity": 0,
                "status": "failed",
                "error": "item_not_found"
            })
            continue

        if item.quantity < data["quantity"]:
            print(f"❌ [INVENTORY] Stock insuficiente para '{item.item}'. Disponible: {item.quantity}, Solicitado: {data['quantity']}")
            send_inventory_event({
                "id": data["id"],
                "item": item.item,
                "quantity": item.quantity,
                "status": "failed",
                "error": "insufficient_quantity"
            })
            continue

        item.quantity -= data["quantity"]
        db.commit()
        print(f"✅ [INVENTORY] Stock reducido: {item.item} → {item.quantity} restantes")
        send_inventory_event({
            "id": data["id"],
            "item": item.item,
            "quantity": item.quantity,
            "order_quantity": data["quantity"],
            "status": "success"
        })
