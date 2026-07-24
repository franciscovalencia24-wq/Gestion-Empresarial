import time
import random

class AntiBanManager:
    """
    Motor matemático que inyecta delays microscópicos y "esperas" grandes
    que emulan ser un humano real operando sobre el teclado y la plataforma.
    """
    def __init__(self, min_wait: int = 45, max_wait: int = 120):
        # Tiempo de espera (en segundos) que el robot tomará entre cliente C y cliente C+1
        self.min_wait = min_wait
        self.max_wait = max_wait
        
    def human_typing_delay(self):
        """Genera un retraso minúsculo milisegundo a milisegundo por cada iteración."""
        time.sleep(random.uniform(0.01, 0.08))
        
    def action_delay(self):
        """Retraso menor para tiempos de búsqueda, clicks y cargas de páginas de internet."""
        time.sleep(random.uniform(1.2, 3.8))

    def random_wait(self, prospect_count: int = 0):
        """
        Retraso fuerte (minutos) entre cada envío completo de mensaje.
        Módulo de cansancio humano: Aumenta sutilmente el retraso base 
        1% si enviamos 1, 10% si llevamos mucho tiempo (cansancio natural).
        """
        fatigue_multiplier = 1.0 + (min(prospect_count, 50) * 0.01)
        
        wait_time = random.uniform(self.min_wait, self.max_wait) * fatigue_multiplier
        
        print(f"  [ANTI-BAN] Simulando espera humana natural de {wait_time:.1f} segundos...")
        time.sleep(wait_time)
