import os
from playwright.sync_api import sync_playwright

def save_page_as_pdf(url: str, output_path: str):
    print(f"Descargando {url} -> {output_path}...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            
            # Esperar un poco a que cargue
            page.wait_for_timeout(3000)
            
            # Guardar como PDF
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            page.pdf(path=output_path, format="A4", print_background=True)
            
            browser.close()
            print(f"Guardado con exito: {output_path}")
    except Exception as e:
        print(f"Error al descargar {url}: {e}")

if __name__ == "__main__":
    # URL Ley sobre Impuesto a la Renta (LIR) - BCN
    lir_url = "https://www.bcn.cl/leychile/navegar?idNorma=6368"
    lir_path = os.path.abspath(os.path.join("DOCUMENTACIÓN CMV", "CMV_LEYES", "LIR_Completa.pdf"))
    
    # URL Circular 21 SII (Normas sobre Tributación de Seguros de Vida y APV - aprox)
    circ21_url = "https://www.sii.cl/normativa_legislacion/circulares/2002/circ21.htm"
    circ21_path = os.path.abspath(os.path.join("DOCUMENTACIÓN CMV", "CIRCULARES", "Circular_21_SII.pdf"))
    
    save_page_as_pdf(lir_url, lir_path)
    save_page_as_pdf(circ21_url, circ21_path)
    
    print("\nDescargas finalizadas!")
