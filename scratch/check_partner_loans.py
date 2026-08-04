import sys, os, sqlite3
sys.path.insert(0, os.getcwd())
from src.database.connection import SessionLocal
from src.database.models import CompanyFinancialMovement

db = SessionLocal()
movs = db.query(CompanyFinancialMovement).filter(CompanyFinancialMovement.tipo_movimiento.in_(["PRESTAMO_SOCIO", "DEVOLUCION_SOCIO"])).all()
print(f"Total partner loan movements: {len(movs)}")
for m in movs:
    print(f"ID: {m.id} | Tipo: {m.tipo_movimiento} | Empresa: {m.empresa} | Socio/Razon: '{m.razon_social}' | Monto: {m.monto_total} | Fecha: {m.fecha}")
db.close()
