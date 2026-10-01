import os
import sys
import time
import json
import sqlite3
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import fitz
import docx

# Agregar el directorio padre al path para importar módulos de src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from src.database.connection import SessionLocal
from src.database.models import OsintLead

def analyze_document_with_gemini_rest(text: str) -> list:
    if not text.strip():
        return []
    
    # --- FILTRO LOCAL ESTRICTO (Ahorro de Costos) ---
    text_lower = text[:15000].lower() 
    
    # Si el documento no pasó los filtros estrictos, lo descartamos
    import re
    action_pattern = re.compile(r"(herencia|posesi[oó]n efectiva|indemnizaci[oó]n|compraventa|liquidaci[oó]n|adjudicaci[oó]n|mutuo|repartici[oó]n|dividendos)", re.IGNORECASE)
    value_pattern = re.compile(r"(millones|uf |unidades de fomento|us\$|d[oó]lares|euros)", re.IGNORECASE)
    
    if not (action_pattern.search(text_lower) and value_pattern.search(text_lower)):
        return []
        
    # Tal como solicitaste, reducimos de 40.000 a solo 10.000 caracteres (aprox 3 páginas).
    # Hemos comprobado empíricamente que la comparecencia y el precio/cláusulas clave 
    # de las escrituras chilenas ocurren siempre en las primeras 3 a 4 planas.
    text_to_analyze = text[:10000]
    
    system_instruction = """
    Eres un analista experto de Family Office e Inteligencia Financiera. 
    Tu objetivo es leer este documento legal/notarial/judicial y detectar OPORTUNIDADES DE INVERSIÓN (LEADS).
    Busca personas naturales o empresas que ESTÉN RECIBIENDO o VAYAN A RECIBIR un flujo de liquidez importante.
    Ejemplos:
    - Vendedores en una compraventa de inmueble.
    - Herederos en una posesión efectiva o partición.
    - Demandantes que ganan indemnizaciones.
    - Socios recibiendo liquidaciones de empresas.
    
    Ignora a quienes pagan (compradores). Solo enfócate en quienes RECIBEN el dinero/patrimonio líquido.
    
    Devuelve un JSON estrictamente con la siguiente estructura (puede ser una lista si hay múltiples):
    [
      {
        "nombre": "Nombre Completo o Empresa",
        "rut": "RUT si aparece",
        "monto_estimado": 150000000, 
        "motivo": "Breve explicación de por qué recibe el dinero",
        "nivel_certeza": "Alta/Media/Baja",
        "fecha_doc": "Fecha del documento si aparece (YYYY-MM-DD)"
      }
    ]
    Si no hay nadie recibiendo flujos importantes, devuelve una lista vacía []. No devuelvas markdown, SOLO el JSON válido.
    """
    
    api_key = os.getenv("GOOGLE_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "parts": [{"text": text_to_analyze}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
    except requests.exceptions.Timeout:
        print("Gemini API Timeout. Skipping this chunk.")
        return []
    except Exception as e:
        print(f"Request error: {e}")
        return []
    
    if response.status_code == 429:
        raise Exception("429 Quota Exceeded")
    response.raise_for_status()
    
    data = response.json()
    try:
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        # Eliminar formato markdown si existe
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines)
            
        import json as json_lib
        leads = json_lib.loads(raw_text)
        if isinstance(leads, dict):
            leads = [leads]
        return leads
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return []

class WordExtractor:
    def __init__(self):
        import pythoncom
        pythoncom.CoInitialize()
        try:
            import win32com.client
            self.word = win32com.client.DispatchEx("Word.Application")
            self.word.Visible = False
            self.word.DisplayAlerts = 0
            self.word.AutomationSecurity = 3
        except Exception as e:
            print("No se pudo iniciar Word:", e)
            self.word = None

    def extract_text(self, filepath):
        if not self.word:
            return ""
            
        import os
        abs_path = os.path.abspath(filepath)
        try:
            wdoc = self.word.Documents.Open(
                abs_path, 
                ReadOnly=True, 
                ConfirmConversions=False,
                AddToRecentFiles=False,
                PasswordDocument="dummy_pass_1234"
            )
            text = wdoc.Content.Text
            wdoc.Close(False)
            return text
        except Exception as e:
            return ""

    def close(self):
        if self.word:
            try:
                self.word.Quit()
            except:
                pass

