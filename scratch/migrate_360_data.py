import sqlite3
import glob

db_files = glob.glob('**/*.db', recursive=True)
print(f"Found DB files: {db_files}")

cols_to_add = {
    'client_profiles': [
        ('flujo_sucesorio', 'TEXT')
    ],
    'client_portfolios': [
        ('riesgo', 'VARCHAR(50)'),
        ('tir', 'FLOAT'),
        ('rentabilidad', 'FLOAT')
    ],
    'client_properties': [
        ('seguros', 'FLOAT DEFAULT 0.0'),
        ('cap_rate', 'FLOAT DEFAULT 0.0')
    ]
}

for f in db_files:
    try:
        conn = sqlite3.connect(f)
        cur = conn.cursor()
        
        for table_name, cols in cols_to_add.items():
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if cur.fetchone():
                for col_name, col_type in cols:
                    try:
                        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                        print(f" Added column '{col_name}' to table '{table_name}' in {f}")
                    except Exception as e:
                        # Silently ignore if column already exists
                        pass
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error checking {f}: {e}")

print("Migration complete.")
