import sqlite3

def fix_db():
    db_path = 'data/processed/prospectos.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtener columnas actuales
    cursor.execute("PRAGMA table_info(prospects)")
    columns = [c[1] for c in cursor.fetchall()]
    
    print(f"Columnas actuales: {columns}")
    
    if 'crm_stage' not in columns:
        print("Añadiendo columna crm_stage...")
        cursor.execute("ALTER TABLE prospects ADD COLUMN crm_stage TEXT DEFAULT 'NUEVO'")
        
    if 'crm_notes' not in columns:
        print("Añadiendo columna crm_notes...")
        cursor.execute("ALTER TABLE prospects ADD COLUMN crm_notes TEXT")
        
    conn.commit()
    conn.close()
    print("Base de datos reparada correctamente.")

if __name__ == "__main__":
    fix_db()
