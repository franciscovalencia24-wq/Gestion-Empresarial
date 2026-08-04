import sqlite3
import glob

db_files = glob.glob('**/*.db', recursive=True)
for f in db_files:
    try:
        conn = sqlite3.connect(f)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cur.fetchall()]
        for t in tables:
            if 'prospect' in t:
                cur.execute(f"SELECT COUNT(*) FROM {t} WHERE rut LIKE '%6298500%' OR nombre LIKE '%Moraga%'")
                cnt = cur.fetchone()[0]
                if cnt > 0:
                    print(f"FOUND {cnt} records in DB '{f}' -> table '{t}'")
        conn.close()
    except Exception as e:
        pass
