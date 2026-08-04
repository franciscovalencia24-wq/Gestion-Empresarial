from src.database.connection import engine
from sqlalchemy import text

with engine.connect() as con:
    query = text("SELECT origen_info, COUNT(*) as total FROM prospects GROUP BY origen_info")
    results = con.execute(query).fetchall()
    
    print("-" * 50)
    print(f"{'Origen de Información':<40} | {'Total'}")
    print("-" * 50)
    for row in results:
        origen = str(row[0]) if row[0] else "Desconocido"
        print(f"{origen:<40} | {row[1]}")
    print("-" * 50)
    
    # Check total
    total = con.execute(text("SELECT COUNT(*) FROM prospects")).scalar()
    print(f"TOTAL GENERAL EN CRM: {total}")
    
    # Check for SINRUT
    sinrut = con.execute(text("SELECT COUNT(*) FROM prospects WHERE rut LIKE 'SINRUT%'")).scalar()
    print(f"Prospectos sin RUT identificado (SINRUT): {sinrut}")
    
    # Show last 5 imports
    print("\nÚLTIMOS 5 REGISTROS INSERTADOS:")
    last_records = con.execute(text("SELECT id, rut, nombre, origen_info FROM prospects ORDER BY id DESC LIMIT 5")).fetchall()
    for r in last_records:
        print(f"ID: {r[0]} | RUT: {r[1]} | Nombre: {r[2]} | Origen: {r[3]}")
