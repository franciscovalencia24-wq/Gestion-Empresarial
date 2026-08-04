import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath('.'))

from src.osint.property_lookup_engine import PropertyLookupEngine

def test_ui_flow():
    print("--- SIMULATING STREAMLIT UI FLOW FOR RUT 6298500-3 ---")
    engine = PropertyLookupEngine()
    rut = "6298500-3"
    nombre = "Nelson Orlando Moraga Benavides"
    
    # Initial load
    osint_init = engine.lookup_properties_by_rut(rut, nombre)
    print(f"Initial Load found: {len(osint_init)} properties")
    
    df_p = pd.DataFrame(osint_init)
    print("DataFrame shape:", df_p.shape)
    print("Columns:", df_p.columns.tolist())
    
    # Filter test from client_management_ui.py
    if "ROL" in df_p.columns and "Dirección" in df_p.columns:
        valid_mask = (~df_p["ROL"].fillna("").astype(str).str.strip().isin(["", "nan", "None"])) | (~df_p["Dirección"].fillna("").astype(str).str.strip().isin(["", "nan", "None"])) | (~df_p["Comuna"].fillna("").astype(str).str.strip().isin(["", "nan", "None"]))
        df_p = df_p[valid_mask].reset_index(drop=True)
    print("After valid_mask filter shape:", df_p.shape)
    
    for idx, row in df_p.iterrows():
        print(f" Property #{idx+1}: {row['Nombre/Alias']} | Comuna: {row['Comuna']} | ROL: {row['ROL']} | Sugerido: {row['Valor Sugerido AI (UF)']} UF")

if __name__ == "__main__":
    test_ui_flow()
