import asyncio
from playwright.async_api import async_playwright
import os

async def png_to_pdf(png_filename, pdf_filename):
    png_path = os.path.abspath(f"assets/{png_filename}")
    pdf_path = os.path.abspath(f"assets/{pdf_filename}")
    
    # Creamos un HTML ultra básico que solo contiene la imagen PNG estirada al 100% de la pantalla.
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      @page {{ size: 2560px 1440px; margin: 0; }}
      body, html {{ margin: 0; padding: 0; width: 2560px; height: 1440px; overflow: hidden; background-color: #0F172A; }}
      img {{ width: 2560px; height: 1440px; display: block; object-fit: contain; margin: 0; padding: 0; }}
    </style>
    </head>
    <body>
      <img src="file:///{png_path.replace(chr(92), '/')}">
    </body>
    </html>
    """
    
    wrapper_path = os.path.abspath("assets/temp_wrapper.html")
    with open(wrapper_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    wrapper_uri = f"file:///{wrapper_path.replace(chr(92), '/')}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Forzamos viewport idéntico
        await page.set_viewport_size({"width": 2560, "height": 1440})
        await page.goto(wrapper_uri)
        # Esperar a que la imagen cargue
        await page.wait_for_timeout(1000)
        
        await page.emulate_media(media="screen")
        await page.pdf(
            path=pdf_path, 
            width="2560px", 
            height="1440px", 
            print_background=True, 
            page_ranges="1",
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
        )
        await browser.close()
        
    os.remove(wrapper_path)
    print(f"PDF perfecto generado: {pdf_filename}")

async def main():
    await png_to_pdf("anuncio_revista_altus.png", "anuncio_revista_altus_v2.pdf")
    await png_to_pdf("infografia_seguro.png", "infografia_seguro_v2.pdf")

if __name__ == "__main__":
    asyncio.run(main())
