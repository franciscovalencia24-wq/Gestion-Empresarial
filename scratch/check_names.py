from src.database.config import SessionLocal
from src.database.models import Prospect

db = SessionLocal()
prospects = db.query(Prospect).limit(10).all()
for p in prospects:
    print(f"ID: {p.id}, Nombre: {p.nombre}")
db.close()
