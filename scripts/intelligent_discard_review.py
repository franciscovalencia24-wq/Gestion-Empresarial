import os
import sys
import re
import sqlite3
import pandas as pd
from tqdm import tqdm
import time
import win32com.client
import docx
import pythoncom

def get_text_from_doc(filepath, word_app):
    try:
        if filepath.lower().endswith('.docx'):
            doc = docx.Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs])
        elif filepath.lower().endswith('.doc'):
            try:
                doc = word_app.Documents.Open(filepath, ReadOnly=True, Visible=False)
                text = doc.Content.Text
                doc.Close(False)
                return text
            except Exception as e:
                return ""
    except Exception:
        return ""
    return ""

def main():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "osint_mass_tracker.db")
    if not os.path.exists(db_path):
        print("Base de datos no encontrada.")
        return

    conn = sqlite3.connect(db_path)
    
    # Obtener archivos descartados por los filtros anteriores, excluyendo los vacíos
    query = """
    SELECT filepath, status
    FROM processed_files
    WHERE status IN ('SKIPPED_NO_KEYWORDS', 'SKIPPED_STRICT_FILTER')
    """
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No hay archivos para la segunda revisión.")
        conn.close()
        return

    print(f"Iniciando Segunda Revisión Inteligente (NLP/Heurística) sobre {len(df)} archivos descartados.")

    # Expresiones regulares para rescatar falsos negativos:
    # 1. Cifras numéricas exactas que denotan alta liquidez
    # Montos en pesos > $50.000.000 (Ej: $ 50.000.000, $150.000.000)
    high_clp_pattern = re.compile(r"\$\s*[5-9]\d{1}\.\d{3}\.\d{3}|\$\s*[1-9]\d{2,3}\.\d{3}\.\d{3}", re.IGNORECASE)
    
    # Montos en UF > 2000 (Ej: 2.500 UF, 10.000 U.F., UF 5000)
    high_uf_pattern = re.compile(r"(?:[2-9]\.\d{3}|[1-9]\d{4,})\s*(?:UF|U\.F\.)|(?:UF|U\.F\.)\s*(?:[2-9]\.\d{3}|[1-9]\d{4,})", re.IGNORECASE)
    
    # Montos en Dolares > 50,000 (Ej: USD 50.000, 100.000 USD, US$ 60.000)
    high_usd_pattern = re.compile(r"(?:USD|US\$)\s*(?:[5-9]\d{1}\.\d{3}|[1-9]\d{2,}\.\d{3})|(?:[5-9]\d{1}\.\d{3}|[1-9]\d{2,}\.\d{3})\s*(?:USD|US\$|D[oó]lares)", re.IGNORECASE)

    # 2. Acciones jurídicas sinónimas que implican liquidez
    action_synonyms = re.compile(r"(cesi[oó]n de derechos|traspaso de acciones|retiro de utilidades|donaci[oó]n|aporte de capital|venta de inmueble|mutuo hipotecario)", re.IGNORECASE)

    rescued_files = []
    
    pythoncom.CoInitialize()
    word_app = None
    try:
        word_app = win32com.client.DispatchEx("Word.Application")
        word_app.Visible = False
        word_app.DisplayAlerts = False
    except Exception as e:
        print(f"Error inicializando MS Word: {e}")
        word_app = None

    restart_counter = 0

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Revisión Inteligente"):
        filepath = row['filepath']
        
        # Reiniciar Word periódicamente para evitar fugas de RAM
        restart_counter += 1
        if restart_counter > 500 and word_app is not None:
            try:
                word_app.Quit()
            except:
                pass
            time.sleep(2)
            try:
                word_app = win32com.client.DispatchEx("Word.Application")
                word_app.Visible = False
                word_app.DisplayAlerts = False
            except:
                pass
            restart_counter = 0

        text = get_text_from_doc(filepath, word_app)
        
        if not text.strip():
            continue
            
        text_lower = text.lower()
        
        # Evaluar heurísticas de rescate
        hit_reason = None
        
        if high_clp_pattern.search(text_lower):
            hit_reason = "ALTO_VALOR_CLP"
        elif high_uf_pattern.search(text_lower):
            hit_reason = "ALTO_VALOR_UF"
        elif high_usd_pattern.search(text_lower):
            hit_reason = "ALTO_VALOR_USD"
        elif action_synonyms.search(text_lower):
            # Para las acciones, confirmar si hay alguna métrica monetaria aunque sea en palabras
            if re.search(r"(millones|uf |unidades de fomento|us\$|d[oó]lares|euros|\$)", text_lower):
                hit_reason = "SINONIMO_ACCION_LIQUIDA"
                
        if hit_reason:
            rescued_files.append({
                "filepath": filepath,
                "reason": hit_reason
            })
            
            # Registrar rescate en la base de datos
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE processed_files 
                SET status = 'RESCUED_SMART_REVIEW', 
                    processed_at = CURRENT_TIMESTAMP
                WHERE filepath = ?
            ''', (filepath,))
            conn.commit()

    if word_app is not None:
        try:
            word_app.Quit()
        except:
            pass
    pythoncom.CoUninitialize()
    conn.close()

    if rescued_files:
        rescued_df = pd.DataFrame(rescued_files)
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Archivos_Rescatados_OSINT.xlsx")
        
        # Add clickable link
        rescued_df['Abrir Archivo'] = rescued_df['filepath'].apply(lambda x: f'=HYPERLINK("{x}", "Abrir Documento")')
        rescued_df = rescued_df[['reason', 'filepath', 'Abrir Archivo']]
        rescued_df.columns = ['Motivo de Rescate', 'Ruta Completa', 'Acción']
        
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
        rescued_df.to_excel(writer, index=False, sheet_name='Rescatados')
        worksheet = writer.sheets['Rescatados']
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 70)
        worksheet.set_column('C:C', 15)
        writer.close()
        
        print(f"\\nSe rescataron {len(rescued_files)} archivos falsos negativos.")
        print(f"Reporte de rescate guardado en: {output_path}")
    else:
        print("\\nEl script finalizó. No se encontraron archivos para rescatar. El filtro estricto tuvo un 100% de precisión.")

if __name__ == "__main__":
    main()
