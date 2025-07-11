from fastapi import FastAPI
from pydantic import BaseModel
from db import SessionLocal
from models import Inventory

app = FastAPI()

class InventoryIn(BaseModel):
    item: str
    quantity: int

@app.post("/inventory")
def create_inventory_item(item: InventoryIn):
    db = SessionLocal()
    existing = db.query(Inventory).filter(Inventory.item == item.item).first()
    if existing:
        return {"message": "Item already exists"}

    new_inventory_item = Inventory(item=item.item, quantity=item.quantity)
    db.add(new_inventory_item)
    db.commit()
    db.refresh(new_inventory_item)
    print(f"✅ [INVENTORY] Item creado: {new_inventory_item.item} con {new_inventory_item.quantity} unidades")
    return {"message": "Inventory item created", "item_id": new_inventory_item.id}

@app.get("/inventory/by-name/{item_name}")
def get_inventory_by_name(item_name: str):
    db = SessionLocal()
    item = db.query(Inventory).filter(Inventory.item == item_name).first()
    if not item:
        return {"message": "Item not found"}
    return {"id": item.id, "item": item.item, "quantity": item.quantity}

@app.get("/inventory")
def get_all_inventory():
    db = SessionLocal()
    items = db.query(Inventory).all()
    return [{"id": item.id, "item": item.item, "quantity": item.quantity} for item in items]