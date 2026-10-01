import os
import sys
import pandas as pd
import logging
from datetime import datetime

sys.path.append(os.getcwd())
from src.database.connection import SessionLocal
from src.database.models import EmpresaB2B, EjecutivoB2B
from src.security.encryption import encrypt_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("b2b_importer")

def clean_rut(rut_raw):
    if pd.isna(rut_raw):
        return None
    r = str(rut_raw).replace(".", "").replace("-", "").strip().upper()
    if len(r) > 1:
        return f"{r[:-1]}-{r[-1]}"
    return r

def import_b2b_executives(empresa_rut: str, file_path: str):
    """
    Importa una nómina de ejecutivos B2B desde Excel o CSV, validando
    cupos, generando tokens únicos e insertando en DB sin duplicados.
    Columnas esperadas: RUT, Nombre, Correo, Cargo
    """
    if not os.path.exists(file_path):
        return {"status": "error", "message": f"Archivo {file_path} no encontrado."}
    
    db = SessionLocal()
    try:
        empresa_rut_clean = clean_rut(empresa_rut)
        empresa = db.query(EmpresaB2B).filter_by(rut=empresa_rut_clean).first()
        
        if not empresa:
            return {"status": "error", "message": f"La empresa B2B con RUT {empresa_rut_clean} no está registrada."}
            
        if not empresa.estado_activo:
            return {"status": "error", "message": f"La empresa B2B con RUT {empresa_rut_clean} no se encuentra activa."}

        # Cargar datos
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Validar columnas
        required_cols = {"RUT", "Nombre", "Correo", "Cargo"}
        if not required_cols.issubset(set(df.columns)):
            return {"status": "error", "message": f"Columnas faltantes. Se requiere: {', '.join(required_cols)}"}

        current_executives_count = db.query(EjecutivoB2B).filter_by(empresa_id=empresa.id).count()
        new_executives_count = 0
        added_records = []
        skipped_records = []

        for idx, row in df.iterrows():
            rut = clean_rut(row.get("RUT"))
            if not rut:
                continue

            nombre = str(row.get("Nombre")).strip()
            correo = str(row.get("Correo")).strip()
            cargo = str(row.get("Cargo")).strip()

            # Evitar duplicados
            exist_exec = db.query(EjecutivoB2B).filter_by(rut=rut).first()
            if exist_exec:
                skipped_records.append(rut)
                continue
                
            # Validar cupos
            if empresa.cupo_licencias != float('inf') and (current_executives_count + new_executives_count >= empresa.cupo_licencias):
                return {
                    "status": "warning", 
                    "message": f"Límite de licencias alcanzado ({empresa.cupo_licencias}). Se importaron {new_executives_count} registros."
                }

            # Generar token de acceso único y cifrado
            token_bruto = f"{empresa.rut}::{rut}::{datetime.utcnow().timestamp()}"
            token_cifrado = encrypt_data(token_bruto)

            nuevo_ejecutivo = EjecutivoB2B(
                empresa_id=empresa.id,
                rut=rut,
                nombre_completo=nombre,
                correo_corporativo=correo,
                cargo=cargo,
                token_acceso=token_cifrado,
                estado_onboarding="Pendiente"
            )
            db.add(nuevo_ejecutivo)
            new_executives_count += 1
            added_records.append(rut)

        db.commit()
        
        return {
            "status": "success",
            "message": f"Nómina procesada. Se agregaron {new_executives_count} ejecutivos.",
            "added": len(added_records),
            "skipped_duplicates": len(skipped_records)
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error procesando nómina B2B: {e}", exc_info=True)
        return {"status": "error", "message": f"Error interno: {str(e)}"}
    finally:
        db.close()

if __name__ == "__main__":
    # Test script if executed directly
    print("Módulo de Ingesta B2B inicializado.")