def init_tracker_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_files (
            filepath TEXT PRIMARY KEY,
            status TEXT,
            leads_found INTEGER,
            processed_at DATETIME
        )
    ''')
    conn.commit()
    return conn

def is_processed(cursor, filepath):
    cursor.execute('SELECT status FROM processed_files WHERE filepath = ?', (filepath,))
    return cursor.fetchone() is not None

def mark_processed(conn, cursor, filepath, status, leads_found):
    cursor.execute('''
        INSERT OR REPLACE INTO processed_files (filepath, status, leads_found, processed_at)
        VALUES (?, ?, ?, ?)
    ''', (filepath, status, leads_found, datetime.now().isoformat()))
    conn.commit()
    
# Soporte extra para PDF, DOCX, XLS, XLSX
def extract_other_file(filepath):
    ext = filepath.lower().split('.')[-1]
    text = ""
    try:
        if ext == 'pdf':
            doc = fitz.open(filepath)
            for page in doc:
                text += page.get_text()
            doc.close()
        elif ext == 'docx':
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext in ['xls', 'xlsx']:
            df = pd.read_excel(filepath)
            text = df.to_string()
    except Exception as e:
        pass # Fallo silencioso para seguir al próximo archivo
    return text

def main(folder_path, limit=None):
    tracker_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "osint_mass_tracker.db")
    os.makedirs(os.path.dirname(tracker_db_path), exist_ok=True)
    
    conn = init_tracker_db(tracker_db_path)
    cursor = conn.cursor()
    
    print(f"Scaneando carpeta para encontrar documentos en: {folder_path}")
    valid_exts = {'.doc', '.docx', '.pdf', '.xls', '.xlsx'}
    all_files = []
    
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_exts:
                # Omitir archivos temporales de Word y borradores
                f_lower = f.lower()
                if not f.startswith('~$') and "borrador" not in f_lower and "revision" not in f_lower and "revisión" not in f_lower:
                    all_files.append(os.path.join(root, f))
                
    print(f"Total de documentos encontrados (limpios): {len(all_files)}")
    
    # Filtrar los que ya fueron procesados
    pending_files = []
    for f in all_files:
        if not is_processed(cursor, f):
            pending_files.append(f)
            
    print(f"Documentos PENDIENTES por procesar: {len(pending_files)}")
    if limit:
        pending_files = pending_files[:limit]
        print(f"-> Limitando a {limit} archivos para esta prueba.\n")
        
    if not pending_files:
        print("¡No hay documentos nuevos que procesar!")
        return

    word_extractor = WordExtractor()
    db_crm = SessionLocal()
    
    try:
        if pending_files:
            print(f"\n[DEBUG] El primer archivo a procesar es: {pending_files[0]}\n")
        # --- COMPILAR FILTROS LOCALES ESTRICTOS (FAMILY OFFICE) ---
        import re
        action_pattern = re.compile(r"(herencia|posesi[oó]n efectiva|indemnizaci[oó]n|compraventa|liquidaci[oó]n|adjudicaci[oó]n|mutuo|repartici[oó]n|dividendos)", re.IGNORECASE)
        value_pattern = re.compile(r"(millones|uf |unidades de fomento|us\$|d[oó]lares|euros)", re.IGNORECASE)
        
        # Barra de progreso
        pbar = tqdm(pending_files, desc="Iniciando motor AI...")
        for i, filepath in enumerate(pbar):
            # Reiniciar WordExtractor cada 500 archivos para liberar RAM (Memory Leak fix)
            if i > 0 and i % 500 == 0:
                tqdm.write("\n[MANTENIMIENTO] Reiniciando MS Word para liberar memoria RAM...")
                word_extractor.close()
                word_extractor = WordExtractor()
                
            pbar.set_description(f"Doc: {os.path.basename(filepath)[:35]}")
            ext = filepath.lower().split('.')[-1]
            if ext == 'doc':
                text = word_extractor.extract_text(filepath)
            else:
                text = extract_other_file(filepath)
                
            if not text or len(text.strip()) < 10:
                mark_processed(conn, cursor, filepath, "EMPTY_TEXT", 0)
                continue
                
            # Filtro Estricto: Debe tener una acción patrimonial Y un indicador de alto valor.
            chunk = text[:15000]
            if not (action_pattern.search(chunk) and value_pattern.search(chunk)):
                mark_processed(conn, cursor, filepath, "SKIPPED_STRICT_FILTER", 0)
                continue
            # -----------------------------
                
            leads = []
            success = False
            retries = 0
            
            # Loop de reintentos para manejar el límite de velocidad (Rate Limit 429) de Google
            while not success and retries < 5:
                try:
                    leads = analyze_document_with_gemini_rest(text)
                    success = True
                except Exception as e:
                    err_str = str(e).lower()
                    if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                        wait_time = 15 * (2 ** retries)
                        tqdm.write(f"\n[GOOGLE LIMIT] Muy rápido. Esperando {wait_time}s antes de reintentar...")
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        tqdm.write(f"\n[ERROR GEMINI] {e} en archivo {os.path.basename(filepath)}")
                        break # Error no recuperable, saltar archivo
                        
            if not success:
                mark_processed(conn, cursor, filepath, "GEMINI_ERROR", 0)
                continue
                
            inserted = 0
            for lead in leads:
                nombre = str(lead.get('nombre', '')).strip()
                if not nombre:
                    continue
                
                # Checkear duplicados exactos en la Base de Datos
                exists = db_crm.query(OsintLead).filter_by(nombre_persona_empresa=nombre, archivo_origen=filepath).first()
                if not exists:
                    try:
                        monto_raw = lead.get('monto_estimado', 0.0)
                        if isinstance(monto_raw, str):
                            monto_raw = monto_raw.replace('.', '').replace(',', '.')
                        monto_final = float(monto_raw)
                    except:
                        monto_final = 0.0

                    nuevo_lead = OsintLead(
                        nombre_persona_empresa=lead.get('nombre', 'Desconocido'),
                        rut=lead.get('rut', ''),
                        monto=monto_final,
                        archivo_origen=filepath,
                        motivo=lead.get('motivo', ''),
                        nivel_certeza=lead.get('nivel_certeza', 'Media'),
                        fecha_documento=lead.get('fecha_doc', ''),
                        estado="Pendiente"
                    )
                    db_crm.add(nuevo_lead)
                    inserted += 1
                    
            if inserted > 0:
                db_crm.commit()
                
            mark_processed(conn, cursor, filepath, "SUCCESS", inserted)
            
    except KeyboardInterrupt:
        print("\n\n[PAUSA] PROCESO PAUSADO POR EL USUARIO. Todo el progreso ha sido guardado.")
        print("Puedes volver a ejecutar este script en cualquier momento y retomará desde aquí.")
    finally:
        word_extractor.close()
        db_crm.close()
        conn.close()
        print("\n[FIN] Proceso finalizado y recursos liberados.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='OSINT Mass Ingestion')
    parser.add_argument('--folder', type=str, help='Ruta de la carpeta a procesar')
    parser.add_argument('--limit', type=int, default=None, help='Límite de archivos para probar')
    args = parser.parse_args()
    
    folder_target = args.folder if args.folder else r"C:\Users\franc\OneDrive\Documentos\MALENTIN KARIME"
    
    if args.limit:
        print(f"Iniciando modo PRUEBA (solo {args.limit} archivos)...")
    else:
        print("Iniciando ejecución MASIVA...")
        
    main(folder_target, limit=args.limit)
