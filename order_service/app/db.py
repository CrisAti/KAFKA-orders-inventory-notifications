from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

engine = create_engine("sqlite:////app/orders.db", connect_args={"check_same_thread": False},
    pool_size=20,           # 🔼 aumenta el tamaño del pool
    max_overflow=30,        # 🔼 permite 30 conexiones extra temporales
    pool_timeout=30         )
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)
