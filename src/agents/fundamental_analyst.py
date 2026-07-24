import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_fundamental_opinion(ticker: str, fund_data: dict) -> str:
    """
    Toma los datos fundamentales extraÃƒÂ­dos (ratios, balances, noticias) y le pide a Gemini
    que actÃƒÂºe como un analista fundamental experto.
    """
    if not api_key:
        return "Ã¢ÂÅ’ La clave de API de Gemini no estÃƒÂ¡ configurada. No se puede generar la opiniÃƒÂ³n de IA."
        
    if not fund_data or not fund_data.get("success"):
        return "No hay suficientes datos fundamentales para generar una opiniÃƒÂ³n."

    summary = fund_data.get("summary", {})
    news = fund_data.get("news", [])

    # Preparar el contexto numÃƒÂ©rico
    datos_duros = f"""
    Instrumento: {ticker}
    Sector: {summary.get('sector', 'Desconocido')}
    Industria: {summary.get('industry', 'Desconocida')}
    
    ValoraciÃƒÂ³n:
    - P/E Ratio (Trailing): {summary.get('pe_ratio')}
    - P/E Ratio (Forward): {summary.get('forward_pe')}
    - P/B Ratio: {summary.get('pb_ratio')}
    - Dividend Yield: {summary.get('dividend_yield')}
    
    Salud Financiera y Eficiencia:
    - Deuda a Capital (Debt/Equity): {summary.get('debt_to_equity')}
    - Margen de Beneficio: {summary.get('profit_margin')}
    - ROE (Return on Equity): {summary.get('return_on_equity')}
    
    Crecimiento:
    - Crecimiento de Ingresos: {summary.get('revenue_growth')}
    - Crecimiento de Ganancias: {summary.get('earnings_growth')}
    - Flujo de Caja Libre: {summary.get('free_cashflow')}
    
    Consenso e Institucionales:
    - Precio Objetivo a 12 meses: {summary.get('target_mean_price')}
    - RecomendaciÃ³n Institucional: {summary.get('recommendation_key')}
    """
    
    # Formatear las noticias
    noticias_texto = ""
    if news:
        for i, n in enumerate(news[:5]):
            noticias_texto += f"{i+1}. Titular: '{n['title']}' | Fuente: {n['publisher']} | Link: {n['link']}\n"
    else:
        noticias_texto = "No hay noticias recientes disponibles."

    prompt = f"""
    Eres 'Altus AI', un analista fundamental financiero institucional. 
    Tu trabajo es emitir un reporte breve, contundente y estructurado sobre el instrumento {ticker}, 
    basÃƒÂ¡ndote EXCLUSIVAMENTE en los siguientes datos contables y noticias:
    
    --- DATOS CONTABLES Y RATIOS ---
    {datos_duros}
    
    --- NOTICIAS RECIENTES ---
    {noticias_texto}
    
    Instrucciones de RedacciÃƒÂ³n (DEBES usar EXACTAMENTE esta estructura Markdown, sin tÃƒÂ­tulos extra):
    
    ### 1. Resumen Ejecutivo
    (Breve pÃƒÂ¡rrafo inicial de 2-3 lÃƒÂ­neas resumiendo la situaciÃƒÂ³n fundamental y corporativa).
    
    ### 2. Puntos Clave
    - **ValoraciÃƒÂ³n:** (EvaluaciÃƒÂ³n de P/E, P/B y dividendos)
    - **Salud Financiera:** (Nivel de deuda y mÃƒÂ¡rgenes operativos)
    - **Crecimiento y Caja:** (Flujo de caja libre y crecimiento de ingresos)
    - **Sentimiento Noticioso:** (IntegraciÃƒÂ³n de las noticias recientes)
    
    ### 3. Conclusión Análisis Corporativo (Fundamental)
    (Desarrolla en un párrafo de 3-4 líneas una conclusión sólida y fundamentada. Usa los datos observados para justificar la posición financiera general de la empresa y su atractivo de inversión. Debe leerse como el dictamen profesional de un analista fundamental).
    
    SÃƒÂ© directo, no uses saludos introductorios ni tÃƒÂ­tulos gigantes (#). Utiliza lenguaje tÃƒÂ©cnico financiero en espaÃƒÂ±ol.
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Ã¢Å¡Â Ã¯Â¸Â Hubo un error al contactar al motor de inteligencia artificial: {e}"


