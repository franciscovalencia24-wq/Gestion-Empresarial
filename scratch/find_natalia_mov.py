import sys, os, sqlite3
sys.path.insert(0, os.getcwd())
from src.database.connection import SessionLocal
from src.database.models import CompanyFinancialMovement

db = SessionLocal()
movs = db.query(CompanyFinancialMovement).all()
print("Searching for 2.500.000 or Natalia movements...")
for m in movs:
    if m.monto_total == 2500000.0 or "NATALIA" in str(m.razon_social).upper() or "NATALIA" in str(m.concepto).upper() or "NATALIA" in str(m.observaciones).upper():
        print(f"ID: {m.id} | Tipo: '{m.tipo_movimiento}' | Categoria: '{m.categoria}' | Socio/Razon: '{m.razon_social}' | Concepto: '{m.concepto}' | Monto: {m.monto_total} | Fecha: {m.fecha}")

db.close()
