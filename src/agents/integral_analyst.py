import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    genai.configure(api_key=api_key)

def generate_integral_opinion(ticker: str, tech_opinion: str, fund_opinion: str, market_consensus: str = "") -> str:
    if not api_key:
        return 'Clave API no configurada (falta GOOGLE_API_KEY en .env).'
        
    prompt = f"""
    Eres 'Altus AI', un analista financiero institucional altamente sofisticado. 
    Tienes a la vista el análisis Técnico, el Fundamental y el Consenso de Mercado para el activo {ticker}.
    
    TÉCNICO:
    {tech_opinion}
    
    FUNDAMENTAL:
    {fund_opinion}

    CONSENSO DE MERCADO:
    {market_consensus}
    
    Tu tarea es emitir un dictamen final. No debes copiar el consenso de mercado ciegamente, sino emitir una recomendación objetiva propia basada en la divergencia técnico-fundamental.

    IMPORTANTE: Tu respuesta DEBE ser un objeto JSON válido (sin formato markdown alrededor) con la siguiente estructura exacta:
    {{
      "conclusion": "Un ÚNICO párrafo de conclusión ejecutiva e integral de máximo 60 palabras, redactado en tercera persona, con lenguaje institucional y terminología avanzada (momentum, capitulación, ROE, value trap, divergencia).",
      "recomendacion": "COMPRAR, MANTENER o VENDER",
      "conviccion": "ALTA, MEDIA o BAJA",
      "justificacion": "Párrafo corto de 2 a 3 líneas explicando el motivo de esta recomendación basado en tu conclusión y no sólo en el consenso."
    }}
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        # Pedimos JSON
        response = model.generate_content(prompt, generation_config=genai.GenerationConfig(response_mime_type="application/json"))
        return response.text.strip()
    except Exception as e:
        return f'{{"conclusion": "Error al contactar a la IA: {str(e)}", "recomendacion": "N/A", "conviccion": "N/A", "justificacion": "Error en la IA"}}'
