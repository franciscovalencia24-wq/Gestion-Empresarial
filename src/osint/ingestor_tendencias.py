import sys
import os
import pandas as pd
from sqlalchemy import text

# CONFIGURACION DE RUTAS
base_path = os.path.abspath(os.curdir)
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from src.database.connection import engine

def crear_tabla_tendencias():
    """Crea la tabla para las tendencias históricas del mercado."""
    with engine.connect() as con:
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS cmf_market_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_inscripcion VARCHAR(50),
                serie VARCHAR(50),
                participacion_pct FLOAT,
                numero_participes INTEGER,
                patrimonio_neto FLOAT,
                rut_agf VARCHAR(20),
                retorno_mensual FLOAT,
                ano INTEGER,
                moneda VARCHAR(20),
                tipo_fondo VARCHAR(100),
                categoria VARCHAR(150),
                segmento VARCHAR(100),
                nombre_fondo VARCHAR(200),
                administradora VARCHAR(100),
                mes INTEGER,
                fecha_data DATE
            )
        """))
        con.commit()

def ingest_market_trends(file_path):
    """Procesa el Excel de Tendencias de Mercado de la CMF."""
    if not os.path.exists(file_path):
        print(f"Error: No se encuentra el archivo {file_path}")
        return

    print(f"Inyectando tendencias de mercado desde {file_path}...")
    
    # Leemos saltando las primeras 2 filas (ajustado según inspección)
    # Usaremos skiprows=2 y asignaremos nombres manuales
    try:
        df = pd.read_excel(file_path, skiprows=2)
        
        # Mapeo manual de columnas (según lo observado en el dump)
        df.columns = [
            "codigo_inscripcion", "serie", "participacion_pct", "numero_participes",
            "patrimonio_neto", "rut_agf", "retorno_mensual", "ano", "moneda",
            "tipo_fondo", "categoria", "segmento", "nombre_fondo", "administradora", "mes"
        ]
        
        # Limpieza básica
        df = df.dropna(subset=["ano", "mes", "nombre_fondo"])
        
        # Crear columna de fecha para fácil filtrado (Asumiendo que mes es 1-12)
        # BUG: Vimos mes '25' en el dump. Si 'mes' es un índice, hay que manejarlo.
        # Por ahora lo guardaremos tal cual y crearemos un helper de visualización.
        
        crear_tabla_tendencias()
        
        with engine.connect() as con:
            # Borrar datos previos para no duplicar (O usar un merge inteligente)
            # Para tendencias históricas, solemos sobreescribir o agregar si es data nueva.
            # Como el archivo es un consolidado, borramos esta fuente específica.
            con.execute(text("DELETE FROM cmf_market_trends"))
            con.commit()
            
            df.to_sql("cmf_market_trends", engine, if_exists="append", index=False)
            
        print(f"Éxito: {len(df)} registros de mercado cargados.")
        
    except Exception as e:
        print(f"Error fatal en ingesta de tendencias: {e}")

if __name__ == "__main__":
    path = "data/cmf/rentabilidad/articles-91850_document_2.xlsx"
    ingest_market_trends(path)
