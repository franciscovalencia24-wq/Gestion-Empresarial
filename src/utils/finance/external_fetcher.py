import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime
import signal
import threading

logger = logging.getLogger(__name__)

original_signal = signal.signal

def mock_signal(signum, handler):
    if threading.current_thread() == threading.main_thread():
        return original_signal(signum, handler)
    else:
        return None

signal.signal = mock_signal

try:
    import mstarpy
except Exception as e:
    logger.error(f"Failed to import mstarpy: {e}")
    mstarpy = None

signal.signal = original_signal


# Diccionario de equivalencias para activos que no están en la CMF
# Nombre en el Excel -> Ticker en Yahoo Finance
ASSET_MAP = {
    "F. I. FALCOM TACTICAL CHILEAN EQUITIES": "CFIFALCTAC.SN",
    "LTM": "LTM.SN",
    "RIPLEY": "RIPLEY.SN",
    "COLBUN": "COLBUN.SN",
    "ENJOY": "ENJOY.SN",
    "QUIÑENCO": "QUINenco.SN",
    "CHILE": "CHILE.SN",
    "COPEC": "COPEC.SN",
    "FALABELLA": "FALABELLA.SN",
    "CMPC": "CMPC.SN",
    "SQM-B": "SQM-B.SN",
    "BSANTANDER": "BSANTANDER.SN",
    "CENCOSUD": "CENCOSUD.SN"
}

# Costo promedio administracion para acciones locales y etfs internacionales
DEFAULT_EQUITY_TAC = 0.5
DEFAULT_FI_TAC = 1.5

def get_yfinance_history(asset_name: str) -> dict:
    """
    Busca el historial en Yahoo Finance si el activo está en nuestro mapa.
    Calcula rentabilidad a 1, 3 y 5 años anualizada.
    """
    if asset_name not in ASSET_MAP:
        return None
        
    ticker_sym = ASSET_MAP[asset_name]
    try:
        tk = yf.Ticker(ticker_sym)
        # Traemos 5 años de historia (más un margen)
        hist = tk.history(period="6y")
        
        if hist.empty:
            logger.warning(f"Yahoo Finance no devolvió datos para {ticker_sym}")
            return None
            
        # Nos aseguramos de tener el índice ordenado
        hist.sort_index(inplace=True)
        
        current_price = hist['Close'].iloc[-1]
        current_date = hist.index[-1]
        
        returns = {}
        for years in [1, 3, 5]:
            # Buscamos el precio hace N años
            target_date = current_date - pd.DateOffset(years=years)
            
            # Si no hay historia suficiente para esos años
            if target_date < hist.index[0]:
                returns[f"{years}Y"] = np.nan
                continue
                
            # Encontramos la fecha más cercana al target date (buscando hacia atrás)
            idx_pos = hist.index.get_indexer([target_date], method='nearest')[0]
            past_price = hist['Close'].iloc[idx_pos]
            
            if pd.isna(past_price) or past_price == 0:
                returns[f"{years}Y"] = np.nan
            else:
                # Retorno acumulado
                cum_ret = (current_price / past_price) - 1
                # Anualizado: (1 + R)^(1/n) - 1
                ann_ret = (1 + cum_ret) ** (1/years) - 1
                returns[f"{years}Y"] = ann_ret * 100  # En porcentaje
                
        # Asignamos un TAC por defecto según el tipo
        tac = DEFAULT_FI_TAC if "F. I." in asset_name else DEFAULT_EQUITY_TAC
        
        return {
            "Rentabilidad_1Y": returns.get("1Y", np.nan),
            "Rentabilidad_3Y": returns.get("3Y", np.nan),
            "Rentabilidad_5Y": returns.get("5Y", np.nan),
            "TAC": tac,
            "Source": "Yahoo Finance"
        }
        
    except Exception as e:
        logger.error(f"Error procesando {asset_name} en yfinance: {e}")
        return None

def get_offshore_history(asset_name: str, regimen: str) -> dict:
    """
    Busca el historial de un fondo offshore usando mstarpy (Morningstar API).
    Específicamente diseñado para JP Morgan US Technology.
    """
    if "JP Morgan US Technology" not in asset_name:
        return None
        
    if mstarpy is None:
        logger.error("La librería mstarpy no está instalada.")
        return None
        
    # ISIN mappings para JP Morgan US Tech
    # Serie D (General): LU0117884678 (EUR, a veces referenciado, buscaremos LU0159052710 o genérico)
    # Serie A (APV): LU0210536198 (USD)
    
    isin = "LU0210536198" if "previsional" in regimen.lower() else "LU0159052710"
    
    try:
        fund = mstarpy.Funds(term=isin, language='es')
        # Usamos time_series para extraer 'nav'
        end_date = datetime.today()
        start_date = end_date - pd.DateOffset(years=6)
        
        ts = fund.TimeSeries(['nav'], start_date=start_date, end_date=end_date)
        
        if not ts or not isinstance(ts, list) or len(ts) == 0:
            return None
            
        nav_data = ts[0].get('nav', [])
        if not nav_data:
            return None
            
        df = pd.DataFrame(nav_data)
        # La API suele devolver {'date': 'YYYY-MM-DD', 'value': 123.4}
        if 'date' not in df.columns or 'value' not in df.columns:
            return None
            
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        
        current_nav = df['value'].iloc[-1]
        current_date = df.index[-1]
        
        returns = {}
        for years in [1, 3, 5]:
            target_date = current_date - pd.DateOffset(years=years)
            
            if target_date < df.index[0]:
                returns[f"{years}Y"] = np.nan
                continue
                
            idx_pos = df.index.get_indexer([target_date], method='nearest')[0]
            past_nav = df['value'].iloc[idx_pos]
            
            if pd.isna(past_nav) or past_nav == 0:
                returns[f"{years}Y"] = np.nan
            else:
                cum_ret = (current_nav / past_nav) - 1
                ann_ret = (1 + cum_ret) ** (1/years) - 1
                returns[f"{years}Y"] = ann_ret * 100
                
        # Extraer TAC desde Morningstar si es posible (feeLevel o info general)
        tac = 1.5 # Valor default razonable para fondos accionarios internacionales
        
        try:
            # feeLevel a veces trae OngoingCharge
            cost_info = fund.dataPoint(['ongoingCharge'])
            if cost_info and len(cost_info) > 0 and 'ongoingCharge' in cost_info[0]:
                val = cost_info[0]['ongoingCharge']
                if val:
                    tac = float(val)
        except:
            pass
            
        return {
            "Rentabilidad_1Y": returns.get("1Y", np.nan),
            "Rentabilidad_3Y": returns.get("3Y", np.nan),
            "Rentabilidad_5Y": returns.get("5Y", np.nan),
            "TAC": tac,
            "Source": "Morningstar"
        }
        
    except Exception as e:
        logger.error(f"Error conectando a Morningstar para {isin}: {e}")
        return None

def fetch_external_asset(asset_name: str, regimen: str = "") -> dict:
    """
    Orquestador principal. Intenta Yahoo Finance primero, si falla intenta Offshore.
    """
    if asset_name == "PERSHING":
        # Explícitamente ignoramos Pershing ya que es custodia, no un activo.
        return {
            "Rentabilidad_1Y": 0.0,
            "Rentabilidad_3Y": 0.0,
            "Rentabilidad_5Y": 0.0,
            "TAC": 0.0,
            "Source": "Custodia"
        }
        
    res_yf = get_yfinance_history(asset_name)
    if res_yf:
        return res_yf
        
    res_ms = get_offshore_history(asset_name, regimen)
    if res_ms:
        return res_ms
        
    return None
