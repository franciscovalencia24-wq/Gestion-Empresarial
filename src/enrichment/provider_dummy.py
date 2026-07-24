import time
import random

class DummyRutEnricherProvider:
    """Simulador de API para la Fase 2 del proyecto."""
    def __init__(self, api_key=None):
        self.api_key = api_key
        
    def fetch_data_by_rut(self, rut: str) -> dict:
        time.sleep(random.uniform(0.5, 1.5))
        
        if random.random() < 0.2:
            return {"success": False, "error": "No encontrado"}
            
        nombres = ["Juan Perez", "Maria Gonzalez", "Pedro Silva", "Camila Tapia", "Andres Lillo", "Jorge Muñoz"]
        telefono = f"+569{random.randint(10000000, 99999999)}"
        
        return {
            "success": True,
            "data": {
                "rut": rut,
                "nombre": random.choice(nombres),
                "telefono": telefono,
                "ciudad": "Santiago",
                "email": f"{rut.split('-')[0]}@mail_dummy.com"
            }
        }
