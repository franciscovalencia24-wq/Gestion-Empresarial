import asyncio
from playwright.async_api import async_playwright
import os
import sys

async def capture_html(input_html="assets/anuncio_revista_altus.html", output_png="assets/anuncio_revista_altus.png"):
    file_path = os.path.abspath(input_html)
    file_uri = f"file:///{file_path.replace(chr(92), '/')}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(device_scale_factor=3) # Resolución 3x (8K)
        page = await context.new_page()
        # Set a standard presentation aspect ratio/resolution 16:9
        await page.set_viewport_size({"width": 2560, "height": 1440})
        await page.goto(file_uri)
        # Wait a bit for fonts/CSS to load
        await page.wait_for_timeout(1000)
        
        await page.screenshot(path=output_png)
        await context.close()
        await browser.close()
        print(f"Captura exitosa: {output_png}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        asyncio.run(capture_html(sys.argv[1], sys.argv[2]))
    else:
        asyncio.run(capture_html())
