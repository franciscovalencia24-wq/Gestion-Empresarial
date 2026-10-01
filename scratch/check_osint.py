import sqlite3
import os
import pprint

db1 = r"c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\data\osint_mass_tracker.db"
db2 = r"c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\data\crm_database.db"

print("=== Tracker DB ===")
if os.path.exists(db1):
    conn1 = sqlite3.connect(db1)
    cur1 = conn1.cursor()
    try:
        cur1.execute("SELECT COUNT(*) FROM processed_files;")
        print(f"Archivos procesados: {cur1.fetchone()[0]}")
        cur1.execute("SELECT COUNT(*) FROM processed_files WHERE leads_found > 0;")
        print(f"Archivos con leads > 0: {cur1.fetchone()[0]}")
        cur1.execute("SELECT * FROM processed_files WHERE leads_found > 0 LIMIT 2;")
        print("Muestra de procesados con leads:")
        pprint.pprint(cur1.fetchall())
    except Exception as e:
        print(e)
else:
    print("No existe", db1)

print("\n=== Main CRM DB ===")
if os.path.exists(db2):
    conn2 = sqlite3.connect(db2)
    cur2 = conn2.cursor()
    try:
        cur2.execute("SELECT COUNT(*) FROM osint_leads;")
        print(f"Total leads (osint_leads): {cur2.fetchone()[0]}")
        cur2.execute("SELECT id, nombre_persona_empresa, rut, monto, motivo, fecha_documento, estado, creado_el FROM osint_leads ORDER BY id DESC LIMIT 3;")
        print("Últimos 3 leads agregados:")
        pprint.pprint(cur2.fetchall())
    except Exception as e:
        print(e)
else:
    print("No existe", db2)
