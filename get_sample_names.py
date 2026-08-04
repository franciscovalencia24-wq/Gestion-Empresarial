import sqlite3
import os

DB_PATH = "C:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/data/processed/prospectos.db"
conn = sqlite3.connect(DB_PATH)
res = conn.execute("SELECT nombre FROM prospects WHERE rut LIKE 'SINRUT%' LIMIT 10").fetchall()
for r in res:
    print(r[0])
conn.close()
