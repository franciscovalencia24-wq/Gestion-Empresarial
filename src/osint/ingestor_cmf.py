import sys
import os
import glob
import pandas as pd
from sqlalchemy import text

# CONFIGURACION DE RUTAS
base_path = os.path.abspath(os.curdir)
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from src.database.connection import engine

# Rutas de las carpetas locales de inyeccion
PATH_COSTOS = os.path.join(base_path, "data", "cmf", "costos")
PATH_RENTABILIDAD = os.path.join(base_path, "data", "cmf", "rentabilidad")

def procesar_excel_costos():
    """Lee todos los Excels que hayas guardado en data/cmf/costos y extrae la TAC"""
    archivos = glob.glob(os.path.join(PATH_COSTOS, "*.xls*"))
    
    if not archivos:
        print(f"No hay archivos Excel en 'data/cmf/costos'.")
        print("  Ve a la CMF y guarda ahí los archivos de Costos.")
        return

    print(f"Iniciando procesamiento de {len(archivos)} archivo(s) de Costos...")
    
    with engine.connect() as con:
        # Aseguramos que la tabla existe con el esquema hiper moderno
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS fondos_mutuos (
                nemotecnico VARCHAR(150) PRIMARY KEY,
                administradora VARCHAR(100),
                nombre_fondo VARCHAR(150),
                tipo_fondo VARCHAR(100),
                moneda VARCHAR(20),
                regimen_tributario VARCHAR(50),
                serie VARCHAR(15),
                tac_anual FLOAT,
                rentabilidad_1a FLOAT,
                ultima_actualizacion DATE DEFAULT CURRENT_DATE
            )
        """))
        con.commit()

        for archivo in archivos:
            nombre_archivo = os.path.basename(archivo)
            print(f"Extrayendo columnas desde: {nombre_archivo}...")
            
            try:
                # Leer el Excel. Ignoramos las primeras 3 filas que la CMF usa para títulos feos
                # Usamos los índices alfabéticos precisos de la CMF según tu captura de pantalla:
                # Col B (1): Administradora, Col C (2): Nombre Fondo, Col D (3): Tipo,
                # Col E (4): Moneda, Col F (5): Serie, Col G (6): Caracteristica, Col N (13): TAC Total
                
                if archivo.endswith('.xlsx'):
                    df = pd.read_excel(archivo, skiprows=4, usecols=[1, 2, 3, 4, 5, 6, 13], engine='openpyxl')
                else: # para .xls que usa la CMF
                    df = pd.read_excel(archivo, skiprows=4, usecols=[1, 2, 3, 4, 5, 6, 13], engine='xlrd')
                
                # Asignamos nombres fáciles de usar a esas 7 columnas
                df.columns = ["admin", "nombre", "tipo", "moneda", "serie", "caract", "tac"]
                
                # Limpieza de datos (Quitar vacíos)
                df = df.dropna(subset=['admin', 'nombre', 'serie'])
                
                fondos_nuevos = 0
                fondos_actualizados = 0

                for _, fila in df.iterrows():
                    try:
                        admin = str(fila['admin']).strip()
                        nombre = str(fila['nombre']).strip()
                        serie = str(fila['serie']).strip()
                        tipo = str(fila['tipo']).strip()
                        moneda = str(fila['moneda']).strip()
                        
                        caract = str(fila['caract']).lower()
                        regimen = "APV (Previsional)" if "previsional" in caract else "General"
                        
                        # Si la TAC viene como "NA", "N/A" o espacio, la dejamos como 0 o NULL
                        tac_str = str(fila['tac']).replace('%', '').replace(',', '.').strip()
                        tac = float(tac_str) if tac_str.replace('.','',1).isdigit() else 0.0

                        # Como la CMF a veces no entrega un "Nemotecnico" universal simple, 
                        # Fabricamos nuestro propio código único (Ej: BICE_ACCIONES_A)
                        admin_corto = admin.replace("Administradora General de Fondos", "AGF").split()[0]
                        nem_limpio = f"{admin_corto}_{nombre.replace(' ', '')}_{serie}".upper()
                        
                        # Inyectar a la base de datos
                        res = con.execute(text("""
                            INSERT INTO fondos_mutuos (nemotecnico, administradora, nombre_fondo, tipo_fondo, moneda, regimen_tributario, serie, tac_anual, ultima_actualizacion)
                            VALUES (:nem, :adm, :nom, :tip, :mon, :reg, :ser, :tac, CURRENT_DATE)
                            ON CONFLICT (nemotecnico) DO UPDATE SET 
                                tac_anual = EXCLUDED.tac_anual,
                                ultima_actualizacion = CURRENT_DATE
                        """), {
                            "nem": nem_limpio, "adm": admin, "nom": nombre, "tip": tipo, 
                            "mon": moneda, "reg": regimen, "ser": serie, "tac": tac
                        })
                        
                        if res.rowcount == 1: # PostgreSQL a veces cuenta distinto, pero esto es ilustrativo
                            fondos_nuevos += 1
                        
                    except Exception as e:
                        print(f"Saltando fila defectuosa: {e}")
                        continue
                
                con.commit()
                print(f"Archivo {nombre_archivo} inyectado. Filas procesadas: {len(df)}")
                
            except Exception as e:
                print(f"Error catastrofico leyendo el Excel {nombre_archivo}: {e}")

if __name__ == "__main__":
    procesar_excel_costos()
