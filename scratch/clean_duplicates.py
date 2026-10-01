import sys
import os
sys.path.append(os.getcwd())
from src.database.connection import SessionLocal
from src.database.models import CompanyFinancialMovement

db = SessionLocal()

# Encontrar ingresos importados desde DETALLE 26 (el excel viejo)
viejos = db.query(CompanyFinancialMovement).filter(
    CompanyFinancialMovement.tipo_movimiento == 'INGRESO',
    CompanyFinancialMovement.observaciones.like('%DETALLE 26%')
).all()

folios_viejos = set()
for v in viejos:
    if v.folio_factura and str(v.folio_factura).strip() != 'nan':
        folios_viejos.add(str(v.folio_factura).strip())

# Encontrar los nuevos del SII
nuevos = db.query(CompanyFinancialMovement).filter(
    CompanyFinancialMovement.tipo_movimiento == 'INGRESO',
    CompanyFinancialMovement.observaciones == 'Importado desde SII RCV'
).all()

borrados = 0
for n in nuevos:
    folio_nuevo = str(n.folio_factura).strip()
    if folio_nuevo in folios_viejos:
        print(f"Borrando duplicado Ingreso: ID {n.id}, Folio {folio_nuevo}")
        db.delete(n)
        borrados += 1

db.commit()
print(f"Total borrados Ingresos: {borrados}")
db.close()
