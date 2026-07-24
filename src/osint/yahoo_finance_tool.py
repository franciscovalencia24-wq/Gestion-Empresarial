from langchain_core.tools import BaseTool
import yfinance as yf
from pydantic import BaseModel, Field
from typing import Optional, Type
import pandas as pd

class YahooFinanceInput(BaseModel):
    ticker: str = Field(description="El símbolo o ticker del fondo/acción en Yahoo Finance (ej. JPM, SPY, AAPL)")
    start_date: Optional[str] = Field(default=None, description="Fecha de inicio en formato YYYY-MM-DD. Opcional.")
    end_date: Optional[str] = Field(default=None, description="Fecha de fin en formato YYYY-MM-DD. Opcional.")

class YahooFinanceTool(BaseTool):
    name: str = "yahoo_finance_historical"
    description: str = "Útil para obtener el precio actual o histórico de fondos internacionales o acciones."
    args_schema: Type[BaseModel] = YahooFinanceInput

    def _run(self, ticker: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        try:
            if start_date and end_date:
                data = yf.download(ticker, start=start_date, end=end_date, progress=False)
                if data.empty:
                    return f"No se encontraron datos para el ticker {ticker} entre {start_date} y {end_date}."
                first_price = float(data['Adj Close'].iloc[0])
                last_price = float(data['Adj Close'].iloc[-1])
                rentabilidad = ((last_price - first_price) / first_price) * 100
                return (f"Datos históricos para {ticker}:\n"
                        f"- Precio inicio ({data.index[0].strftime('%Y-%m-%d')}): {first_price:.4f}\n"
                        f"- Precio fin ({data.index[-1].strftime('%Y-%m-%d')}): {last_price:.4f}\n"
                        f"- Rentabilidad: {rentabilidad:.2f}%\n")
            else:
                # Obtener el último precio de cierre disponible
                ticker_obj = yf.Ticker(ticker)
                data = ticker_obj.history(period="5d") # Traemos 5 días por si hay feriados/fines de semana
                if data.empty:
                    return f"No se encontraron datos recientes para el ticker {ticker}."
                last_price = float(data['Close'].iloc[-1])
                last_date = data.index[-1].strftime('%Y-%m-%d')
                return f"Último precio de cierre publicado para {ticker} ({last_date}): {last_price:.4f} USD"
        except Exception as e:
            return f"Error al consultar Yahoo Finance para {ticker}: {str(e)}"
