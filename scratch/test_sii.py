import pandas as pd
import sys
import os

sys.path.append(os.getcwd())
from src.ingestion.sii_importer import process_sii_dataframe

def test_sii():
    compra_csv = "RCV_COMPRA_REGISTRO_78328835-4_202607_33 (1).csv"
    venta_csv = "RCV_VENTA_78328835-4_202607_33.csv"
    
    for f in [compra_csv, venta_csv]:
        if os.path.exists(f):
            print(f"\nProcesando {f}...")
            try:
                # El SII suele usar codificación iso-8859-1 o latin-1
                with open(f, "r", encoding="latin-1", errors="replace") as file:
                    df = pd.read_csv(file, sep=';', index_col=False)
                res = process_sii_dataframe(df, "FV Asesorías SpA", f)
                print(res)
            except Exception as e:
                print(f"Error parseando {f}: {e}")
        else:
            print(f"No se encontro {f}")

if __name__ == "__main__":
    test_sii()
