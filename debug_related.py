import sys
import os

# Add src to python path if needed
sys.path.append(os.path.abspath("."))
from src.database.connection import SessionLocal
from src.database.models import Prospect, ClientCompany, CompanyShareholder, ClientMacroHistory

db = SessionLocal()

# RUT of the owner
rut_owner = "8116116-K"
# RUT of the company
rut_company = "77227723-7"

prospect_owner = db.query(Prospect).filter_by(rut=rut_owner).first()
prospect_company = db.query(Prospect).filter_by(rut=rut_company).first()

print(f"Owner prospect: {prospect_owner}")
print(f"Company prospect: {prospect_company}")

if prospect_owner:
    related = prospect_owner.get_related_prospects(db)
    print(f"Related to Owner: {related}")

if prospect_company:
    related = prospect_company.get_related_prospects(db)
    print(f"Related to Company: {related}")
    
# check raw tables
print("\n--- Raw Tables ---")
owner_companies = db.query(ClientCompany).filter_by(prospect_id=prospect_owner.id if prospect_owner else 0).all()
print(f"ClientCompany for owner prospect: {[(c.id, c.rut_empresa, c.razon_social) for c in owner_companies]}")

owner_as_shareholder = db.query(CompanyShareholder).filter_by(rut=rut_owner).all()
print(f"CompanyShareholder where owner is rut: {[(s.id, s.prospect_id, s.rut, s.nombre) for s in owner_as_shareholder]}")

# History
if prospect_owner:
    history = db.query(ClientMacroHistory).filter_by(prospect_id=prospect_owner.id).all()
    print(f"History for Owner: {history}")
if prospect_company:
    history = db.query(ClientMacroHistory).filter_by(prospect_id=prospect_company.id).all()
    print(f"History for Company: {history}")

db.close()
