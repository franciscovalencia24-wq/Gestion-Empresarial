import sys
import os
import re
from playwright.sync_api import sync_playwright

def diagnosticar_busqueda(nombre):
    print(f"--- DIAGNÓSTICO PARA: {nombre} ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # Lo ponemos visible para ver qué pasa
        page = browser.new_page()
        try:
            url = f"https://www.infoprobidad.cl/Busqueda/Index?termino={nombre.replace(' ', '%20')}"
            print(f"Navegando a: {url}")
            page.goto(url, timeout=15000)
            page.wait_for_timeout(3000)
            
            # Capturar captura de pantalla para el log interno (simulado)
            content = page.content()
            print("¿Hay resultados? ", "SÍ" if "card-body" in content else "NO")
            
            # Ver enlaces encontrados
            links = page.locator("a").all()
            print(f"Enlaces totales encontrados: {len(links)}")
            for link in links[:10]:
                href = link.get_attribute("href")
                if href and "/Declaracion/Index/" in href:
                    print(f"¡POTENCIAL RUT ENCONTRADO EN LINK!: {href}")
            
            browser.close()
        except Exception as e:
            print(f"ERROR: {e}")
            browser.close()

if __name__ == "__main__":
    # Probamos con el nombre que vimos antes
    diagnosticar_busqueda("Guillermo Leon Teillier Del Valle")
