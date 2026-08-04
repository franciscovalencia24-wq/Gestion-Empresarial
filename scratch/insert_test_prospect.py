import sqlite3
import pandas as pd
import os

db_path = 'data/processed/prospectos.db'
if not os.path.exists(db_path):
    print("Database not found:", db_path)
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert or update the test prospect
cursor.execute('''
    INSERT OR REPLACE INTO prospects (
        rut, nombre, telefono, email, es_cliente, status_contacto, 
        ciudad, tipo_negocio, origen_info
    ) VALUES (
        '15884242-4', 'FRANCISCO JAVIER VALENCIA AGUILA', '+56966779662', 'francisco.valencia24@gmail.com',
        0, 'Pendiente', 'Simulacro', 'Prueba Motor', 'Test Manual'
    )
''')
conn.commit()

df = pd.read_sql("SELECT rut, nombre, telefono, email, status_contacto FROM prospects WHERE rut='15884242-4'", conn)
print(df)
conn.close()
