from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import os
import requests
import json
from datetime import datetime

class BCCInput(BaseModel):
    series_code: str = Field(description="El código de la serie en el Banco Central (Ej: F073.UFF.PRE.Z.D para UF, F073.TCO.PRE.Z.D para Dólar)")
    first_date: Optional[str] = Field(default=None, description="Fecha de inicio en formato YYYY-MM-DD. Opcional.")
    last_date: Optional[str] = Field(default=None, description="Fecha de fin en formato YYYY-MM-DD. Opcional.")

class BancoCentralTool(BaseTool):
    name: str = "banco_central_chile"
    description: str = "Obtiene indicadores económicos de Chile (UF, Dólar, TPM, Imacec, IPC) desde el Banco Central. Usa F073.UFF.PRE.Z.D para UF, F073.TCO.PRE.Z.D para Dólar."
    args_schema: Type[BaseModel] = BCCInput

    def _run(self, series_code: str, first_date: Optional[str] = None, last_date: Optional[str] = None) -> str:
        user = os.getenv("BCC_API_USER")
        password = os.getenv("BCC_API_PASS")
        
        if not user or not password:
            return "Error: Faltan credenciales del Banco Central (BCC_API_USER y BCC_API_PASS en .env)."
            
        # Si no se pasan fechas, buscamos los últimos 10 días automáticamente
        if not first_date or not last_date:
            from datetime import timedelta
            now = datetime.now()
            last_date = now.strftime('%Y-%m-%d')
            first_date = (now - timedelta(days=10)).strftime('%Y-%m-%d')
            
        url = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
        
        params = {
            "user": user,
            "pass": password,
            "function": "GetSeries",
            "timeseries": series_code,
            "firstdate": first_date,
            "lastdate": last_date
        }
        
        try:
            response = requests.get(url, params=params, verify=False, timeout=10)
            if response.status_code != 200:
                return f"Error HTTP del Banco Central: {response.status_code}"
                
            data = response.json()
            if data.get("Codigo") != 0:
                return f"Error de la API BCC: {data.get('Descripcion')}"
                
            series_data = data.get("Series", {})
            obs = series_data.get("Obs", [])
            valid_obs = [o for o in obs if o.get('statusCode') == 'OK' and o.get('value') != 'NaN']
            
            if not valid_obs:
                return f"No se encontraron datos para la serie {series_code} entre {first_date} y {last_date}."
                
            # Extraer primer y ultimo dato valido
            primer_dato = valid_obs[0]
            ultimo_dato = valid_obs[-1]
            
            return (f"Datos del Banco Central (Serie: {series_code}):\n"
                    f"- Primer registro en el periodo ({primer_dato['indexDateString']}): {primer_dato['value']}\n"
                    f"- Último registro en el periodo ({ultimo_dato['indexDateString']}): {ultimo_dato['value']}\n"
                    f"- Total de días con observaciones: {len(obs)}")
        except Exception as e:
            return f"Error al consultar el Banco Central: {str(e)}"
