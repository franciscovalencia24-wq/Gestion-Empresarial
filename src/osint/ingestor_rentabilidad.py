import sys
import os
import pandas as pd
from sqlalchemy import text

# CONFIGURACION DE RUTAS
base_path = os.path.abspath(os.curdir)
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from src.database.connection import engine

def actualizar_rentabilidades():
    folder_path = "data/cmf/rentabilidad"
    archivos = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xlsx')]

    if not archivos:
        print("No se encontraron archivos de rentabilidad en data/cmf/rentabilidad.")
        return

    # Usamos el archivo mas reciente
    archivo = archivos[-1]
    print(f"Procesando: {archivo}")

    try:
        # El archivo tiene cabeceras en la fila 0
        df = pd.read_excel(archivo, engine='openpyxl')
        
        # Mapeo de columnas segun analisis previo
        # fm_serie -> serie
        # rent_nominal_1a -> rent_1a
        # rent_nominal_3a_ann -> rent_3a
        # rent_nominal_5a_ann -> rent_5a
        # familia_visualizador -> familia
        # nombre_fondo -> nombre
        # nombre_agf -> admin
        # fo_run -> run_fondo

        with engine.connect() as con:
            # Asegurar que todas las columnas de inteligencia existan
            cols = [
                ("run_fondo", "INTEGER"),
                ("rentabilidad_1a", "FLOAT"),
                ("rentabilidad_3a", "FLOAT"),
                ("rentabilidad_5a", "FLOAT"),
                ("rent_10a", "FLOAT"),
                ("familia_fondo", "VARCHAR(100)")
            ]
            for col_name, col_type in cols:
                try:
                    con.execute(text(f"ALTER TABLE fondos_mutuos ADD COLUMN {col_name} {col_type};"))
                except Exception: pass 
            
            con.commit()

            count = 0
            for _, fila in df.iterrows():
                # Limpieza de nombres para cruce
                admin = str(fila['nombre_agf']).strip().upper()
                nombre = str(fila['nombre_fondo']).strip().upper()
                serie = str(fila['fm_serie']).strip().upper()
                
                # Datos financieros
                run_f = fila['fo_run']
                r1 = float(fila['rent_nominal_1a']) if pd.notnull(fila['rent_nominal_1a']) else None
                r3 = float(fila['rent_nominal_3a_ann']) if pd.notnull(fila['rent_nominal_3a_ann']) else None
                r5 = float(fila['rent_nominal_5a_ann']) if pd.notnull(fila['rent_nominal_5a_ann']) else None
                r10 = float(fila['rent_nominal_10a_ann']) if pd.notnull(fila['rent_nominal_10a_ann']) else None
                familia = str(fila['familia_visualizador']).strip()

                # Actualizamos por matching de Nombre + Admin + Serie (que es lo que ya tenemos de Costos)
                # O por run_fondo si ya existe
                con.execute(text("""
                    UPDATE fondos_mutuos 
                    SET rentabilidad_1a = :r1, 
                        rentabilidad_3a = :r3, 
                        rentabilidad_5a = :r5,
                        rent_10a = :r10,
                        familia_fondo = :fam,
                        run_fondo = :run
                    WHERE UPPER(administradora) LIKE :adm 
                      AND UPPER(nombre_fondo) LIKE :nom
                      AND UPPER(serie) = :ser
                """), {
                    "r1": r1, "r3": r3, "r5": r5, "r10": r10, "fam": familia, "run": run_f,
                    "adm": f"%{admin}%", "nom": f"%{nombre}%", "ser": serie
                })
                count += 1
            
            con.commit()
            print(f"Actualización completada. Se procesaron {count} registros de rentabilidad.")

    except Exception as e:
        print(f"Error procesando rentabilidades: {e}")

if __name__ == "__main__":
    actualizar_rentabilidades()
