import sqlite3
import glob

db_files = glob.glob('**/*.db', recursive=True) + glob.glob('**/*.sqlite', recursive=True) + glob.glob('**/*.bak', recursive=True)

for f in db_files:
    try:
        conn = sqlite3.connect(f)
        cur = conn.cursor()
        cur.execute("SELECT status_contacto FROM prospects WHERE nombre LIKE '%Patricio Oyanadel Tabilo%'")
        rows = cur.fetchall()
        if rows:
            print(f"File {f}: {rows}")
        conn.close()
    except Exception as e:
        pass
