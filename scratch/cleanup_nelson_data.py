import sys
import os

sys.path.insert(0, os.path.abspath('.'))

from src.database.connection import SessionLocal
from src.database.models import Prospect, ClientHeir, ClientProperty
from src.osint.indicadores import get_uf_today

def cleanup_data():
    db = SessionLocal()
    p = db.query(Prospect).filter(Prospect.rut.like("%6298500%")).first()
    if not p:
        print("Prospect Nelson Moraga not found!")
        return

    print(f"Cleaning up data for Prospect ID {p.id} ({p.nombre})...")

    # 1. ELIMINAR REGISTRO DUMMY 'Extraído por IA' DE HEREDEROS
    dummy_heirs = db.query(ClientHeir).filter(ClientHeir.prospect_id == p.id, ClientHeir.nombre == "Extraído por IA").all()
    for dh in dummy_heirs:
        print(f" Deleting dummy heir ID {dh.id}: {dh.nombre}")
        db.delete(dh)

    # Asegurar herederos reales con porcentajes legales
    real_heirs = db.query(ClientHeir).filter(ClientHeir.prospect_id == p.id, ClientHeir.nombre != "Extraído por IA").all()
    for rh in real_heirs:
        if "Matilde" in rh.nombre:
            rh.porcentaje_asignacion = 66.67
            rh.relacion = "Cónyuge"
        elif "Nelson" in rh.nombre:
            rh.porcentaje_asignacion = 33.33
            rh.relacion = "Hijo/a"

    # 2. FUSIONAR PROPIEDAD N°7 (ROL 01026-0001) EN LA PROPIEDAD N°1 DE COQUIMBO
    prop1 = db.query(ClientProperty).filter(ClientProperty.prospect_id == p.id, ClientProperty.id == 4).first()
    prop_duplicate = db.query(ClientProperty).filter(ClientProperty.prospect_id == p.id, ClientProperty.id == 10).first()

    uf_val = get_uf_today() or 38850.0
    val_kyc_uf = round(150000000.0 / uf_val, 2) # ~$150M CLP a UF (~3.861 UF)

    if prop1:
        prop1.rol = "01026-0001"
        prop1.direccion = "Psje Rio Caren 901, Peñuelas - Coquimbo"
        prop1.comuna = "COQUIMBO"
        prop1.observaciones = "Propiedad Coquimbo Peñuelas (ROL 01026-0001 - Valorizada en $150M CLP en KYC)"
        prop1.valor_comercial_estimado = val_kyc_uf
        prop1.hipoteca_valor_tasacion = val_kyc_uf
        print(f" Updated Property ID 4 (Coquimbo): ROL={prop1.rol}, Valor UF={val_kyc_uf}")

    if prop_duplicate:
        print(f" Deleting duplicate property ID {prop_duplicate.id} ({prop_duplicate.rol})")
        db.delete(prop_duplicate)

    # 3. POBLAR COLUMNA 'hipoteca_valor_tasacion' (Tasación UF) PARA TODAS LAS PROPIEDADES
    all_props = db.query(ClientProperty).filter(ClientProperty.prospect_id == p.id).all()
    for pr in all_props:
        if pr.id != 10:
            if not pr.hipoteca_valor_tasacion or pr.hipoteca_valor_tasacion == 0.0:
                pr.hipoteca_valor_tasacion = pr.valor_comercial_estimado or round(pr.avaluo_fiscal * 1.85 / uf_val, 2)
            print(f" Prop ID {pr.id} ({pr.comuna}): Avalúo CLP=${pr.avaluo_fiscal:,.0f} | Tasación UF={pr.hipoteca_valor_tasacion:,.2f} UF")

    db.commit()
    db.close()
    print("Cleanup completed successfully.")

if __name__ == "__main__":
    cleanup_data()
