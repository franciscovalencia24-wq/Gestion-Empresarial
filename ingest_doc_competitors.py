import docx
import json
import os
import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.connection import SessionLocal
from src.database.models import CompetitorProfile
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])

def run_ingestion():
    print("Leyendo documento...")
    texto = extract_text_from_docx("Investigación Competencia Family Office Chile.docx")
    
    print("Invocando a Gemini para extracción estructurada...")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
    
    prompt = f"""
    Eres un analista de inteligencia de la información. Acabas de recibir un mega documento de investigación sobre el mercado de Wealth Management y Family Offices en Chile.
    Extrae un análisis exhaustivo para CADA competidor o actor mencionado en el documento (ej: SURA, Banchile, Santander, Altis, Fynsa, Quest Capital, VICAPITAL, AT Legacy Partners, Capital Advisors, Fintual, Betterplan, SoyFocus, Racional, etc.).
    
    Responde ÚNICAMENTE con un JSON Array válido, sin bloques markdown ```json, con esta estructura exacta para CADA competidor que encuentres:
    [
        {{
            "nombre": "Nombre de la institución",
            "tipo": "Megabanco | Boutique/MFO | WealthTech",
            "pros": "Fortalezas resumidas",
            "contras": "Debilidades (ej: retrocesiones, burocracia, mala atención)",
            "estrategias": "Estrategia que están usando actualmente",
            "publico_objetivo": "A qué tipo de cliente apuntan",
            "nichos_abandonados": "Oportunidad de ataque para nosotros"
        }}
    ]
    
    DOCUMENTO:
    {texto}
    """
    
    resp = llm.invoke(prompt)
    texto_json = resp.content
    if isinstance(texto_json, list):
        texto_json = texto_json[0].get('text', '') if isinstance(texto_json[0], dict) else str(texto_json)
    
    texto_json = str(texto_json).strip()
    if texto_json.startswith("```json"):
        texto_json = texto_json[7:]
    if texto_json.endswith("```"):
        texto_json = texto_json[:-3]
        
    try:
        competidores_data = json.loads(texto_json.strip())
    except Exception as e:
        print("Error parseando JSON:", e)
        print("Raw text:", texto_json[:500])
        return

    print(f"Se extrajeron {len(competidores_data)} competidores. Guardando en BD...")
    
    db = SessionLocal()
    for item in competidores_data:
        comp = db.query(CompetitorProfile).filter_by(nombre=item.get("nombre")).first()
        if not comp:
            comp = CompetitorProfile(nombre=item.get("nombre"), tipo=item.get("tipo", "Institución Financiera"))
            db.add(comp)
        else:
            comp.tipo = item.get("tipo", comp.tipo)
            
        comp.pros = item.get("pros", "")
        comp.contras = item.get("contras", "")
        comp.estrategias = item.get("estrategias", "")
        comp.publico_objetivo = item.get("publico_objetivo", "")
        comp.nichos_abandonados = item.get("nichos_abandonados", "")
        comp.updated_at = datetime.datetime.utcnow()
        
    db.commit()
    db.close()
    print("¡Ingesta de Matriz completada exitosamente!")

if __name__ == "__main__":
    run_ingestion()
