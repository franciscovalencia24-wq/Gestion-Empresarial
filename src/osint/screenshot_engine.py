import os
from playwright.sync_api import sync_playwright
import uuid

def capture_full_page_screenshot(url: str) -> str:
    """
    Navega a una URL utilizando un navegador headless, toma un pantallazo de página completa
    y devuelve la ruta del archivo generado temporalmente.
    """
    temp_filename = f"temp_screenshot_{uuid.uuid4().hex}.png"
    temp_path = os.path.join(os.getcwd(), temp_filename)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Emular una pantalla grande para capturar todos los gráficos
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        try:
            # Esperar a que la red esté inactiva (networkidle) o forzar un tiempo de espera para que carguen los gráficos
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Scrollear suavemente hacia abajo para forzar la carga de elementos lazy-loaded (típico en JPM)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000) # Esperar 2 segundos tras scrollear
            
            # Tomar captura de página completa
            page.screenshot(path=temp_path, full_page=True)
        finally:
            browser.close()
            
    return temp_path
