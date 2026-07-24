import requests
from datetime import datetime

class CMFScraper:
    """
    Agente OSINT para Extracción de Mercado (FASE 1).
    Se conecta a la API de la Comisión para el Mercado Financiero (CMF).
    """
    def __init__(self, api_key: str = "19ad91bcf846d9f868008de700dde297238c9390"):
        self.api_key = api_key
        # Usamos el endpoint oficial de Indicadores Financieros de la CMF
        self.base_url = "https://api.cmfchile.cl/api-sbifv3/recursos_api/"

    def fetch_indicadores_hoy(self):
        """
        Extrae UF y Dólar del día directamente desde la CMF.
        """
        # La API de la CMF usa el formato /recursos_api/uf?apikey=...
        params = {"apikey": self.api_key, "formato": "json"}
        
        resultados = {}
        
        try:
            print("[*] Conectando a API CMF para extraer Dólar Observado...")
            r_dolar = requests.get(f"{self.base_url}dolar", params=params, timeout=10)
            if r_dolar.status_code == 200:
                data = r_dolar.json()
                dolares = data.get("Dolares", [])
                if dolares:
                    resultados['dolar'] = dolares[0].get("Valor")
            else:
                resultados['dolar'] = "Error Auth"

            print("[*] Conectando a API CMF para extraer UF...")
            r_uf = requests.get(f"{self.base_url}uf", params=params, timeout=10)
            if r_uf.status_code == 200:
                data = r_uf.json()
                ufs = data.get("UFs", [])
                if ufs:
                    resultados['uf'] = ufs[0].get("Valor")
            else:
                resultados['uf'] = "Error Auth"
                
            return {
                "exito": True if "Error Auth" not in [resultados.get('uf'), resultados.get('dolar')] else False,
                "datos": resultados,
                "mensaje": "Indicadores extraídos exitosamente de la CMF." if "Error" not in str(resultados) else "Falta configurar la API KEY de la CMF."
            }
        except Exception as e:
            return {"exito": False, "mensaje": f"Fallo de conexión CMF: {e}"}

if __name__ == "__main__":
    scraper = CMFScraper()
    print(scraper.fetch_indicadores_hoy())
