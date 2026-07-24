import sys
import os

# CONFIGURACIÓN DE PATHS (Debe ir antes de importar src)
base_path = os.path.abspath(os.curdir)
if base_path not in sys.path:
    sys.path.insert(0, base_path)

import time
import re
import random
from dotenv import load_dotenv
from src.database.connection import engine
from sqlalchemy import text
from playwright.sync_api import sync_playwright

load_dotenv()

# ─── Credenciales TransUnion desde .env (NUNCA hardcodear en código) ─────────
TU_USUARIO = os.getenv("TRANSUNION_USER", "")
TU_PASSWORD = os.getenv("TRANSUNION_PASS", "")

def login_transunion(page):
    """Función de inicio de sesión — credenciales desde .env."""
    if not TU_USUARIO or not TU_PASSWORD:
        raise ValueError(
            "Credenciales TransUnion no configuradas. "
            "Define TRANSUNION_USER y TRANSUNION_PASS en tu archivo .env"
        )
    print(" Ingresando a TransUnion...")
    page.goto("https://www.transunionchile.cl/databusqueda/inicio.xhtml")
    page.wait_for_timeout(2000)
    
    user_field = page.locator("td:has-text('Nombre de Usuario:') + td input")
    if user_field.count() > 0 and user_field.is_visible():
        user_field.fill(TU_USUARIO)
        pass_field = page.locator("td:has-text('Contraseña:') + td input")
        pass_field.fill(TU_PASSWORD)
        page.keyboard.press("Enter")
        page.wait_for_timeout(5000)
    return True

def get_rut_corregido(rut_completo):
    """Toma un RUT y asegura que el cuerpo esté completo antes de calcular el DV."""
    import re
    limpio = str(rut_completo).strip().upper()
    
    # 1. Si tiene guion, el cuerpo es lo que está antes
    if '-' in limpio:
        cuerpo = re.sub(r'[^\d]', '', limpio.split('-')[0])
    else:
        # 2. Si NO tiene guion
        solo_alnum = re.sub(r'[^\dK]', '', limpio)
        # Sabiendo que filtramos RUTs > 50M, el cuerpo es siempre de 8 dígitos. 
        # Si tiene 9 caracteres en total, asumimos que el último es el DV.
        if len(solo_alnum) == 9:
            cuerpo = re.sub(r'[^\d]', '', solo_alnum[:-1])
        else:
            cuerpo = re.sub(r'[^\d]', '', solo_alnum)
            
    if not cuerpo or len(cuerpo) < 6: return None
    
    # Algoritmo Módulo 11 para Chile
    suma = 0
    multiplo = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1
    
    res = 11 - (suma % 11)
    dv = str(res)
    if res == 11: dv = "0"
    if res == 10: dv = "K"
    
    return f"{cuerpo}{dv}"

