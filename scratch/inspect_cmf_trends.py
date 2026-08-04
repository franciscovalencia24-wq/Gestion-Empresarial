import pandas as pd
import os

file_path = "data/cmf/rentabilidad/articles-91850_document_2.xlsx"

if os.path.exists(file_path):
    # Obtener nombres de las hojas
    xl = pd.ExcelFile(file_path)
    print(f"Hojas: {xl.sheet_names}")
    
    # Leer la primera hoja para ver la estructura
    df = pd.read_excel(file_path, sheet_name=xl.sheet_names[0], nrows=5)
    print(f"Columnas detectadas: {df.columns.tolist()}")
    
    # Intentar leer con una fila de encabezado diferente si es necesario
    # A veces los archivos de la CMF tienen el encabezado en la fila 3-5
    df2 = pd.read_excel(file_path, sheet_name=xl.sheet_names[0], skiprows=4, nrows=5)
    print(f"\nColumnas (skiprows=4): {df2.columns.tolist()}")
    print(df2.head().to_string())
else:
    print(f"Archivo no encontrado: {file_path}")
