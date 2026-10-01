import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://socich.cl/listado-de-socios/")
        await page.wait_for_load_state("networkidle")
        
        content = await page.content()
        with open("scratch/socich_page.html", "w", encoding="utf-8") as f:
            f.write(content)
            
        await browser.close()
        print("Page saved to scratch/socich_page.html")

if __name__ == "__main__":
    asyncio.run(run())
