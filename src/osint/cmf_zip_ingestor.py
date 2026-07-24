import os
import sys
import zipfile
import pandas as pd
from datetime import datetime
from sqlalchemy import text

base_path = os.path.abspath(os.curdir)
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from src.database.connection import engine

class CMFZipIngestor:
    """
    Ingesta real de datos de Fondos Mutuos desde el archivo ZIP oficial de la CMF.
    Dado que la CMF tiene bloqueos (WAF) y URLs dinámicas para descargas automatizadas,
    este script asume que el archivo 'fm_valor_cuota.zip' se deposita en 'data/raw/'
    (lo cual puede hacerse manualmente cada lunes o mediante un scraper Selenium/Playwright futuro).
    """
    def __init__(self, zip_path="data/raw/fm_valor_cuota.zip"):
        self.zip_path = os.path.abspath(zip_path)
        self.extract_dir = os.path.abspath("data/processed/cmf_temp")

    def run_ingestion(self):
        print(f"[*] Buscando archivo ZIP de la CMF en: {self.zip_path}")
        
        if not os.path.exists(self.zip_path):
            return {"exito": False, "mensaje": f"No se encontró el archivo {self.zip_path}. Por favor descárgalo de la CMF y ponlo en esa ruta."}
            
        data_file = None
        if self.zip_path.endswith('.zip'):
            os.makedirs(self.extract_dir, exist_ok=True)
            try:
                print("[*] Descomprimiendo archivo...")
                with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.extract_dir)
                    
                extracted_files = os.listdir(self.extract_dir)
                for f in extracted_files:
                    if f.endswith('.txt') or f.endswith('.csv') or f.endswith('.xlsx') or f.endswith('.xls'):
                        data_file = os.path.join(self.extract_dir, f)
                        break
                        
                if not data_file:
                    return {"exito": False, "mensaje": "El ZIP no contenía ningún archivo de datos válido."}
            except Exception as e:
                return {"exito": False, "mensaje": f"Error descomprimiendo el ZIP: {str(e)}"}
        else:
            data_file = self.zip_path
            
        try:
            print(f"[*] Parseando archivo de datos: {data_file}")
            
            if data_file.endswith('.xlsx') or data_file.endswith('.xls'):
                # En los reportes de Excel de la CMF, la tabla real empieza típicamente en la fila 10
                df = pd.read_excel(data_file, skiprows=9)
            else:
                df = pd.read_csv(data_file, sep=';', encoding='latin1', low_memory=False)
            
            # Normalizar columnas
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Mapeo Inteligente de Columnas (Soporte para CSV y Excel CMF)
            # En el Excel, la columna de Nombre de Fondo suele venir sin título (Unnamed: 0)
            col_nombre = next((c for c in df.columns if 'nombre' in c or 'fondo' in c and 'tipo' not in c), None)
            if not col_nombre and 'unnamed: 0' in df.columns:
                col_nombre = 'unnamed: 0'
                
            col_nemotecnico = next((c for c in df.columns if 'nemo' in c or 'run' in c), None)
            col_valor = next((c for c in df.columns if 'valor' in c or 'cuota' in c), None)
            col_fecha = next((c for c in df.columns if 'fecha' in c), None)
            
            if not col_nombre or not col_valor:
                return {"exito": False, "mensaje": f"No se encontraron las columnas necesarias. Columnas detectadas: {list(df.columns)}"}
                
            df_clean = df[[col_nemotecnico, col_nombre, col_valor, col_fecha]].copy() if col_nemotecnico and col_fecha else df[[col_nombre, col_valor]].copy()
            if col_nemotecnico and col_nemotecnico not in df_clean.columns: df_clean[col_nemotecnico] = df[col_nemotecnico]
            
            df_clean.rename(columns={
                col_nemotecnico: 'nemotecnico',
                col_nombre: 'nombre_fondo',
                col_valor: 'valor_cuota',
                col_fecha: 'fecha_valor'
            }, inplace=True, errors='ignore')
            
            # Limpiar datos
            df_clean['valor_cuota'] = pd.to_numeric(df_clean['valor_cuota'].astype(str).str.replace(',', '.'), errors='coerce')
            df_clean.dropna(subset=['valor_cuota'], inplace=True)
            
            if 'fecha_valor' not in df_clean.columns:
                df_clean['fecha_valor'] = datetime.now().date()
            
            print(f"[*] Actualizando base de datos SQLite con {len(df_clean)} registros...")
            with engine.connect() as con:
                # Upsert masivo
                for _, row in df_clean.iterrows():
                    con.execute(text("""
                        INSERT INTO cmf_valores_cuota (nemotecnico, nombre_fondo, valor_cuota, fecha_valor)
                        VALUES (:nemo, :nombre, :valor, :fecha)
                        ON CONFLICT(nombre_fondo) DO UPDATE SET 
                            valor_cuota=excluded.valor_cuota,
                            fecha_valor=excluded.fecha_valor
                    """), {
                        "nemo": row.get('nemotecnico', ''),
                        "nombre": row['nombre_fondo'],
                        "valor": row['valor_cuota'],
                        "fecha": row['fecha_valor']
                    })
                con.commit()
                
            return {"exito": True, "mensaje": f"Sincronización masiva completada. {len(df_clean)} fondos actualizados."}
            
        except Exception as e:
            return {"exito": False, "mensaje": f"Error procesando el ZIP de la CMF: {str(e)}"}

if __name__ == "__main__":
    ingestor = CMFZipIngestor()
    print(ingestor.run_ingestion())
