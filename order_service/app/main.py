from fastapi import FastAPI
from pydantic import BaseModel
from db import SessionLocal
from models import Order
from kafka_producer import send_order_event

app = FastAPI()

class OrderIn(BaseModel):
    item: str
    quantity: int

@app.post("/order")
def create_order(order: OrderIn):
    db = SessionLocal()
    try:
        new_order = Order(item=order.item, quantity=order.quantity, status="created")
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        send_order_event({
            "id": new_order.id,
            "item": new_order.item,
            "quantity": new_order.quantity
        })

        print(f"✅ [ORDER] Orden creada: {new_order}")
        return {"message": "Order created", "order_id": new_order.id}
    finally:
        db.close()  # Asegura que la sesión se cierre

@app.get("/orders")
def get_orders():
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        return [{"id": order.id, "item": order.item, "quantity": order.quantity, "status": order.status} for order in orders]
    finally:
        db.close()  # También aquí
