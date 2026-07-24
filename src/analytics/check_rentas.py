import sys
import os
from sqlalchemy import text

# Path setup
base_path = os.path.abspath(os.curdir)
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from src.database.connection import engine

def auditar_principal():
    with engine.connect() as con:
        # Buscamos las series de Principal que mencionaste
        query = text("""
            SELECT nombre_fondo, serie, rentabilidad_1a, rentabilidad_3a, rentabilidad_5a 
            FROM fondos_mutuos 
            WHERE administradora LIKE '%PRINCIPAL%' 
            AND (serie = 'PAT' OR nombre_fondo LIKE '%GESTION ACTIVA%' OR nombre_fondo LIKE '%GLOBAL EQUITY%')
            ORDER BY nombre_fondo ASC
        """)
        res = con.execute(query).fetchall()
        
        print('\n' + '='*100)
        print(f'{"FONDO":<45} | {"SERIE":<8} | {"1A %":<8} | {"3A %":<8} | {"5A %":<8}')
        print('-'*100)
        for r in res:
            # Reemplazar None por "N/A"
            r1 = f"{r[2]:.2f}" if r[2] is not None else "N/D"
            r3 = f"{r[3]:.2f}" if r[3] is not None else "N/D"
            r5 = f"{r[4]:.2f}" if r[4] is not None else "N/D"
            print(f'{str(r[0])[:45]:<45} | {str(r[1]):<8} | {r1:<8} | {r3:<8} | {r5:<8}')
        print('='*100 + '\n')

if __name__ == '__main__':
    auditar_principal()
