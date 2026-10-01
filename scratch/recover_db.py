import os
import subprocess
import sqlite3

versions = [
    "1787246107628220",
    "1787247550259844",
    "1787248308175464",
    "1787248532729172",
    "1787248620769144" # Última (posiblemente corrupta)
]

print("Analizando las versiones en GCS...")
os.makedirs("data/recovery", exist_ok=True)

for i, v in enumerate(versions, 1):
    db_path = f"data/recovery/crm_database_v{i}.db"
    if not os.path.exists(db_path):
        cmd = f"gsutil cp gs://fv-asesorias-db-storage-fv/crm_database.db#{v} {db_path}"
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM company_financial_movements")
        count = c.fetchone()[0]
        conn.close()
        print(f"Versión {i} (Generation: {v}): {count} movimientos financieros registrados.")
    except Exception as e:
        print(f"Versión {i} (Generation: {v}): Error al leer DB - {e}")
