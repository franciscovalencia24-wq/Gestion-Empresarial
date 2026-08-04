import os
import sys
sys.path.append(os.getcwd())
import pandas as pd
from sqlalchemy import text
from src.database.connection import engine

try:
    with engine.connect() as con:
        res = con.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in res]
        print("Tablas encontradas:", tables)
        
    for table in tables:
        try:
            df = pd.read_sql(f"SELECT * FROM {table} LIMIT 1", con=engine)
            print(f"\nTabla: {table}")
            print("Columnas:", df.columns.tolist())
        except:
            print(f"\nTabla: {table} (Vacía o error)")
except Exception as e:
    print(f"Error: {e}")
