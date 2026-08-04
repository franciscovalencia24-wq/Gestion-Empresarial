import pandas as pd
import sqlite3
import re
import uuid
import os

from src.core.config import DATABASE_URL
if DATABASE_URL.startswith("sqlite:///"):
    DB_PATH = DATABASE_URL.replace("sqlite:///", "")
else:
    DB_PATH = "data/processed/prospectos.db"
FILES = ["csvvalor.csv", "csvAccionDerecho.csv"]

def limpiar_rut(r):
    if pd.isna(r): return ""
    return re.sub(r'[^0-9kK\-]', '', str(r)).upper()

def procesar():
    if not os.path.exists(DB_PATH):
        print(f"❌ No encuentro la base de datos en {DB_PATH}")
        return

    print("🔗 Conectando a la base de datos...")
    conn = sqlite3.connect(DB_PATH)
    # ACTIVAR MODO ULTRA RÁPIDO
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=OFF;")
    
    print("⏳ Cargando base de datos actual a memoria para evitar duplicados...")
    try:
        existentes = pd.read_sql("SELECT rut, nombre FROM prospects", conn)
        ruts_set = set(existentes['rut'].dropna().unique())
        nombres_set = set(existentes['nombre'].str.lower().dropna().unique())
    except Exception as e:
        print(f"⚠️ Error leyendo existentes: {e}. Asumiendo base vacía.")
        ruts_set = set()
        nombres_set = set()

    for f_name in FILES:
        if not os.path.exists(f_name):
            print(f"⚠️ Archivo no encontrado en la carpeta raíz: {f_name}. Saltando...")
            continue
        
        print(f"📖 Leyendo {f_name} (esto puede tardar unos segundos)...")
        try:
            # Primero probamos con punto y coma, saltando líneas mal formateadas
            df = pd.read_csv(f_name, sep=';', encoding='latin-1', on_bad_lines='skip', low_memory=False)
            if len(df.columns) < 2: 
                # Si solo detectó 1 columna, probamos con coma
                df = pd.read_csv(f_name, sep=',', encoding='latin-1', on_bad_lines='skip', low_memory=False)
        except Exception as e1:
            try:
                # Fallback a UTF-8 si latin-1 falla
                df = pd.read_csv(f_name, sep=';', encoding='utf-8', on_bad_lines='skip', low_memory=False)
            except Exception as e2:
                print(f"❌ Error fatal leyendo {f_name}: {e1} / {e2}")
                continue

        # Estandarizar columnas a minúsculas
        df.columns = df.columns.astype(str).str.lower().str.strip().str.replace(' ', '_')
        
        # Mapeo de columnas según Infoprobidad
        col_rut = next((c for c in df.columns if 'rut' in c or 'sujeto' in c or 'identificacion' in c), None)
        col_nom = next((c for c in df.columns if 'nombre' in c or 'sujeto' in c or 'razon' in c), None)
        col_ape = next((c for c in df.columns if 'apellido' in c), None)
        col_mon = next((c for c in df.columns if 'monto' in c or 'valor' in c or 'patrimonio' in c), None)

        if not col_nom:
            print(f"❌ No encontré columna de nombre en {f_name}. Columnas detectadas: {list(df.columns)}")
            continue

        nuevos = []
        actualizados = 0
        
        print(f"⚙️ Procesando {len(df)} registros de {f_name}...")
        for i, row in df.iterrows():
            if i % 5000 == 0 and i > 0: print(f"   ... procesadas {i} filas")
            
            nombre = str(row[col_nom]).strip()
            if col_ape and pd.notna(row[col_ape]):
                nombre += " " + str(row[col_ape]).strip()
            nombre = nombre.title()
            
            if not nombre or nombre.lower() in ['nan', 'none', '']: continue
            
            rut = limpiar_rut(row[col_rut]) if col_rut else ""
            
            # Lógica de identificación
            if len(rut) < 7:
                # Si no hay RUT, chequeamos por nombre para no duplicar
                if nombre.lower() in nombres_set: 
                    actualizados += 1
                    continue
                rut = f"SINRUT-{str(uuid.uuid4())[:6].upper()}"
            
            if rut in ruts_set:
                actualizados += 1
                continue
            
            monto = 0
            if col_mon and pd.notna(row[col_mon]):
                try: 
                    monto_raw = str(row[col_mon])
                    monto = float(re.sub(r'[^0-9]', '', monto_raw))
                except: 
                    pass

            nuevos.append((rut, nombre, monto, f"Ingesta Directa ({f_name})", "Pendiente"))
            ruts_set.add(rut)
            nombres_set.add(nombre.lower())

        if nuevos:
            print(f"🚀 Inyectando {len(nuevos)} prospectos nuevos a la base de datos...")
            try:
                conn.executemany("""
                    INSERT INTO prospects (rut, nombre, monto_suscrito, origen_info, status_contacto)
                    VALUES (?, ?, ?, ?, ?)
                """, nuevos)
                conn.commit()
                print(f"✅ ÉXITO: {f_name} integrado. ({len(nuevos)} nuevos, {actualizados} ya existían/duplicados)")
            except Exception as e:
                print(f"❌ Error inyectando a BD: {e}")
        else:
            print(f"ℹ️ No se encontraron registros nuevos en {f_name}.")

    conn.close()
    print("\n🎉 ¡PROCESO DE ALTA VELOCIDAD TERMINADO!")
    print("Ya puedes volver a 'app.py' y verás todos tus prospectos nuevos en el embudo.")

if __name__ == "__main__":
    procesar()
