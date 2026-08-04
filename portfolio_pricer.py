import yfinance as yf
import pandas as pd
import difflib
import os
import sys
from sqlalchemy import text

base_path = os.path.abspath(os.curdir)
if base_path not in sys.path:
    sys.path.insert(0, base_path)
from src.database.connection import engine

# Diccionario de mapeo heurístico: Nombre del producto en el Excel -> Ticker de Yahoo Finance
TICKER_MAP = {
    "RIPLEY": "RIPLEY.SN",
    "COLBUN": "COLBUN.SN",
    "ENJOY": "ENJOY.SN",
    "QUIÑENCO": "QUINENCO.SN",
    "LTM": "LTM.SN",
    "APORTE - USD - LTM": "LTM.SN"
}

def fetch_cmf_price_fuzzy(product_name):
    """
    Busca el precio en la BD local de la CMF usando Fuzzy Matching.
    """
    import re
    search_name = product_name
    if "SURA" in search_name.upper() and "APV" in search_name.upper():
        search_name = re.sub(r'(?i)APV', 'H', search_name).strip()

    try:
        with engine.connect() as con:
            res = con.execute(text("SELECT nombre_fondo, valor_cuota, fecha_valor FROM cmf_valores_cuota"))
            fondos_cmf = {row[0]: {'precio': row[1], 'fecha': str(row[2]) if row[2] else 'Reciente'} for row in res}
            
            matches = difflib.get_close_matches(search_name, fondos_cmf.keys(), n=1, cutoff=0.6)
            if matches:
                return fondos_cmf[matches[0]]
            return None
    except Exception as e:
        print(f"CMF DB Error: {e}")
        return None

def fetch_market_prices(unique_products):
    prices = {}
    for product in unique_products:
        if not isinstance(product, str):
            continue
            
        ticker_symbol = None
        for key, symbol in TICKER_MAP.items():
            if key.lower() in product.lower():
                ticker_symbol = symbol
                break
                
        if ticker_symbol:
            try:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    prices[product] = {'precio': round(hist['Close'].iloc[-1], 2), 'fecha': hist.index[-1].strftime('%Y-%m-%d')}
                else:
                    info = ticker.info
                    val = info.get('regularMarketPrice') or info.get('previousClose')
                    if val:
                        prices[product] = {'precio': round(val, 2), 'fecha': 'Reciente'}
                    else:
                        prices[product] = None
            except Exception as e:
                print(f"Error fetching {ticker_symbol}: {e}")
                prices[product] = None
        else:
            prices[product] = None
            
        if prices[product] is None:
            cmf_data = fetch_cmf_price_fuzzy(product)
            if cmf_data is not None:
                prices[product] = {'precio': round(cmf_data['precio'], 4), 'fecha': cmf_data['fecha']}
            
    return prices

if __name__ == "__main__":
    # Prueba rápida
    test_products = ["COLBUN", "SURA SELECCIÓN GLOBAL", "APORTE - USD - LTM ($6,8326)"]
    print(fetch_market_prices(test_products))
