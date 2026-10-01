import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "data", "crm_database.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE prospects ADD COLUMN direccion VARCHAR(200)")
    print("Column 'direccion' added successfully to 'prospects' table.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'direccion' already exists.")
    else:
        print(f"Error: {e}")

conn.commit()
conn.close()
