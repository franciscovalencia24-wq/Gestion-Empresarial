import pandas as pd
from src.database.connection import engine

try:
    df = pd.read_sql("SELECT rut, observaciones FROM prospects WHERE observaciones LIKE '%TRANSUNION RAW:%' LIMIT 3", con=engine)
    for index, row in df.iterrows():
        print(f"--- RUT: {row['rut']} ---")
        print(row['observaciones'])
except Exception as e:
    print(f"Error: {e}")
