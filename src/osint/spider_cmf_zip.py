import os
import asyncio
import logging
from pathlib import Path
from typing import Tuple

from playwright.async_api import async_playwright, Playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
ZIP_FILENAME = "fm_valor_cuota.zip"
DOWNLOAD_URL = "https://www.cmfchile.cl/institucional/estadisticas/fm.bpr_menu.php"

async def _setup_browser(playwright: Playwright) -> Tuple[Browser, Page]:
    """Inicializa el navegador Chromium en modo headless y abre una nueva página.
    Configuramos la ruta de descargas para que el archivo se guarde directamente en data/raw.
    """
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(accept_downloads=True, downloads_path=str(DATA_RAW_DIR))
    page = await context.new_page()
    return browser, page

async def _navigate_and_download(page: Page) -> bool:
    """Navega por la interfaz de la CMF y dispara la descarga del ZIP.
    El flujo exacto está basado en la versión actual del sitio (febrero‑2026).
    Si la página cambia, lanzará una excepción que será capturada arriba.
    """
    try:
        logger.info("Visitando la página principal de descargas CMF")
        await page.goto(DOWNLOAD_URL, timeout=30000)
        # Asegurar que la página cargó (título esperado)
        await page.wait_for_selector("text=Valor Cuota", timeout=10000)
        # Seleccionar la fecha (el formulario suele tener un <select> name='fecha')
        # Elegimos la fecha de ayer (valor 'ayer')
        try:
            await page.select_option("select[name='fecha']", label="Ayer")
        except PlaywrightTimeoutError:
            # Si no hay selector, intentar con el botón de "Descargar" directamente
            pass
        # Hacer clic en el botón de descarga (el texto suele ser 'Descargar' o 'Exportar')
        download_button = await page.query_selector("button:has-text('Descargar')")
        if not download_button:
            download_button = await page.query_selector("a:has-text('Descargar')")
        if not download_button:
            raise Exception("No se encontró el botón de descarga en la página CMF")
        logger.info("Click en botón de descarga")
        async with page.expect_download(timeout=20000) as download_info:
            await download_button.click()
        download = await download_info.value
        # Guardar con nombre estándar
        download_path = Path(download.path())
        target_path = DATA_RAW_DIR / ZIP_FILENAME
        # Si ya existe, lo sobrescribimos
        if target_path.exists():
            target_path.unlink()
        download.save_as(str(target_path))
        logger.info(f"ZIP descargado y guardado en {target_path}")
        return True
    except Exception as e:
        logger.error(f"Error durante la descarga: {e}")
        return False

async def download_cmf_zip() -> Tuple[bool, str]:
    """Función pública que lanza el proceso completo.
    Devuelve (exito, mensaje).
    """
    try:
        async with async_playwright() as playwright:
            browser, page = await _setup_browser(playwright)
            success = await _navigate_and_download(page)
            await browser.close()
            if success:
                return True, f"Archivo ZIP descargado correctamente en {DATA_RAW_DIR / ZIP_FILENAME}"
            else:
                return False, "No se pudo descargar el ZIP: la página de la CMF pudo haber cambiado o el servidor está inaccesible."
    except Exception as e:
        return False, f"Excepción inesperada: {e}"

# Para pruebas rápidas desde la línea de comandos
if __name__ == "__main__":
    import sys
    asyncio.run(download_cmf_zip())
    sys.exit(0)
