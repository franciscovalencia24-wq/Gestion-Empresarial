import sqlite3
import glob

db_files = glob.glob('**/*.db', recursive=True)
print(f"Found DB files: {db_files}")

cols_to_add = [
    ('nombres', 'VARCHAR(150)'),
    ('apellido_paterno', 'VARCHAR(100)'),
    ('apellido_materno', 'VARCHAR(100)'),
    ('renta_anual_declarada', 'FLOAT DEFAULT 0.0'),
    ('tipo_persona', "VARCHAR(20) DEFAULT 'PN'"),
    ('audio_path', 'VARCHAR(500)'),
    ('fecha_constitucion', 'DATE'),
    ('notaria_constitucion', 'VARCHAR(200)'),
    ('repertorio_constitucion', 'VARCHAR(100)'),
    ('fecha_ultima_vigencia', 'DATE'),
    ('documentos_legales_path', 'VARCHAR(500)')
]

for f in db_files:
    try:
        conn = sqlite3.connect(f)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='client_profiles'")
        if cur.fetchone():
            for col_name, col_type in cols_to_add:
                try:
                    cur.execute(f"ALTER TABLE client_profiles ADD COLUMN {col_name} {col_type}")
                    print(f" Added column '{col_name}' to {f}")
                except Exception as e:
                    pass
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error checking {f}: {e}")
