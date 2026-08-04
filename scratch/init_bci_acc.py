import os, sys, sqlite3
sys.path.insert(0, os.getcwd())
from src.database.connection import SessionLocal, Base, engine
from src.database.models import CompanyAccount

# Ensure company_accounts table exists in DB
Base.metadata.create_all(bind=engine)

db = SessionLocal()
bci_acc = db.query(CompanyAccount).filter(CompanyAccount.alias == "CTA. CTE. BCI: FV ASESORIAS").first()

if not bci_acc:
    print("Creating BCI CompanyAccount row...")
    bci_acc = CompanyAccount(
        empresa="FV Asesorías SpA",
        banco="Banco BCI",
        titular="FV Asesorías SpA",
        alias="CTA. CTE. BCI: FV ASESORIAS",
        saldo_actual=21160054.0
    )
    db.add(bci_acc)
    db.commit()
    print("✅ Created BCI account with balance $21.160.054")
else:
    print(f"Existing BCI account balance: {bci_acc.saldo_actual}")
    bci_acc.saldo_actual = 21160054.0
    db.commit()
    print("✅ Updated BCI account balance to $21.160.054")

db.close()
