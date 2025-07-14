from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# Leer la URL desde la variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@db_order:5432/orders")

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30
)

SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)
