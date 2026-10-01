import os
import fitz  # PyMuPDF
import docx
import json
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict

from src.database.connection import SessionLocal
from src.database.models import OsintLead

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def extract_text_from_file(filepath: str) -> str:
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
        elif ext == 'doc':
            try:
                import win32com.client
                import pythoncom
                import os
                pythoncom.CoInitialize()
                abs_path = os.path.abspath(filepath)
                word = win32com.client.DispatchEx("Word.Application")
                word.Visible = False
                word.DisplayAlerts = False
                wdoc = word.Documents.Open(abs_path, ReadOnly=True, ConfirmConversions=False)
                text = wdoc.Content.Text
                wdoc.Close(False)
                word.Quit()
                pythoncom.CoUninitialize()
            except Exception as e_word:
                print(f"Win32com error: {e_word}")
    except Exception as e:
        print(f"Error extrayendo {filepath}: {e}")
    return text

def analyze_document_with_gemini(text: str) -> List[Dict]:
    if not text.strip():
        return []
    
    # We truncate to ~150k characters just to be safe
    text_to_analyze = text[:150000]
    
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
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content([system_instruction, text_to_analyze])
        
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        data = json.loads(raw_text)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
    except Exception as e:
        print(f"Error en Gemini API: {e}")
    
    return []

def process_folder(folder_path: str):
    db = SessionLocal()
    processed_count = 0
    leads_found = 0
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.pdf', '.docx', '.doc')):
                filepath = os.path.join(root, file)
                
                text = extract_text_from_file(filepath)
                if not text:
                    continue
                
                leads = analyze_document_with_gemini(text)
                    
                processed_count += 1
                
                inserted_this_file = 0
                for lead in leads:
                    nombre = str(lead.get('nombre', '')).strip()
                    if not nombre:
                        continue
                    
                    monto = 0.0
                    try:
                        monto = float(lead.get('monto_estimado', 0.0))
                    except:
                        pass
                    
                    # Prevent extreme duplicates (same exact file + name)
                    exists = db.query(OsintLead).filter_by(nombre_persona_empresa=nombre, archivo_origen=filepath).first()
                    if not exists:
                        nuevo_lead = OsintLead(
                            nombre_persona_empresa=lead.get('nombre', 'Desconocido'),
                            rut=lead.get('rut', ''),
                            monto=lead.get('monto_estimado', 0.0),
                            archivo_origen=filepath,
                            motivo=lead.get('motivo', ''),
                            nivel_certeza=lead.get('nivel_certeza', 'Media'),
                            fecha_documento=lead.get('fecha_doc', ''),
                            estado="Pendiente"
                        )
                        db.add(nuevo_lead)
                        leads_found += 1
                
                db.commit()
    
    db.close()
    return processed_count, leads_found
