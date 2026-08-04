import asyncio
from playwright.async_api import async_playwright
import os
import sys

async def capture_pdf(input_html, output_pdf):
    file_path = os.path.abspath(input_html)
    file_uri = f"file:///{file_path.replace(chr(92), '/')}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Set a standard presentation aspect ratio/resolution 16:9
        await page.set_viewport_size({"width": 2560, "height": 1440})
        await page.goto(file_uri)
        # Wait a bit for fonts/CSS to load
        await page.wait_for_timeout(1000)
        
        # Emular pantalla para que no aplique estilos de impresión
        await page.emulate_media(media="screen")
        
        # Save as PDF with exact dimensions (16:9)
        await page.pdf(
            path=output_pdf, 
            width="2560px", 
            height="1440px", 
            print_background=True, 
            page_ranges="1",
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
        )
        await browser.close()
        print(f"PDF generado con éxito: {output_pdf}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        asyncio.run(capture_pdf(sys.argv[1], sys.argv[2]))
    else:
        print("Generando anuncio_revista_altus_final.pdf...")
        asyncio.run(capture_pdf("assets/anuncio_revista_altus.html", "assets/anuncio_revista_altus_final.pdf"))
        print("Generando infografia_seguro_final.pdf...")
        asyncio.run(capture_pdf("assets/infografia_seguro.html", "assets/infografia_seguro_final.pdf"))
