import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class CAMVSpider:
    def __init__(self, max_depth=2):
        self.base_url = "https://www.camvchile.cl"
        self.max_depth = max_depth
        self.visited_urls = set()
        self.pdf_links = set()
        self.save_dir = "data/knowledge/camv_pdfs"
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
        # Para evitar rechazos o WAF simples
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'text/html,application/xhtml+xml,application/xml'
        }

    def crawl(self, url, current_depth=0):
        if current_depth > self.max_depth:
            return
        if url in self.visited_urls:
            return
        
        # Solo navegar dentro del mismo dominio
        if not url.startswith(self.base_url):
            return

        self.visited_urls.add(url)
        print(f"[{current_depth}] Explorando: {url}")
        
        try:
            # verify=False porque CAMV suele tener problemas certificados de vez en cuando
            response = requests.get(url, headers=self.headers, verify=False, timeout=10)
            if response.status_code != 200:
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar links en la página
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)
                
                if full_url.lower().endswith('.pdf'):
                    self.pdf_links.add((full_url, a_tag.text.strip()))
                else:
                    self.crawl(full_url, current_depth + 1)
                    
            time.sleep(1) # Respetar el servidor
            
        except Exception as e:
            print(f"Error procesando {url}: {e}")

    def download_pdfs(self):
        print(f"\nSe encontraron {len(self.pdf_links)} posibles archivos PDF.")
        count = 0
        for pdf_url, link_text in self.pdf_links:
            # Generar un nombre de archivo seguro
            filename = os.path.basename(urlparse(pdf_url).path)
            if not filename.endswith('.pdf'): continue
            
            # Limpiar nombre
            safe_name = "".join([c for c in filename if c.isalnum() or c in ".-_"])
            filepath = os.path.join(self.save_dir, safe_name)
            
            if os.path.exists(filepath):
                print(f"[CACHE] Ya existe {safe_name}")
                continue
                
            print(f"Descargando -> {safe_name}")
            try:
                r = requests.get(pdf_url, headers=self.headers, verify=False, stream=True, timeout=20)
                if r.status_code == 200 and 'application/pdf' in r.headers.get('Content-Type', ''):
                    with open(filepath, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    count += 1
            except Exception as e:
                print(f"  Error: {e}")
                
        print(f"\nFinalizado. {count} PDFs nuevos descargados en {self.save_dir}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    spider = CAMVSpider(max_depth=1)
    # Start points comunes en webs académicas
    spider.crawl("https://www.camvchile.cl/")
    spider.crawl("https://www.camvchile.cl/acreditacion")
    spider.crawl("https://www.camvchile.cl/material-estudio")
    spider.download_pdfs()
