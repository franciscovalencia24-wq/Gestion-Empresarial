import sys, os
sys.path.insert(0, os.getcwd())
import sqlite3
from src.database.connection import engine, Base
from src.database.models import Prospect, ClientProfile

print("Executing Base.metadata.create_all(bind=engine)...")
Base.metadata.create_all(bind=engine)

# Also check sqlite3 table info for data/crm_database.db
db_file = "data/crm_database.db"
if os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(client_profiles)")
    cols = [r[1] for r in cur.fetchall()]
    print(f"Columns in client_profiles: {cols}")
    
    for c in ["nombres", "apellido_paterno", "apellido_materno"]:
        if c not in cols:
            print(f"Adding missing column {c} to client_profiles...")
            cur.execute(f"ALTER TABLE client_profiles ADD COLUMN {c} TEXT")
            
    conn.commit()
    conn.close()
    print("✅ Migration on data/crm_database.db finished cleanly!")
