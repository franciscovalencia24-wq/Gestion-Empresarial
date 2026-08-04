import sys
import os
import datetime

sys.path.insert(0, os.path.abspath('.'))

from src.database.connection import SessionLocal
from src.database.models import Prospect, ClientHeir, ClientProperty, ClientPortfolio

def populate_nelson_data():
    db = SessionLocal()
    prospect = db.query(Prospect).filter(Prospect.rut.like("%6298500%")).first()
    
    if not prospect:
        print("Prospect Nelson Moraga not found!")
        return

    print(f"Found prospect ID: {prospect.id} - {prospect.nombre}")
    
    # 1. Insert Heirs if not exist
    existing_heir_names = [h.nombre for h in db.query(ClientHeir).filter(ClientHeir.prospect_id == prospect.id).all()]
    
    heirs_to_add = [
        {"nombre": "Matilde Ivette Rivera Berndt", "relacion": "Cónyuge", "rut": "9.017.656-0", "porcentaje": 66.67},
        {"nombre": "Nelson Rodrigo Moraga Cires", "relacion": "Hijo/a", "rut": "10.870.820-4", "porcentaje": 33.33}
    ]
    
    for h in heirs_to_add:
        if h["nombre"] not in existing_heir_names:
            heir_obj = ClientHeir(
                prospect_id=prospect.id,
                relacion=h["relacion"],
                nombre=h["nombre"],
                porcentaje_asignacion=h["porcentaje"]
            )
            db.add(heir_obj)
            print(f" Added Heir: {h['nombre']} ({h['relacion']})")
            
    # 2. Insert Property if not exist
    existing_rols = [p.rol for p in db.query(ClientProperty).filter(ClientProperty.prospect_id == prospect.id).all()]
    if "01026-0001" not in existing_rols:
        prop_obj = ClientProperty(
            prospect_id=prospect.id,
            observaciones="Propiedad Peñuelas-Coquimbo (Declarada en KYC)",
            comuna="COQUIMBO",
            rol="01026-0001",
            direccion="ROL 01026-0001 Peñuelas-Coquimbo",
            destino="HABITACIONAL",
            avaluo_fiscal=60000000.0,
            valor_comercial_estimado=3672.44,
            deuda_hipotecaria=0.0,
            porcentaje_derecho=100.0
        )
        db.add(prop_obj)
        print(" Added Property: ROL 01026-0001 Peñuelas-Coquimbo")

    # 3. Insert Insurances / APV declaration (ClientPortfolio)
    existing_ins = [i.institucion for i in db.query(ClientPortfolio).filter(ClientPortfolio.prospect_id == prospect.id).all() if i.institucion]
    for inst in ["Principal APV", "Banco de Chile"]:
        if inst not in existing_ins:
            ins_obj = ClientPortfolio(
                prospect_id=prospect.id,
                institucion=inst,
                activo="APV / Cuenta Corriente (KYC)",
                tipo_activo="APV-B",
                monto_original=0.0,
                moneda_original="CLP",
                monto_clp=0.0,
                objetivo_personal="Declaración KYC Cliente: Principal APV / Banco de Chile"
            )
            db.add(ins_obj)
            print(f" Added Portfolio/APV: {inst}")

    db.commit()
    db.close()
    print("Populated Nelson Moraga KYC records successfully.")

if __name__ == "__main__":
    populate_nelson_data()
