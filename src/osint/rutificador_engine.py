import time
import re
from playwright.sync_api import sync_playwright
from src.database.connection import engine
from sqlalchemy import text

def buscar_rut_por_nombre(nombre_completo):
    """
    Busca el RUT en InfoProbidad con tiempos de respuesta optimizados.
    """
    with sync_playwright() as p:
        # Modo sigilo para evitar bloqueos
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        try:
            # --- INTENTO 1: NOMBRE COMPLETO ---
            url_search = f"https://www.infoprobidad.cl/Busqueda/Index?termino={nombre_completo.replace(' ', '%20')}"
            page.goto(url_search, timeout=12000, wait_until="networkidle")
            
            # Selector más genérico para capturar cualquier enlace de declaración
            selector_resultado = "a[href*='/Declaracion/Index/']"
            
            if page.locator(selector_resultado).count() == 0:
                print(f"❌ Fallo inicial para: {nombre_completo}")
                # Captura rápida para ver qué ve el robot (se guarda en la carpeta del proyecto)
                # page.screenshot(path=f"debug_fallo_{int(time.time())}.png") 
                
                partes = nombre_completo.split()
                if len(partes) >= 2:
                    nombre_corto = f"{partes[0]} {partes[1]}"
                    print(f"🔄 Re-intentando con nombre corto: {nombre_corto}...")
                    url_search = f"https://www.infoprobidad.cl/Busqueda/Index?termino={nombre_corto.replace(' ', '%20')}"
                    page.goto(url_search, timeout=10000, wait_until="domcontentloaded")

            # Verificamos resultados final
            if page.locator(selector_resultado).count() > 0:
                enlace = page.locator(selector_resultado).first
                href = enlace.get_attribute("href")
                if href:
                    match = re.search(r'(\d{1,8}-[\dkK])', href)
                    if match:
                        rut = match.group(1).upper()
                        print(f"✅ ¡RUT ENCONTRADO!: {rut}")
                        browser.close()
                        return rut
            else:
                print(f"🚫 Definitivamente sin resultados para {nombre_completo}")
            
            browser.close()
            return None
            
        except Exception:
            if 'browser' in locals(): browser.close()
            return None

def iniciar_rutificador_masivo(status_ui=None, progress_bar=None):
    print("Iniciando Motor de Reconocimiento de Identidad...")
    
    with engine.connect() as con:
        query = text("SELECT id, nombre FROM prospects WHERE rut LIKE 'SINRUT%' LIMIT 50")
        pendientes = con.execute(query).fetchall()
        
        if not pendientes:
            if status_ui: status_ui.success("No hay prospectos pendientes.")
            return

        total = len(pendientes)
        exitos = 0
        
        for i, (id_prospecto, nombre) in enumerate(pendientes):
            msg = f"[{i+1}/{total}] Buscando identidad para: {nombre}..."
            if status_ui: status_ui.write(msg)
            print(msg)
            
            rut_encontrado = buscar_rut_por_nombre(nombre)
            
            if rut_encontrado:
                con.execute(text("UPDATE prospects SET rut = :r WHERE id = :id"), 
                            {"r": rut_encontrado, "id": id_prospecto})
                con.commit()
                exitos += 1
                if status_ui: status_ui.success(f"Encontrado: {nombre} -> {rut_encontrado}")
            
            if progress_bar:
                progress_bar.progress((i + 1) / total)
            
            time.sleep(1)
            
        if status_ui:
            status_ui.info(f"Finalizado. Se rescataron {exitos} identidades.")

if __name__ == "__main__":
    iniciar_rutificador_masivo()
