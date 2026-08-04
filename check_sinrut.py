import sqlite3
import os

DB_PATH = "C:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/data/processed/prospectos.db"
conn = sqlite3.connect(DB_PATH)
res = conn.execute("SELECT COUNT(*) FROM prospects WHERE rut LIKE 'SINRUT%'").fetchone()
print(f"SINRUT Actual: {res[0]}")
conn.close()
