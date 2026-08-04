import sqlite3
import os

DB_PATH = "C:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/data/processed/prospectos.db"
conn = sqlite3.connect(DB_PATH)

# Prospectos con teléfono válido
res_tel = conn.execute("SELECT COUNT(*) FROM prospects WHERE telefono IS NOT NULL AND telefono != 'No encontrado'").fetchone()
# Procesados por Transunion (tuvieran éxito o no)
res_tu = conn.execute("SELECT COUNT(*) FROM prospects WHERE observaciones LIKE '%TRANSUNION%'").fetchone()

print(f"Contactables (Con Teléfono): {res_tel[0]}")
print(f"Total Procesados por TransUnion: {res_tu[0]}")

conn.close()
