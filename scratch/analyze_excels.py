import os
import pandas as pd
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

folder = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\SIMULADORES Y OTROS"

files = [f for f in os.listdir(folder) if f.endswith('.xlsx') or f.endswith('.xlsm')]

print(f"Encontrados {len(files)} archivos Excel.\n")

for file in files:
    path = os.path.join(folder, file)
    print(f"--- Archivo: {file} ---")
    try:
        xls = pd.ExcelFile(path, engine='openpyxl')
        sheets = xls.sheet_names
        print(f"Hojas: {sheets}")
        
        # Read the first sheet just to see columns
        for sheet in sheets[:2]:  # only first 2 sheets to save space
            try:
                df = pd.read_excel(path, sheet_name=sheet, engine='openpyxl', nrows=5)
                print(f"  Hoja '{sheet}':")
                print(f"  Columnas: {list(df.columns)}")
                print(f"  Primeros 2 filas (preview):")
                print(df.head(2).to_string(index=False))
            except Exception as e:
                print(f"  Error leyendo hoja {sheet}: {e}")
                
    except Exception as e:
        print(f"Error abriendo archivo {file}: {e}")
    print("\n")
