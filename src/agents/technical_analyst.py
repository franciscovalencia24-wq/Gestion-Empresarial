import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_technical_opinion(ticker: str, summary: dict) -> str:
    """
    Toma los indicadores técnicos generados y le pide a Gemini
    que actúe como un analista cuantitativo experto para emitir una opinión.
    """
    if not api_key:
        return "❌ La clave de API de Gemini no está configurada. No se puede generar la opinión de IA."
        
    if not summary or "precio_cierre" not in summary:
        return "No hay suficientes datos técnicos para generar una opinión."

    # Formatear los datos matemáticos
    datos_duros = f"""
    Instrumento: {ticker}
    Último Precio de Cierre: {summary.get('precio_cierre')}
    Tendencia Largo Plazo (vs SMA 200): {summary.get('tendencia_largo_plazo')}
    
    Osciladores de Momento:
    - RSI (14): {summary.get('rsi_14')}
    - MACD: {summary.get('macd')}
    - MACD Signal: {summary.get('macd_signal')}
    - MACD Histograma: {summary.get('macd_histogram')}
    
    Medias Móviles Simples:
    - SMA 20 (Corto Plazo): {summary.get('sma_20')}
    - SMA 50 (Mediano Plazo): {summary.get('sma_50')}
    - SMA 200 (Largo Plazo): {summary.get('sma_200')}
    
    Bandas de Bollinger (Volatilidad):
    - Banda Superior: {summary.get('bollinger_upper')}
    - Banda Inferior: {summary.get('bollinger_lower')}
    """

    prompt = f"""
    Eres 'Altus AI', un analista técnico financiero institucional altamente sofisticado y estricto. 
    Tu trabajo es emitir un reporte breve, contundente y fundado matemáticamente sobre el instrumento {ticker}, 
    basándote EXCLUSIVAMENTE en los siguientes datos calculados al cierre de hoy:
    
    {datos_duros}
    
    Instrucciones de Redacción (DEBES usar EXACTAMENTE esta estructura Markdown, sin títulos extra):
    
    ### 1. Resumen Ejecutivo
    (Breve párrafo inicial de 2-3 líneas resumiendo la situación técnica global).
    
    ### 2. Puntos Clave
    - **Tendencia General:** (Análisis de SMAs)
    - **Momentum (RSI):** (Interpretación de sobrecompra/sobreventa)
    - **Fuerza (MACD):** (Interpretación del cruce y fuerza)
    - **Volatilidad:** (Análisis de Bandas de Bollinger)
    
    ### 3. Conclusión Análisis Cuantitativo (Técnico)
    (Desarrolla en un párrafo de 3-4 líneas una conclusión sólida y fundamentada. Usa los datos observados para justificar si la postura es Alcista, Bajista o Neutral. Debe leerse como el dictamen profesional de un analista cuantitativo).
    
    Sé directo, no uses saludos introductorios ni títulos gigantes (#). Utiliza lenguaje técnico financiero en español.
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Hubo un error al contactar al motor de inteligencia artificial: {e}"
