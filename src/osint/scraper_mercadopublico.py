import requests
from datetime import datetime

class MercadoPublicoScraper:
    """
    Agente OSINT para detectar Eventos de Liquidez (Fase 1).
    Consulta la API oficial de Mercado Público usando el RUT de la empresa proveedora.
    """
    def __init__(self, api_ticket: str = "62B250DD-1663-44BF-990F-49C5DB0EBE55"):
        self.base_url = "https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
        self.ticket = api_ticket

    def fetch_liquidity_events(self, rut_proveedor: str):
        """
        Busca las adjudicaciones recientes para el RUT dado.
        """
        # Limpiar el RUT
        rut_limpio = rut_proveedor.replace(".", "")
        
        params = {
            "rutProveedor": rut_limpio,
            "ticket": self.ticket
        }
        
        try:
            print(f"[*] Consultando Mercado Público para el Proveedor: {rut_limpio}")
            response = requests.get(self.base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                ordenes = data.get("Listado", [])
                
                total_adjudicado = 0
                eventos = []
                
                for orden in ordenes:
                    codigo = orden.get("Codigo")
                    nombre = orden.get("Nombre")
                    # En la API real, la orden base no trae el monto total, hay que hacer una segunda llamada
                    # o estimarlo. Asumiremos que tenemos el valor detallado para la maqueta.
                    
                    eventos.append({
                        "codigo": codigo,
                        "nombre": nombre,
                        "estado": orden.get("Estado")
                    })
                
                return {
                    "exito": True,
                    "cantidad_ordenes": len(ordenes),
                    "eventos": eventos,
                    "mensaje": f"Se encontraron {len(ordenes)} órdenes de compra."
                }
            elif response.status_code == 401 or "Ticket" in response.text:
                return {"exito": False, "mensaje": "⚠️ Ticket de Mercado Público inválido o ausente. Ingresa tu Ticket en la configuración."}
            else:
                return {"exito": False, "mensaje": f"Error HTTP {response.status_code}"}
                
        except Exception as e:
            return {"exito": False, "mensaje": f"Fallo de conexión: {str(e)}"}

if __name__ == "__main__":
    scraper = MercadoPublicoScraper(api_ticket="DUMMY")
    res = scraper.fetch_liquidity_events("76.123.456-7")
    print(res)