def extraer_telefonos_por_rut(page, batch_size=25):
    """Búsqueda de teléfonos con CAMUFLAJE PRO."""
    query = """
    SELECT id, rut FROM prospects 
    WHERE (rut IS NOT NULL AND rut != '' AND rut NOT LIKE 'SINRUT%') 
    AND (
        telefono IS NULL OR telefono = '' OR 
        fecha_nacimiento IS NULL OR 
        ultima_direccion IS NULL OR
        fallecido IS NULL
    )
    AND CAST(REPLACE(REPLACE(rut, '.', ''), '-', '') AS INTEGER) >= 50000000
    AND (telefono != 'RUT INVALIDO' AND telefono != 'SIN INFO' OR telefono IS NULL)
    ORDER BY id ASC
    LIMIT :limit
    """
    # Usamos un limite por sesion de 100 para evitar bloqueos
    batch_limit = 100
    if batch_size > batch_limit: batch_size = batch_limit
    
    with engine.connect() as conn:
        result = conn.execute(text(query), {"limit": batch_size})
        prospectos = result.fetchall()

    if not prospectos:
        print(" Todo completado.")
        return False # No hay más para procesar

    page.goto("https://www.transunionchile.cl/databusqueda/inicio.xhtml")
    
    counter = 0
    for p_id, rut_full in prospectos:
        counter += 1
        r = get_rut_corregido(rut_full)
        if not r or len(r) > 9:
            print(f"\n ({counter}/{len(prospectos)}) Saltando RUT inválido de origen: {rut_full}")
            with engine.connect() as con:
                con.execute(text("UPDATE prospects SET telefono = 'RUT INVALIDO' WHERE id = :id"), {"id": p_id})
                con.commit()
            continue
        
        print(f"\n ({counter}/{len(prospectos)}) Procesando: {r}...")
        
        try:
            # 1. Asegurar página y detectar errores de servidor
            if "Exception Occured" in page.content() or "inicio.xhtml" not in page.url:
                print(" Reset de página por error o desvío...")
                page.goto("https://www.transunionchile.cl/databusqueda/inicio.xhtml")
                page.wait_for_timeout(3000)

            # Abrir acordeón
            header = page.locator(".ui-accordion-header:has-text('BÚSQUEDA POR RUT')").first
            if "ui-state-active" not in (header.get_attribute("class") or ""):
                header.click()
                page.wait_for_timeout(800)

            frame = None
            for f in page.frames:
                if f.locator("input[id*='rut']").count() > 0:
                    frame = f; break
            
            if not frame: continue

            # Modo Individual (Lista de RUT: No)
            radio_no = frame.locator("td:has-text('Lista de RUT:') + td label:has-text('No')").first
            if radio_no.count() > 0: 
                radio_no.click()
                page.wait_for_timeout(800) # Más tiempo para el cambio de modo

            # Escribir RUT con velocidad variable
            campo = frame.locator("input[type='text']").first
            campo.click(click_count=3)
            page.keyboard.press("Backspace")
            
            for char in r:
                page.keyboard.type(char)
                time.sleep(random.uniform(0.04, 0.10))
            
            page.keyboard.press("Tab")
            page.wait_for_timeout(1000)

            # Consultar
            btn_consultar = frame.locator("button:has-text('CONSULTAR')").first
            btn_consultar.click()

            # 3. EXTRAER
            try:
                page.wait_for_selector("button:has-text('OTRA BÚSQUEDA')", timeout=15000)
                
                texto_ficha = frame.locator("body").inner_text()
                
                # REGLA ORO: Solo es "Sin info" si el nombre NO está registrado
                if "NOMBRE O RAZÓN SOCIAL NO REGISTRADA" in texto_ficha:
                    print(" RUT inexistente en portal. Marcando.")
                    with engine.connect() as con:
                        con.execute(text("UPDATE prospects SET telefono = 'SIN INFO' WHERE id = :id"), {"id": p_id})
                        con.commit()
                else:
                    # --- EXTRACCIÓN ENRIQUECIDA ---
                    
                    # 1. Defunción
                    es_fallecido = "NO"
                    if "Registra Defunción SI" in texto_ficha.replace(":",""): 
                        es_fallecido = "SI"
                    
                    # 2. Fecha Nacimiento (Flexible)
                    nacimiento = None
                    match_nac = re.search(r'Nacimiento\s*[:\-]*\s*(\d{2}/\d{2}/\d{4})', texto_ficha, re.IGNORECASE)
                    if match_nac: 
                        nacimiento = match_nac.group(1)
                    
                    # 3. Dirección y Comuna (Flexible)
                    direccion = None
                    if "DIRECCIONES" in texto_ficha:
                        # Buscamos la primera linea que parece direccion después de la cabecera
                        lines = [l.strip() for l in texto_ficha.split('\n') if l.strip()]
                        for i, line in enumerate(lines):
                            if "DIRECCIONES" in line and i + 1 < len(lines):
                                direccion = lines[i+1]
                                break
                    
                    # 4. Teléfonos (Prioridad 9XXXXXXXX)
                    fonos = re.findall(r'\b9\d{8}\b|\b\d{8}\b', texto_ficha)
                    tel = fonos[0] if fonos else "SIN TEL"
                    
                    print(f" ¡DATOS!: {tel} | Fallecido: {es_fallecido} | Nacimiento: {nacimiento}")
                    
                    with engine.connect() as con:
                        con.execute(text("""
                            UPDATE prospects 
                            SET telefono = :t, 
                                fallecido = :f, 
                                fecha_nacimiento = :n, 
                                ultima_direccion = :d 
                            WHERE id = :id
                        """), {
                            "t": tel, "f": es_fallecido, "n": nacimiento, "d": direccion, "id": p_id
                        })
                        con.commit()
                
                # Volver con pausa humana
                page.wait_for_timeout(random.randint(2000, 5000))
                btn_otra = frame.locator("button:has-text('OTRA BÚSQUEDA')").first
                btn_otra.click()
                
            except Exception as e:
                print(f" Error extrayendo ficha. Marcando RUT como defectuoso... {e}")
                with engine.connect() as con:
                    con.execute(text("UPDATE prospects SET telefono = 'RUT ERROR' WHERE id = :id"), {"id": p_id})
                    con.commit()

        except Exception as e:
            print(f" Error general en interacción con el portal: {e}")
            with engine.connect() as con:
                con.execute(text("UPDATE prospects SET telefono = 'RUT ERROR' WHERE id = :id"), {"id": p_id})
                con.commit()

    return True # Indicar que hay posibilidad de más registros

if __name__ == "__main__":
    while True:
        print("\n Iniciando nueva sesión de navegación segura...")
        with sync_playwright() as p:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(user_agent=ua, viewport={'width': 1280, 'height': 800})
            page = context.new_page()

            try:
                if login_transunion(page):
                    continuar = extraer_telefonos_por_rut(page, batch_size=25)
                    if not continuar:
                        print(" Proceso finalizado. No hay más registros.")
                        browser.close()
                        break
                
                print(" Esperando 10 segundos antes de rotar sesión...")
                time.sleep(10)
                browser.close()
            except Exception as e:
                print(f" Error en la sesión: {e}")
                browser.close()
                time.sleep(30)
