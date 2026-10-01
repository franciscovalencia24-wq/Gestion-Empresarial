import os
import sqlite3

db_path = r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\data\crm_database.db'

print(f"Migrating database: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE client_companies ADD COLUMN valor_estimado FLOAT DEFAULT 0.0")
    print("Added valor_estimado")
except sqlite3.OperationalError as e:
    print(f"Ignoring error for valor_estimado: {e}")

try:
    cursor.execute("ALTER TABLE client_companies ADD COLUMN posee_bienes_raices BOOLEAN DEFAULT 0")
    print("Added posee_bienes_raices")
except sqlite3.OperationalError as e:
    print(f"Ignoring error for posee_bienes_raices: {e}")

conn.commit()
conn.close()
print("Migration complete.")
