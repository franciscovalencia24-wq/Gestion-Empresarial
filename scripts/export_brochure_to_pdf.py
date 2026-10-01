import asyncio
import os
import sys

# Asegurar que corre en Windows sin problemas de event loop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: Playwright no está instalado. Ejecuta: pip install playwright && playwright install chromium")
    sys.exit(1)

async def export_to_pdf():
    html_path = os.path.abspath("brochure_altus_core.html")
    pdf_path = os.path.abspath("Brochure_ALTUS_CORE_v6.pdf")
    
    if not os.path.exists(html_path):
        print(f"Error: No se encontró el archivo {html_path}")
        return

    print("Iniciando motor Chromium para exportar a PDF...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Cargar el archivo HTML local
            print("Renderizando HTML...")
            await page.goto(f"file:///{html_path}")
            
            # Esperar a que todo cargue (fuentes, etc)
            await page.wait_for_load_state("networkidle")
            
            # Opciones de exportación PDF (Sin headers ni footers molestos)
            print("Generando PDF de alta calidad...")
            await page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,           # Mantener colores oscuros
                display_header_footer=False,     # Eliminar fechas, urls y número de página
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
            )
            
            await browser.close()
            print(f"Brochure exportado a PDF impecablemente en: {pdf_path}")
            
    except Exception as e:
        print(f"Error al generar PDF: {e}")
        print("Si es un error de binarios de playwright, intenta ejecutar en la terminal: playwright install chromium")

if __name__ == "__main__":
    asyncio.run(export_to_pdf())
