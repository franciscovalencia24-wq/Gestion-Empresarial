import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class CAMVScraper:
    """
    Agente Académico: Dedicado a extraer y estructurar todo el material de estudio,
    leyes y manuales del Comité de Acreditación (CAMV) para entrenar al Agente Asesor.
    """
    def __init__(self):
        self.base_url = "https://www.camvchile.cl/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml'
        }
        self.db_path = "data/raw/camv_knowledge/"
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)

    def extract_index(self):
        """Mapea todas las secciones de recursos y normativas de la web principal."""
        print(f"[*] Escaneando portal académico: {self.base_url}")
        try:
            r = requests.get(self.base_url, headers=self.headers, verify=False, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            knowledge_links = []
            # Busca todos los enlaces, pero la lógica fuerte estará en 
            # seguir enlaces que van hacia sub-páginas de "conocimiento"
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.text.strip().lower()
                
                if 'http' not in href:
                    href = self.base_url + href.lstrip('/')
                    
                # Filtros inteligentes
                keywords = ['acreditacion', 'norma', 'ley', 'circular', 'manual', 'estudio', 'examen']
                if any(kw in text for kw in keywords) or any(kw in href.lower() for kw in keywords):
                    knowledge_links.append({"titulo": a.text.strip(), "url": href})

            self._save_knowledge_index(knowledge_links)
            return len(knowledge_links)

        except Exception as e:
            print(f"[!] Error accediendo a CAMV: {e}")
            return 0

    def download_pdf(self, url, title):
        """Descarga un documento oficial para incorporarlo al cerebro del agente."""
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        filepath = os.path.join(self.db_path, f"{safe_title.replace(' ', '_')}.pdf")
        
        if os.path.exists(filepath):
            return filepath
            
        print(f"[*] Descargando material de estudio: {safe_title}")
        try:
            r = requests.get(url, headers=self.headers, stream=True, verify=False)
            if 'application/pdf' in r.headers.get('Content-Type', ''):
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                return filepath
        except Exception as e:
            print(f"[!] Error descargando PDF: {e}")
        return None

    def _save_knowledge_index(self, links):
        """Guarda un índice maestro de lo que el agente debe leer."""
        index_file = os.path.join(self.db_path, "index.json")
        data = {"last_updated": str(datetime.now()), "sources": links}
        with open(index_file, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings() # CAMV puede tener SSL antiguo
    scraper = CAMVScraper()
    enlaces_encontrados = scraper.extract_index()
    print(f"[*] El módulo académico mapeó {enlaces_encontrados} recursos clave.")
    
    print("\n--- NOTA ARQUITECTURA: CUARTO DE ESTUDIO DE LA IA ---")
    print("El siguiente paso será conectar esta carpeta 'data/raw/camv_knowledge/'")
    print("a un motor RAG (Retrieval-Augmented Generation) vectorial usando LlamaIndex")
    print("para que el Agente Asesor pueda resolver dudas de prospectos citando la ley exacta.")
