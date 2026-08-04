import asyncio
from playwright.async_api import async_playwright
import os

async def capture_html():
    file_path = os.path.abspath("anuncio_revista_altus.html")
    file_uri = f"file:///{file_path.replace(chr(92), '/')}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Set a standard magazine aspect ratio/resolution
        await page.set_viewport_size({"width": 1200, "height": 1600})
        await page.goto(file_uri)
        # Wait a bit for fonts/CSS to load
        await page.wait_for_timeout(1000)
        
        await page.screenshot(path="anuncio_revista_altus.png", full_page=True)
        await browser.close()
        print("Captura exitosa: anuncio_revista_altus.png")

if __name__ == "__main__":
    asyncio.run(capture_html())
