import sqlite3
import pandas as pd

def audit_database():
    db_path = 'data/processed/prospectos.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtener nombres de tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Tablas encontradas: {tables}")
    
    if not tables:
        print("Base de datos vacía.")
        return

    # Usar la primera tabla para el reporte
    target_table = tables[0]
    print(f"--- ANALIZANDO TABLA: {target_table} ---")
    
    try:
        df_leads = pd.read_sql(f"SELECT * FROM {target_table}", conn)
        total = len(df_leads)
        con_telefono = df_leads[df_leads['telefono'].notnull() & (df_leads['telefono'] != '')].shape[0]
        con_email = df_leads[df_leads['email'].notnull() & (df_leads['email'] != '')].shape[0]
        con_ambos = df_leads[(df_leads['telefono'].notnull()) & (df_leads['email'].notnull()) & (df_leads['telefono'] != '') & (df_leads['email'] != '')].shape[0]
        
        print(f"Total Prospectos en Base: {total}")
        print(f"Prospectos Enriquecidos (Tel): {con_telefono} ({(con_telefono/total*100):.1f}%)")
        print(f"Prospectos Enriquecidos (Email): {con_email} ({(con_email/total*100):.1f}%)")
        print(f"Enriquecimiento Full (Tel + Email): {con_ambos} ({(con_ambos/total*100):.1f}%)")
        
    except Exception as e:
        print(f"Error al leer tabla: {e}")
    
    conn.close()

if __name__ == "__main__":
    audit_database()
