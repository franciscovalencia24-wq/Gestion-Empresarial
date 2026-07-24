import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

class BCNScraper:
    """
    Agente Recolector Autónomo (Fase 0).
    Se conecta a la API pública de Ley Chile (Biblioteca del Congreso Nacional)
    para descargar los textos actualizados de las normativas tributarias.
    """
    def __init__(self):
        # API Pública de Ley Chile
        self.base_url = "http://www.leychile.cl/Consulta/obtxml"
        self.vault_path = "data/knowledge_base/tributaria/"
        
        if not os.path.exists(self.vault_path):
            os.makedirs(self.vault_path)
            
        # Catálogo Integral de Normas de Family Office
        self.target_laws = {
            "6366": "Codigo_Tributario_DL830",
            "6368": "Ley_sobre_Impuesto_a_la_Renta_DL824",
            "6369": "Ley_sobre_Impuesto_a_las_Ventas_y_Servicios_IVA_DL825",
            "28246": "Ley_16271_Herencias_Asignaciones_Donaciones",
            "29472": "Ley_18045_Mercado_de_Valores",
            "1058032": "Ley_20712_Unica_de_Fondos_LUF",
            "29473": "Ley_18046_Sociedades_Anonimas",
            "172986": "Codigo_Civil",
            "1128400": "Ley_21133_Honorarios_y_Prevision"
        }

    def fetch_and_save_law(self, id_norma: str, filename: str) -> bool:
        """
        Descarga el XML de la ley desde la API de BCN, extrae el texto y lo guarda.
        """
        params = {
            "opt": "7",
            "idNorma": id_norma
        }
        print(f"[*] Conectando a BCN Ley Chile API para Norma {id_norma}...")
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code != 200:
                print(f"[!] Error de conexión: HTTP {response.status_code}")
                return False
                
            # Parsear el XML
            root = ET.fromstring(response.content)
            
            # Extraer el texto puro (simplificado para el RAG)
            law_text = f"--- LEY CHILE: NORMA {id_norma} ---\n"
            law_text += f"Extraído el: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            
            # BCN XML tiene una estructura compleja, iteramos por todos los textos
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    text = elem.text.strip()
                    # Evitar tokens basura muy cortos
                    if len(text) > 20:
                        law_text += text + "\n\n"
            
            # Guardar en la bóveda
            filepath = os.path.join(self.vault_path, f"{filename}.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(law_text)
                
            print(f"[+] Ley guardada con éxito en: {filepath}")
            return True
            
        except Exception as e:
            print(f"[!] Fallo al extraer Norma {id_norma}: {str(e)}")
            return False

    def sync_tributary_library(self):
        """Descarga todo el catálogo de leyes tributarias objetivo."""
        success_count = 0
        for id_norma, filename in self.target_laws.items():
            if self.fetch_and_save_law(id_norma, filename):
                success_count += 1
                
        return success_count, len(self.target_laws)

if __name__ == "__main__":
    print("Iniciando Agente Recolector BCN...")
    scraper = BCNScraper()
    exitos, total = scraper.sync_tributary_library()
    print(f"Sincronización completa: {exitos}/{total} leyes tributarias descargadas a la bóveda.")
