import os
import subprocess
import sqlite3

versions = [
    "1787001669734114",
    "1787002082835382",
    "1787002105177916",
    "1787002842889829",
    "1787002895408097",
    "1787002962360202"
]

print("Analizando versiones más antiguas en GCS...")

for i, v in enumerate(versions, 6):
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
