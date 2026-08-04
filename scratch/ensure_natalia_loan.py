import sys, os, datetime
sys.path.insert(0, os.getcwd())
from src.database.connection import SessionLocal
from src.database.models import CompanyFinancialMovement

db = SessionLocal()

# Check if loan to Natalia already exists in DB
existing = db.query(CompanyFinancialMovement).filter(
    CompanyFinancialMovement.tipo_movimiento == "PRESTAMO_SOCIO",
    CompanyFinancialMovement.razon_social.contains("NATALIA"),
    CompanyFinancialMovement.monto_total == 2500000.0
).first()

if not existing:
    print("Adding PRESTAMO_SOCIO for Natalia Tapia ($2.500.000)...")
    mov = CompanyFinancialMovement(
        empresa="FV Asesorías SpA",
        tipo_movimiento="PRESTAMO_SOCIO",
        categoria="PRESTAMO SOCIO",
        fecha=datetime.date(2026, 7, 28),
        periodo="2026-07",
        rut_contraparte="",
        razon_social="NATALIA TAPIA (SOCIA)",
        concepto="Préstamo a Socia Natalia Tapia",
        monto_neto=2500000.0,
        monto_iva=0.0,
        monto_total=2500000.0,
        cuenta_corriente="CTA. CTE. BCI: FV ASESORIAS",
        observaciones="Registrado manualmente desde Dashboard Web"
    )
    db.add(mov)
    db.commit()
    print("✅ Registered Natalia loan of $2.500.000 dated 28.07.2026 in DB!")
else:
    print(f"Existing loan for Natalia found: ID {existing.id}")

db.close()
