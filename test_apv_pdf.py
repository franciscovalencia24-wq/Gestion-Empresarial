import os
import sys
import pandas as pd

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.pdf_generator_apv import generar_pdf_apv
from src.database.connection import SessionLocal
from src.database.models import Prospect

print("Imports exitosos.")

# Test DB Connection
db = SessionLocal()
try:
    prospect = db.query(Prospect).first()
    if prospect:
        print(f"DB Test Exitoso. Encontrado: {prospect.nombre}")
    else:
        print("DB Test Exitoso. Base de datos vacía pero conexión ok.")
except Exception as e:
    print(f"Error DB: {e}")
finally:
    db.close()

# Test PDF Generation
try:
    df_mock = pd.DataFrame({
        "Año": [1, 2, 3],
        "Ahorro Obligatorio (10%)": [100, 200, 300],
        "Ahorro APV": [50, 100, 150]
    })
    
    pdf_path = generar_pdf_apv(
        rut="11.111.111-1",
        nombre="Test Nombre",
        sueldo=5000000,
        aporte=500000,
        anos=3,
        rentabilidad=0.05,
        ahorro_anual=810000,
        bono_estado=430000,
        df_proy=df_mock
    )
    print(f"PDF generado exitosamente en: {pdf_path}")
    if os.path.exists(pdf_path):
        print("El archivo físico del PDF existe.")
except Exception as e:
    print(f"Error PDF: {e}")
