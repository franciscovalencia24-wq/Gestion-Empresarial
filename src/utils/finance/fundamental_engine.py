import yfinance as yf
import pandas as pd

def get_fundamental_data(ticker_symbol: str) -> dict:
    """
    Extrae los datos fundamentales y las noticias recientes de Yahoo Finance.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # Info general (ratios, descripcion, sector)
        info = stock.info
        
        # Balance General (anual)
        balance_sheet = stock.balance_sheet
        # Estado de Resultados
        financials = stock.financials
        # Flujo de Caja
        cashflow = stock.cashflow
        
        # Noticias
        news = stock.news
        
        # Formatear la data relevante
        summary = {
            "sector": info.get("sector", "Desconocido"),
            "industry": info.get("industry", "Desconocida"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "forward_pe": info.get("forwardPE", "N/A"),
            "pb_ratio": info.get("priceToBook", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "debt_to_equity": info.get("debtToEquity", "N/A"),
            "profit_margin": info.get("profitMargins", "N/A"),
            "return_on_equity": info.get("returnOnEquity", "N/A"),
            "free_cashflow": info.get("freeCashflow", "N/A"),
            "target_mean_price": info.get("targetMeanPrice", "N/A"),
            "recommendation_key": info.get("recommendationKey", "N/A"),
            "currency": info.get("currency", "USD"),
            "revenue_growth": info.get("revenueGrowth", "N/A"),
            "earnings_growth": info.get("earningsGrowth", "N/A"),
            "number_of_analyst_opinions": info.get("numberOfAnalystOpinions", "N/A")
        }
        
        # Extraer consensos / upgrades
        upgrades = []
        try:
            up = stock.upgrades_downgrades
            if up is not None and not up.empty:
                # Diccionarios de traducción para términos financieros
                action_map = {
                    "Reit": "Reitera", "Maintains": "Mantiene", "Upgrades": "Sube calificación a", 
                    "Downgrades": "Baja calificación a", "Initiates": "Inicia cobertura con", "Resumes": "Retoma cobertura con"
                }
                grade_map = {
                    "Outperform": "Rendimiento Superior", "Equal-Weight": "Rendimiento Promedio", 
                    "Overweight": "Sobreponderar", "Underweight": "Subponderar",
                    "Buy": "Comprar", "Sell": "Vender", "Neutral": "Neutral", "Hold": "Mantener",
                    "Strong Buy": "Fuerte Compra", "Market Perform": "Rendimiento de Mercado",
                    "Sector Perform": "Rendimiento del Sector", "Underperform": "Rendimiento Inferior",
                    "Peer Perform": "Rendimiento Promedio"
                }
                
                # Tomar los ultimos 5
                last_up = up.head(5)
                for index, row in last_up.iterrows():
                    raw_action = row.get("Action", "")
                    raw_to_grade = row.get("ToGrade", "")
                    raw_from_grade = row.get("FromGrade", "")
                    
                    # Funciones auxiliares para traduccion case-insensitive
                    def translate_str(text, mapping):
                        if not text or not isinstance(text, str): return text
                        for k, v in mapping.items():
                            if k.lower() in text.lower():
                                return v
                        return text
                    
                    # Añadir atajos comunes (Yahoo a veces usa minúsculas y recortes)
                    action_map.update({"init": "Inicia cobertura con", "main": "Mantiene", "reit": "Reitera", "down": "Baja calificación a", "up": "Sube calificación a"})
                    
                    action_es = translate_str(raw_action, action_map)
                    to_grade_es = translate_str(raw_to_grade, grade_map)
                    from_grade_es = translate_str(raw_from_grade, grade_map)
                    
                    upgrades.append({
                        "date": str(index.date()) if hasattr(index, 'date') else str(index),
                        "firm": row.get("Firm", ""),
                        "to_grade": to_grade_es,
                        "from_grade": from_grade_es,
                        "action": action_es
                    })
        except Exception:
            pass
            
        summary["recent_analyst_actions"] = upgrades
        
        # Extraer las ultimas 5 noticias
        news_list = []
        if news:
            for item in news[:5]:
                news_list.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", "")
                })
                
        return {
            "success": True,
            "summary": summary,
            "news": news_list,
            "business_summary": info.get("longBusinessSummary", "No hay descripciÃ³n disponible.")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


