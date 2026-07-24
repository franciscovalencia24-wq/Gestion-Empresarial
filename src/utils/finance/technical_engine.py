import yfinance as yf
import pandas as pd
import pandas_ta as ta

def get_historical_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Descarga los datos históricos de un ticker específico.
    Para la bolsa de Santiago, usar formato 'TICKER.SN' (ej: SQM-B.SN).
    """
    try:
        data = yf.download(tickers=ticker, period=period, interval=interval, progress=False)
        if data.empty:
            raise ValueError(f"No se encontraron datos para el ticker {ticker}")
            
        # yfinance devuelve a veces un multiindex en las columnas, lo aplanamos si es necesario
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
            
        return data
    except Exception as e:
        raise Exception(f"Error descargando datos para {ticker}: {e}")

def apply_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica indicadores de Análisis Técnico al DataFrame usando pandas-ta.
    Calcula: SMA, EMA, RSI, MACD, Bollinger Bands.
    """
    if df.empty or len(df) < 50:
        return df # No hay suficientes datos para calcular algunos indicadores

    try:
        # Asegurarse de que el índice es datetime (pandas-ta lo requiere)
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        # Usar la estrategia "All" de pandas-ta (calcula muchísimos)
        # O calcular manualmente los más importantes para no saturar:
        
        # Medias Móviles
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.sma(length=200, append=True)
        df.ta.ema(length=20, append=True)
        
        # Osciladores
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        
        # Volatilidad
        df.ta.bbands(length=20, std=2, append=True)
        df.ta.atr(length=14, append=True)

        return df
    except Exception as e:
        print(f"Error al calcular indicadores técnicos: {e}")
        return df

def generate_technical_summary(df: pd.DataFrame) -> dict:
    """
    Genera un resumen cuantitativo del último punto de datos 
    para ser entregado al Agente IA como "argumentos duros".
    """
    if df.empty:
        return {}
        
    last_row = df.iloc[-1]
    
    # Extraer los nombres de las columnas que pandas-ta generó por defecto
    cols = df.columns
    
    rsi_col = next((c for c in cols if 'RSI' in c), None)
    macd_col = next((c for c in cols if c.startswith('MACD_')), None)
    macds_col = next((c for c in cols if c.startswith('MACDs_')), None)
    macdh_col = next((c for c in cols if c.startswith('MACDh_')), None)
    sma20_col = next((c for c in cols if 'SMA_20' in c), None)
    sma50_col = next((c for c in cols if 'SMA_50' in c), None)
    sma200_col = next((c for c in cols if 'SMA_200' in c), None)
    bbl_col = next((c for c in cols if 'BBL_' in c), None) # Bandas Inferiores
    bbu_col = next((c for c in cols if 'BBU_' in c), None) # Bandas Superiores
    
    summary = {
        "precio_cierre": float(last_row['Close']) if 'Close' in last_row else None,
        "volumen": float(last_row['Volume']) if 'Volume' in last_row else None,
        "rsi_14": float(last_row[rsi_col]) if rsi_col and not pd.isna(last_row[rsi_col]) else None,
        "macd": float(last_row[macd_col]) if macd_col and not pd.isna(last_row[macd_col]) else None,
        "macd_signal": float(last_row[macds_col]) if macds_col and not pd.isna(last_row[macds_col]) else None,
        "macd_histogram": float(last_row[macdh_col]) if macdh_col and not pd.isna(last_row[macdh_col]) else None,
        "sma_20": float(last_row[sma20_col]) if sma20_col and not pd.isna(last_row[sma20_col]) else None,
        "sma_50": float(last_row[sma50_col]) if sma50_col and not pd.isna(last_row[sma50_col]) else None,
        "sma_200": float(last_row[sma200_col]) if sma200_col and not pd.isna(last_row[sma200_col]) else None,
        "bollinger_upper": float(last_row[bbu_col]) if bbu_col and not pd.isna(last_row[bbu_col]) else None,
        "bollinger_lower": float(last_row[bbl_col]) if bbl_col and not pd.isna(last_row[bbl_col]) else None,
    }
    
    # Tendencia básica
    if summary["precio_cierre"] and summary["sma_200"]:
        summary["tendencia_largo_plazo"] = "Alcista" if summary["precio_cierre"] > summary["sma_200"] else "Bajista"
    else:
        summary["tendencia_largo_plazo"] = "Indeterminada"
        
    return summary
