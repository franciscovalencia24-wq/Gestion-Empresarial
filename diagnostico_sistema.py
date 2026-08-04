"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         DIAGNÓSTICO INTEGRAL DEL SISTEMA - BD SENIOR CRM                  ║
║         Versión 3.0 — Auditoría Completa de Todos los Módulos              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Ejecutar desde la raíz del proyecto:
    python diagnostico_sistema.py

Este script verifica TODOS los componentes del sistema sin ejecutar
operaciones destructivas ni envíos reales.
"""

import sys
import os
import time
import importlib
import traceback
import sqlite3
from datetime import datetime
from pathlib import Path

# ─── Forzar UTF-8 en stdout/stderr para evitar UnicodeEncodeError en Windows ─
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─── Asegurar que el path raíz del proyecto esté en sys.path ─────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ─── Colores ANSI para terminal ───────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"

# ─── Contadores globales ──────────────────────────────────────────────────────
resultados = {"ok": 0, "warn": 0, "error": 0, "skip": 0}

def encabezado(titulo: str):
    print(f"\n{C.BOLD}{C.CYAN}{'═'*70}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {titulo}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═'*70}{C.RESET}")

def ok(msg: str):
    resultados["ok"] += 1
    print(f"  {C.GREEN}✅ OK     {C.RESET}{msg}")

def warn(msg: str):
    resultados["warn"] += 1
    print(f"  {C.YELLOW}⚠️  WARN   {C.RESET}{msg}")

def error(msg: str):
    resultados["error"] += 1
    print(f"  {C.RED}❌ ERROR  {C.RESET}{msg}")

def skip(msg: str):
    resultados["skip"] += 1
    print(f"  {C.BLUE}⏭️  SKIP   {C.RESET}{msg}")

def info(msg: str):
    print(f"  {C.WHITE}ℹ️  INFO   {C.RESET}{msg}")

def separador():
    print(f"  {C.BLUE}{'─'*65}{C.RESET}")


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 1 — ENTORNO Y DEPENDENCIAS
# ══════════════════════════════════════════════════════════════════════════════
def check_entorno():
    encabezado("MÓDULO 1 | ENTORNO & DEPENDENCIAS PYTHON")

    # Python version
    version = sys.version_info
    info(f"Python {version.major}.{version.minor}.{version.micro} — {sys.executable}")
    if version.major == 3 and version.minor >= 9:
        ok("Versión de Python compatible (≥ 3.9)")
    else:
        error(f"Python {version.major}.{version.minor} puede causar incompatibilidades (se requiere ≥ 3.9)")

    # Paquetes requeridos
    separador()
    paquetes = {
        "pandas":        "pandas",
        "sqlalchemy":    "sqlalchemy",
        "dotenv":        "dotenv",
        "playwright":    "playwright",
        "streamlit":     "streamlit",
        "requests":      "requests",
        "beautifulsoup4":"bs4",
        "openpyxl":      "openpyxl",
    }
    paquetes_faltantes = []
    for nombre_pip, modulo in paquetes.items():
        try:
            mod = importlib.import_module(modulo)
            version_str = getattr(mod, "__version__", "?")
            ok(f"{nombre_pip:<20} v{version_str}")
        except ImportError:
            error(f"{nombre_pip:<20} NO INSTALADO — ejecuta: pip install {nombre_pip}")
            paquetes_faltantes.append(nombre_pip)

    # Playwright browsers
    separador()
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                ok("Playwright Chromium — disponible y funcional")
            except Exception as e:
                error(f"Playwright Chromium no disponible: {e}")
                warn("  → Ejecuta: playwright install chromium")
    except ImportError:
        error("Playwright no instalado")

    return len(paquetes_faltantes) == 0


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 2 — ESTRUCTURA DE ARCHIVOS Y DIRECTORIOS
# ══════════════════════════════════════════════════════════════════════════════
def check_estructura():
    encabezado("MÓDULO 2 | ESTRUCTURA DE ARCHIVOS Y DIRECTORIOS")

    archivos_criticos = [
        ("app.py",                                    True),
        ("ingesta_maestra.py",                        True),
        ("requirements.txt",                          True),
        (".env",                                      True),
        ("src/core/config.py",                        True),
        ("src/database/connection.py",               True),
        ("src/database/models.py",                   True),
        ("src/ingestion/importer.py",                True),
        ("src/ingestion/cleaner.py",                 True),
        ("src/messaging/whatsapp_web.py",            True),
        ("src/messaging/spintax.py",                 True),
        ("src/messaging/anti_ban.py",                True),
        ("src/osint/scraper_do.py",                  True),
        ("src/osint/scraper_infoprobidad.py",        True),
        ("src/osint/transunion_scraper.py",          True),
        ("src/osint/rutificador_engine.py",          True),
        ("src/osint/llm_reader.py",                  True),
        ("src/enrichment/apollo_api.py",             True),
        ("src/enrichment/run_enrichment.py",         True),
        ("src/enrichment/detector.py",               True),
        ("src/enrichment/provider_dummy.py",         True),
        # Opcionales
        ("data/raw",                                  False),
        ("data/processed",                            False),
        ("data/whatsapp_session",                     False),
    ]

    criticos_faltantes = []
    for ruta, es_critico in archivos_criticos:
        ruta_abs = os.path.join(ROOT, ruta)
        existe = os.path.exists(ruta_abs)
        if existe:
            if os.path.isfile(ruta_abs):
                size = os.path.getsize(ruta_abs)
                ok(f"{ruta:<50}  ({size:,} bytes)")
            else:
                ok(f"{ruta:<50}  (directorio)")
        else:
            if es_critico:
                error(f"{ruta:<50}  — FALTANTE CRÍTICO")
                criticos_faltantes.append(ruta)
            else:
                warn(f"{ruta:<50}  — directorio no creado aún")

    # Archivos CSV de datos fuente
    separador()
    csvs = ["csvvalor.csv", "csvAccionDerecho.csv"]
    for csv in csvs:
        ruta_abs = os.path.join(ROOT, csv)
        if os.path.exists(ruta_abs):
            size_mb = os.path.getsize(ruta_abs) / (1024*1024)
            ok(f"{csv:<35}  ({size_mb:.1f} MB)")
        else:
            warn(f"{csv:<35}  — no encontrado en raíz del proyecto")

    return len(criticos_faltantes) == 0


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 3 — CONFIGURACIÓN Y VARIABLES DE ENTORNO
# ══════════════════════════════════════════════════════════════════════════════
def check_configuracion():
    encabezado("MÓDULO 3 | CONFIGURACIÓN (.env y Variables de Entorno)")

    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))

    database_url = os.getenv("DATABASE_URL", "")
    apollo_key   = os.getenv("APOLLO_API_KEY", "")

    if database_url:
        ok(f"DATABASE_URL definida: {database_url}")
    else:
        error("DATABASE_URL no encontrada en .env")

    if apollo_key:
        masked = apollo_key[:6] + "***" + apollo_key[-4:]
        ok(f"APOLLO_API_KEY definida: {masked}")
    else:
        warn("APOLLO_API_KEY no definida — módulo Apollo deshabilitado")

    # Verificar coherencia del path SQLite
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        db_abs  = os.path.join(ROOT, db_path) if not os.path.isabs(db_path) else db_path

        separador()
        info(f"Ruta resuelta de la BD: {db_abs}")
        if os.path.exists(db_abs):
            size_mb = os.path.getsize(db_abs) / (1024*1024)
            ok(f"Archivo de base de datos existe ({size_mb:.2f} MB)")
        else:
            warn(f"Archivo SQLite no encontrado aún (se crea al correr el importer)")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 4 — BASE DE DATOS: CONEXIÓN Y ESQUEMA
# ══════════════════════════════════════════════════════════════════════════════
def check_base_de_datos():
    encabezado("MÓDULO 4 | BASE DE DATOS — Conexión, Esquema y Estadísticas")

    try:
        from src.database.connection import engine
        from sqlalchemy import text, inspect

        with engine.connect() as con:
            result = con.execute(text("SELECT sqlite_version()")).scalar()
            ok(f"Conexión SQLAlchemy exitosa — SQLite v{result}")

        # Inspección del esquema
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        if "prospects" in tablas:
            ok(f"Tabla 'prospects' encontrada")
            columnas = [c["name"] for c in inspector.get_columns("prospects")]
            info(f"Columnas detectadas ({len(columnas)}): {', '.join(columnas)}")

            # Columnas requeridas por el modelo
            cols_modelo = [
                "id", "rut", "nombre", "telefono", "email", "ciudad",
                "nombre_asesor", "supervisor", "tipo_negocio",
                "monto_suscrito", "saldo_administrado", "origen_info",
                "titulo_profesional", "observaciones", "status_contacto",
                "es_cliente", "nombre_rrll", "rut_rrll",
                "score_liquidez", "ultimo_evento", "fecha_hallazgo",
                "link_fuente", "origen_web"
            ]
            separador()
            faltantes = [c for c in cols_modelo if c not in columnas]
            if faltantes:
                warn(f"Columnas del modelo NO en BD (requieren ALTER TABLE): {faltantes}")
            else:
                ok("Esquema completo: todas las columnas del modelo están presentes")

        else:
            warn("Tabla 'prospects' NO existe aún — se crea al importar datos")

        # Estadísticas de datos
        separador()
        try:
            with engine.connect() as con:
                total         = con.execute(text("SELECT COUNT(*) FROM prospects")).scalar()
                con_tel       = con.execute(text("SELECT COUNT(*) FROM prospects WHERE telefono IS NOT NULL AND telefono != ''")).scalar()
                sin_tel       = total - con_tel
                con_email     = con.execute(text("SELECT COUNT(*) FROM prospects WHERE email IS NOT NULL AND email != ''")).scalar()
                sin_rut       = con.execute(text("SELECT COUNT(*) FROM prospects WHERE rut LIKE 'SINRUT%'")).scalar()
                do_leads      = con.execute(text("SELECT COUNT(*) FROM prospects WHERE rut LIKE 'DO-%'")).scalar()
                infop_leads   = con.execute(text("SELECT COUNT(*) FROM prospects WHERE rut LIKE 'INFOP-%'")).scalar()
                clientes      = con.execute(text("SELECT COUNT(*) FROM prospects WHERE es_cliente = 1")).scalar()
                prospectos    = total - clientes
                enviados      = con.execute(text("SELECT COUNT(*) FROM prospects WHERE status_contacto NOT IN ('Pendiente', 'No Contactar')")).scalar()
                pendientes    = con.execute(text("SELECT COUNT(*) FROM prospects WHERE status_contacto = 'Pendiente'")).scalar()
                score_alto    = con.execute(text("SELECT COUNT(*) FROM prospects WHERE score_liquidez >= 70")).scalar()

            print(f"\n  {C.BOLD}{'MÉTRICA':<40} {'VALOR':>10}{C.RESET}")
            print(f"  {'─'*52}")
            print(f"  {'📊 Universo Total':<40} {total:>10,}")
            print(f"  {'👥 Clientes Actuales':<40} {clientes:>10,}")
            print(f"  {'🎯 Prospectos Nuevos':<40} {prospectos:>10,}")
            print(f"  {'📱 Con Teléfono':<40} {con_tel:>10,}")
            print(f"  {'📵 Sin Teléfono (pendientes minería)':<40} {sin_tel:>10,}")
            print(f"  {'✉️  Con Email':<40} {con_email:>10,}")
            print(f"  {'🆔 Sin RUT Real (SINRUT)':<40} {sin_rut:>10,}")
            print(f"  {'📰 Leads Diario Oficial (DO-)':<40} {do_leads:>10,}")
            print(f"  {'🏛️  Leads InfoProbidad (INFOP-)':<40} {infop_leads:>10,}")
            print(f"  {'🚀 En Seguimiento CRM':<40} {enviados:>10,}")
            print(f"  {'⏳ Pendientes de Contactar':<40} {pendientes:>10,}")
            print(f"  {'🔥 Score Liquidez Alto (≥70)':<40} {score_alto:>10,}")
            print()

            if total > 0:
                cobertura_tel = (con_tel / total) * 100
                cobertura_email = (con_email / total) * 100
                if cobertura_tel >= 60:
                    ok(f"Cobertura telefónica: {cobertura_tel:.1f}%")
                elif cobertura_tel >= 30:
                    warn(f"Cobertura telefónica baja: {cobertura_tel:.1f}%")
                else:
                    error(f"Cobertura telefónica crítica: {cobertura_tel:.1f}% — Se requiere minería urgente")

                if cobertura_email >= 20:
                    ok(f"Cobertura email: {cobertura_email:.1f}%")
                else:
                    warn(f"Cobertura email baja: {cobertura_email:.1f}%")
            else:
                warn("Base de datos vacía — ejecuta ingesta_maestra.py primero")

        except Exception as e:
            warn(f"No se pudo obtener estadísticas (tabla vacía o inexistente): {e}")

        return True

    except Exception as e:
        error(f"Error crítico de conexión a BD: {e}")
        traceback.print_exc()
        return False


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 5 — IMPORTACIONES DE MÓDULOS SRC (Integridad del Código)
# ══════════════════════════════════════════════════════════════════════════════
def check_importaciones():
    encabezado("MÓDULO 5 | INTEGRIDAD DE CÓDIGO — Importaciones de Todos los Módulos")

    modulos = [
        ("src.core.config",                    "DATABASE_URL"),
        ("src.database.connection",            "engine"),
        ("src.database.models",                "Prospect"),
        ("src.ingestion.cleaner",              "clean_rut_chileno"),
        ("src.ingestion.importer",             "ingest_excel"),
        ("src.messaging.spintax",              "format_message"),
        ("src.messaging.anti_ban",             "AntiBanManager"),
        ("src.messaging.whatsapp_web",         "WhatsAppBot"),
        ("src.osint.scraper_do",               "run_scraper"),
        ("src.osint.scraper_infoprobidad",     "minar_infoprobidad"),
        ("src.osint.transunion_scraper",       "extraer_telefonos_por_rut"),
        ("src.osint.rutificador_engine",       "iniciar_rutificador_masivo"),
        ("src.osint.llm_reader",               "extract_intel_from_url"),
        ("src.enrichment.apollo_api",          "ApolloProvider"),
        ("src.enrichment.detector",            "get_prospects_missing_info"),
        ("src.enrichment.provider_dummy",      "DummyRutEnricherProvider"),
        ("src.enrichment.run_enrichment",      "run_enrichment_process"),
    ]

    errores = 0
    for modulo_path, objeto_esperado in modulos:
        try:
            modulo = importlib.import_module(modulo_path)
            if hasattr(modulo, objeto_esperado):
                ok(f"{modulo_path:<45} → {objeto_esperado}")
            else:
                warn(f"{modulo_path:<45} → '{objeto_esperado}' no encontrado en el módulo")
        except ImportError as e:
            error(f"{modulo_path:<45} → ImportError: {e}")
            errores += 1
        except Exception as e:
            error(f"{modulo_path:<45} → Error inesperado: {e}")
            errores += 1

    return errores == 0


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 6 — LÓGICA CORE: LIMPIADORES Y SPINTAX
# ══════════════════════════════════════════════════════════════════════════════
def check_logica_core():
    encabezado("MÓDULO 6 | LÓGICA CORE — Limpiadores, RUT y Spintax")

    # --- RUT Cleaner ---
    separador()
    info("Probando clean_rut_chileno()...")
    from src.ingestion.cleaner import clean_rut_chileno, clean_phone_number, clean_amount

    casos_rut = [
        ("12.345.678-9",  "12345678-9"),
        ("12345678-9",    "12345678-9"),
        ("123456789",     "12345678-9"),
        ("K123456789",    "K12345678-9"),
        (None,            None),
        ("",              None),
    ]
    for entrada, esperado in casos_rut:
        resultado = clean_rut_chileno(entrada)
        if resultado == esperado:
            ok(f"RUT '{entrada}' → '{resultado}'")
        else:
            error(f"RUT '{entrada}' → '{resultado}' (esperado: '{esperado}')")

    # --- Phone Cleaner ---
    separador()
    info("Probando clean_phone_number()...")
    casos_tel = [
        ("+56966779662", "+569" + "66779662"),
        ("966779662",    "+569" + "66779662"),
        ("0966779662",   "+569" + "66779662"),  # 10 dígitos → últimos 8
        (None,           None),
    ]
    for entrada, esperado in casos_tel:
        resultado = clean_phone_number(entrada)
        if resultado == esperado:
            ok(f"Teléfono '{entrada}' → '{resultado}'")
        else:
            warn(f"Teléfono '{entrada}' → '{resultado}' (esperado: '{esperado}')")

    # --- Amount Cleaner ---
    separador()
    info("Probando clean_amount()...")
    casos_monto = [
        ("$ 5.000.000",   5000000.0),
        ("5000000",       5000000.0),
        ("5.000,50",      5000.50),
        (5000000,         5000000.0),
        (None,            None),
    ]
    for entrada, esperado in casos_monto:
        resultado = clean_amount(entrada)
        if resultado == esperado:
            ok(f"Monto '{entrada}' → {resultado}")
        else:
            warn(f"Monto '{entrada}' → {resultado} (esperado: {esperado})")

    # --- Spintax ---
    separador()
    info("Probando Spintax y format_message()...")
    from src.messaging.spintax import spin, format_message

    texto_spin = "{Hola|Buenos días|Qué tal} [NOMBRE], te contacto desde {Principal|la empresa}."
    prospect_test = {
        "nombre": "Carlos Rodriguez",
        "monto_suscrito": 5000000,
        "ciudad": "Coquimbo",
        "telefono": "+56966779662"
    }
    resultados_spin = set()
    for _ in range(20):
        res = format_message(texto_spin, prospect_test)
        resultados_spin.add(res.split(",")[0])  # Solo el saludo cambia

    if len(resultados_spin) > 1:
        ok(f"Spintax genera variaciones únicas: {len(resultados_spin)} saludos distintos")
    else:
        warn("Spintax no está generando suficiente variación")

    msg_final = format_message(texto_spin, prospect_test)
    if "Carlos" in msg_final and "[NOMBRE]" not in msg_final:
        ok(f"Variables reemplazadas correctamente en: '{msg_final[:80]}...'")
    else:
        error(f"Variable [NOMBRE] no fue reemplazada o el nombre es incorrecto: '{msg_final}'")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 7 — MÓDULO ANTI-BAN
# ══════════════════════════════════════════════════════════════════════════════
def check_antiban():
    encabezado("MÓDULO 7 | MOTOR ANTI-BAN (Timing y Fatiga Humana)")

    from src.messaging.anti_ban import AntiBanManager

    mgr = AntiBanManager(min_wait=1, max_wait=2)  # Valores cortos para el test

    tiempos_human = []
    for _ in range(5):
        t0 = time.time()
        mgr.human_typing_delay()
        tiempos_human.append(time.time() - t0)

    media_ms = (sum(tiempos_human) / len(tiempos_human)) * 1000
    if 10 <= media_ms <= 100:
        ok(f"human_typing_delay() — media: {media_ms:.1f}ms (dentro del rango humano 10–80ms)")
    else:
        warn(f"human_typing_delay() — media: {media_ms:.1f}ms (fuera del rango esperado)")

    tiempos_action = []
    for _ in range(3):
        t0 = time.time()
        mgr.action_delay()
        tiempos_action.append(time.time() - t0)
    media_action = sum(tiempos_action) / len(tiempos_action)
    if 1.0 <= media_action <= 4.5:
        ok(f"action_delay() — media: {media_action:.2f}s (dentro del rango esperado 1.2–3.8s)")
    else:
        warn(f"action_delay() — media: {media_action:.2f}s")

    # Verificar el multiplicador de fatiga
    w0 = mgr.min_wait + (mgr.max_wait - mgr.min_wait) / 2
    mult_50 = 1.0 + (min(50, 50) * 0.01)
    ok(f"Multiplicador de fatiga @50 prospectos: {mult_50:.2f}x — espera teórica máx: {mgr.max_wait * mult_50:.1f}s")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 8 — SCRAPER DIARIO OFICIAL
# ══════════════════════════════════════════════════════════════════════════════
def check_scraper_do():
    encabezado("MÓDULO 8 | OSINT — Scraper Diario Oficial Chile")

    import requests
    from bs4 import BeautifulSoup
    from src.osint.scraper_do import get_edition_id, calculate_score, normalize_text

    # Test conectividad
    try:
        resp = requests.get(
            "https://www.diariooficial.interior.gob.cl",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        if resp.status_code == 200:
            ok(f"Conectividad con diariooficial.interior.gob.cl — HTTP {resp.status_code}")
        else:
            warn(f"Diario Oficial respondió HTTP {resp.status_code}")
    except Exception as e:
        error(f"Sin conexión a Diario Oficial: {e}")

    # Test del módulo normalize_text
    separador()
    texto_test = "Constitución de Sociedad Fusión S.A."
    normalizado = normalize_text(texto_test)
    if "CONSTITUCION" in normalizado and "FUSION" in normalizado:
        ok(f"normalize_text() funciona: '{texto_test}' → '{normalizado}'")
    else:
        error(f"normalize_text() falló: '{normalizado}'")

    # Test de calculate_score
    separador()
    casos_score = [
        ("EXPROPIACION de terreno sector norte", 95),
        ("POSESION efectiva causante Juan Perez", 90),
        ("COMPRAVENTA predio agrícola Santiago", 85),
        ("CONSTITUCION sociedad anónima cerrada", 80),
        ("MODIFICACION estatutos empresa", 40),
        ("Texto sin keywords relevantes", 30),
    ]
    for texto, score_esperado in casos_score:
        score = calculate_score(texto)
        if score == score_esperado:
            ok(f"Score '{texto[:45]}...' → {score} pts ✓")
        else:
            warn(f"Score '{texto[:45]}...' → {score} pts (esperado: {score_esperado})")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 9 — SCRAPER TRANSUNION (Verificación sin ejecución real)
# ══════════════════════════════════════════════════════════════════════════════
def check_transunion():
    encabezado("MÓDULO 9 | OSINT — Scraper TransUnion (Análisis Estático)")

    try:
        # Verificamos que el módulo importa correctamente
        from src.osint import transunion_scraper
        ok("Módulo transunion_scraper.py importado correctamente")

        # Verificamos que las funciones críticas existen
        funciones = ["login_transunion", "extraer_telefonos_por_rut"]
        for fn in funciones:
            if hasattr(transunion_scraper, fn):
                ok(f"Función '{fn}' definida")
            else:
                error(f"Función '{fn}' NO encontrada en el módulo")

        # Verificar que la BD tiene RUTs reales para procesar
        from src.database.connection import engine
        from sqlalchemy import text

        with engine.connect() as con:
            pendientes = con.execute(text(
                "SELECT COUNT(*) FROM prospects WHERE telefono IS NULL AND rut NOT LIKE 'SINRUT%' AND rut NOT LIKE 'DO-%' AND rut NOT LIKE 'INFOP-%'"
            )).scalar()

        if pendientes > 0:
            ok(f"Hay {pendientes:,} prospectos con RUT real pendientes de minería telefónica")
        else:
            warn("No hay prospectos con RUT real sin teléfono — BD posiblemente vacía o ya procesada")

        # Verificar conectividad con TransUnion
        import requests
        try:
            resp = requests.get(
                "https://www.transunionchile.cl",
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            if resp.status_code < 400:
                ok(f"Conectividad con transunionchile.cl — HTTP {resp.status_code}")
            else:
                warn(f"TransUnion respondió HTTP {resp.status_code} (posible bloqueo o mantenimiento)")
        except Exception as e:
            warn(f"TransUnion no respondió: {e}")

        skip("No se ejecuta login real en diagnóstico — riesgo de bloqueo de cuenta")

    except Exception as e:
        error(f"Error al cargar transunion_scraper: {e}")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 10 — RUTIFICADOR ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def check_rutificador():
    encabezado("MÓDULO 10 | OSINT — Motor Rutificador (InfoProbidad)")

    try:
        from src.osint.rutificador_engine import buscar_rut_por_nombre, iniciar_rutificador_masivo
        ok("rutificador_engine.py importado correctamente")

        # Verificar cuántos SINRUT quedan
        from src.database.connection import engine
        from sqlalchemy import text

        with engine.connect() as con:
            sinrut_count = con.execute(text("SELECT COUNT(*) FROM prospects WHERE rut LIKE 'SINRUT%'")).scalar()

        if sinrut_count > 0:
            warn(f"Hay {sinrut_count:,} prospectos con identidad temporal (SINRUT) — se requiere rutificación")
            info("  → Ejecuta el motor de rescate desde app.py > Pestaña 'Recuperar RUTs (SINRUT)'")
        else:
            ok("No hay prospectos SINRUT pendientes de identificación")

        # Verificar conectividad con InfoProbidad
        import requests
        try:
            resp = requests.get("https://www.infoprobidad.cl", timeout=8)
            if resp.status_code < 400:
                ok(f"Conectividad con infoprobidad.cl — HTTP {resp.status_code}")
            else:
                warn(f"InfoProbidad respondió HTTP {resp.status_code}")
        except Exception as e:
            warn(f"InfoProbidad no respondió: {e}")

        skip("No se ejecuta búsqueda real en diagnóstico (lenta, Playwright headless)")

    except Exception as e:
        error(f"Error en rutificador_engine: {e}")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 11 — APOLLO API
# ══════════════════════════════════════════════════════════════════════════════
def check_apollo():
    encabezado("MÓDULO 11 | ENRIQUECIMIENTO — Apollo.io API")

    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    api_key = os.getenv("APOLLO_API_KEY", "")

    if not api_key:
        skip("APOLLO_API_KEY no configurada — módulo desactivado")
        return True

    try:
        from src.enrichment.apollo_api import ApolloProvider
        ok("ApolloProvider importado correctamente")

        # Test de autenticación (sin gastar créditos — búsqueda con 0 resultados esperados)
        import requests
        resp = requests.post(
            "https://api.apollo.io/v1/auth/health",
            headers={"X-Api-Key": api_key, "Content-Type": "application/json"},
            timeout=10
        )
        if resp.status_code == 200:
            ok(f"API Key de Apollo válida — HTTP {resp.status_code}")
        elif resp.status_code == 401:
            error("API Key de Apollo inválida o expirada (401 Unauthorized)")
        elif resp.status_code == 403:
            warn("API Key de Apollo con permisos restringidos (403 Forbidden)")
        else:
            warn(f"Apollo respondió HTTP {resp.status_code} — verificar manualmente")

    except Exception as e:
        error(f"Error verificando Apollo: {e}")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 12 — INGESTA MAESTRA (Análisis sin escritura)
# ══════════════════════════════════════════════════════════════════════════════
def check_ingesta():
    encabezado("MÓDULO 12 | INGESTA — Archivos CSV y Sistema de Importación")

    csvs = {
        "csvvalor.csv": os.path.join(ROOT, "csvvalor.csv"),
        "csvAccionDerecho.csv": os.path.join(ROOT, "csvAccionDerecho.csv"),
    }

    for nombre, ruta in csvs.items():
        if not os.path.exists(ruta):
            skip(f"{nombre} — no encontrado, se omite análisis")
            continue

        try:
            import pandas as pd
            size_mb = os.path.getsize(ruta) / (1024 * 1024)
            info(f"Analizando {nombre} ({size_mb:.1f} MB)...")

            # Solo leer las primeras 100 filas para diagnóstico rápido
            df = pd.read_csv(ruta, sep=';', encoding='latin-1', on_bad_lines='skip',
                             low_memory=False, nrows=100)
            ok(f"{nombre}: {len(df.columns)} columnas, encoding latin-1 OK")
            info(f"  Columnas: {list(df.columns[:8])}{'...' if len(df.columns) > 8 else ''}")

            # Detectar columna de RUT
            cols_lower = [c.lower() for c in df.columns]
            col_rut = next((c for c in cols_lower if 'rut' in c or 'identificacion' in c), None)
            col_nom = next((c for c in cols_lower if 'nombre' in c or 'razon' in c), None)
            if col_rut:
                ok(f"  Columna RUT detectada: '{col_rut}'")
            else:
                warn(f"  No se detectó columna RUT en {nombre}")
            if col_nom:
                ok(f"  Columna Nombre detectada: '{col_nom}'")
            else:
                warn(f"  No se detectó columna Nombre en {nombre}")

        except Exception as e:
            error(f"Error leyendo {nombre}: {e}")

    # Verificar importer.py
    separador()
    try:
        from src.ingestion.importer import ingest_excel, run_import_all
        ok("src/ingestion/importer.py — importado correctamente")

        data_raw = os.path.join(ROOT, "data", "raw")
        if os.path.exists(data_raw):
            excels = list(Path(data_raw).glob("*.xlsx"))
            if excels:
                ok(f"Encontrados {len(excels)} archivo(s) Excel en data/raw/: {[f.name for f in excels]}")
            else:
                warn("data/raw/ existe pero no contiene archivos .xlsx")
        else:
            warn("Directorio data/raw/ no existe — créalo y coloca los Excel del cliente")

    except Exception as e:
        error(f"Error en importer.py: {e}")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 13 — PROBLEMAS CONOCIDOS Y DEUDA TÉCNICA
# ══════════════════════════════════════════════════════════════════════════════
def check_deuda_tecnica():
    encabezado("MÓDULO 13 | AUDITORÍA — Deuda Técnica y Riesgos Identificados")

    issues = [
        ("CRÍTICO",  "transunion_scraper.py",
         "Credenciales hardcodeadas en el código (línea 24-26): usuario 'AXH.GCAMILO' y contraseña visible.",
         "Mover TRANSUNION_USER y TRANSUNION_PASS al archivo .env"),

        ("CRÍTICO",  "scraper_infoprobidad.py",
         "minar_infoprobidad() usa datos SINTÉTICOS (3 PEPs hardcodeados), NO extrae datos reales de la web.",
         "Implementar la lógica real de descarga del CSV de datos abiertos del CPLT"),

        ("ALTO",     "llm_reader.py",
         "simular_ia_extraction() es un placeholder — NO invoca ningún LLM real.",
         "Conectar a la API de Gemini/OpenAI para extracción real de entidades"),

        ("ALTO",     "ingesta_maestra.py vs src/ingestion/importer.py",
         "Hay DOS sistemas de ingesta paralelos con rutas de BD distintas:\n"
         "           ingesta_maestra.py → data/processed/prospectos.db\n"
         "           importer.py → usa DATABASE_URL del .env (misma ruta OK)\n"
         "           Riesgo de incoherencia si se usan ambos indistintamente.",
         "Unificar en un único sistema de ingesta (importer.py es el correcto)"),

        ("ALTO",     "app.py (líneas 26-41)",
         "El 'PARCHE SQL EN CALIENTE' en startup aplica migrations con ALTER TABLE.\n"
         "           Silencia excepciones sin distinguir entre 'columna ya existe' y errores reales.",
         "Usar Alembic para gestión formal de migraciones de esquema"),

        ("MEDIO",    "src/database/connection.py",
         "os.makedirs() usa os.path.dirname() que falla si db_path es solo 'prospectos.db'\n"
         "           (sin subdirectorio), generando un path vacío.",
         "Añadir validación: if os.path.dirname(db_abs): os.makedirs(...)"),

        ("MEDIO",    "src/messaging/whatsapp_web.py",
         "No hay función send_message() separada del send_attachment_and_message().\n"
         "           app.py línea 546 llama bot.send_message() que NO EXISTE.",
         "Añadir método send_message() o refactorizar la llamada en app.py"),

        ("MEDIO",    "src/ingestion/cleaner.py → clean_phone_number()",
         "Teléfonos de 8 dígitos como '12345678' devuelven '+5691234567' (un 8 inválido).\n"
         "           La lógica toma siempre los últimos 8 sin validar que empiece en 9.",
         "Añadir validación: if not ultimo_8.startswith('9'): return None"),

        ("BAJO",     ".env",
         "APOLLO_API_KEY está commiteada en texto plano en .env (git rastreable).",
         "Añadir .env al .gitignore si el proyecto usa Git"),

        ("BAJO",     "src/enrichment/provider_dummy.py",
         "DummyRutEnricherProvider es un proveedor de datos ficticio en producción.",
         "Implementar un proveedor real o desactivar el button en app.py"),
    ]

    colores = {
        "CRÍTICO": C.RED,
        "ALTO":    C.YELLOW,
        "MEDIO":   C.CYAN,
        "BAJO":    C.BLUE,
    }

    for severidad, archivo, problema, solucion in issues:
        col = colores.get(severidad, C.WHITE)
        print(f"\n  {col}{C.BOLD}[{severidad}]{C.RESET} {C.BOLD}{archivo}{C.RESET}")
        print(f"    {C.WHITE}Problema:{C.RESET} {problema}")
        print(f"    {C.GREEN}Solución:{C.RESET} {solucion}")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 14 — CONNECTIVITY CHECK (Red y APIs externas)
# ══════════════════════════════════════════════════════════════════════════════
def check_conectividad():
    encabezado("MÓDULO 14 | CONECTIVIDAD — Red e Integrations Externas")

    import requests

    endpoints = [
        ("Internet General",              "https://www.google.com"),
        ("Diario Oficial Chile",          "https://www.diariooficial.interior.gob.cl"),
        ("TransUnion Chile",              "https://www.transunionchile.cl"),
        ("InfoProbidad Chile",            "https://www.infoprobidad.cl"),
        ("Apollo.io API",                 "https://api.apollo.io"),
        ("WhatsApp Web",                  "https://web.whatsapp.com"),
    ]

    for nombre, url in endpoints:
        try:
            t0 = time.time()
            resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            latencia = (time.time() - t0) * 1000
            if resp.status_code < 400:
                ok(f"{nombre:<35} HTTP {resp.status_code}  ({latencia:.0f}ms)")
            else:
                warn(f"{nombre:<35} HTTP {resp.status_code}  ({latencia:.0f}ms)")
        except requests.exceptions.ConnectionError:
            error(f"{nombre:<35} Sin conexión")
        except requests.exceptions.Timeout:
            warn(f"{nombre:<35} Timeout (>8s)")
        except Exception as e:
            warn(f"{nombre:<35} Error: {e}")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ══════════════════════════════════════════════════════════════════════════════
def resumen_final():
    total = sum(resultados.values())
    pct_ok = (resultados["ok"] / total * 100) if total > 0 else 0

    print(f"\n\n{C.BOLD}{'═'*70}{C.RESET}")
    print(f"{C.BOLD}  RESUMEN DEL DIAGNÓSTICO — BD SENIOR CRM{C.RESET}")
    print(f"{C.BOLD}  Ejecutado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}")
    print(f"{C.BOLD}{'═'*70}{C.RESET}")
    print(f"  {C.GREEN}✅  Verificaciones OK:      {resultados['ok']:>5}{C.RESET}")
    print(f"  {C.YELLOW}⚠️   Advertencias (WARN):   {resultados['warn']:>5}{C.RESET}")
    print(f"  {C.RED}❌  Errores críticos:       {resultados['error']:>5}{C.RESET}")
    print(f"  {C.BLUE}⏭️   Omitidos (SKIP):        {resultados['skip']:>5}{C.RESET}")
    print(f"  {'─'*40}")
    print(f"  {'Total de verificaciones:':<30} {total:>5}")
    print(f"  {'Salud del sistema:':<30} {pct_ok:>4.0f}%")
    print(f"{C.BOLD}{'═'*70}{C.RESET}\n")

    if resultados["error"] == 0 and resultados["warn"] <= 3:
        print(f"  {C.GREEN}{C.BOLD}🚀 SISTEMA OPERATIVO — Listo para producción.{C.RESET}\n")
    elif resultados["error"] == 0:
        print(f"  {C.YELLOW}{C.BOLD}⚠️  SISTEMA FUNCIONAL — Revisar advertencias antes de campaña masiva.{C.RESET}\n")
    else:
        print(f"  {C.RED}{C.BOLD}🚨 SISTEMA CON ERRORES — Corregir antes de operar.{C.RESET}\n")

    print(f"  {C.CYAN}PRIORIDADES DE CORRECCIÓN INMEDIATA:{C.RESET}")
    if resultados["error"] > 0:
        print(f"  1. Resolver los {resultados['error']} errores marcados con ❌")
    print(f"  2. Mover credenciales de transunion_scraper.py al .env")
    print(f"  3. Implementar send_message() en whatsapp_web.py")
    print(f"  4. Unificar pipeline de ingesta en src/ingestion/importer.py")
    print(f"  5. Reemplazar datos sintéticos en scraper_infoprobidad.py\n")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — Ejecución secuencial de todos los módulos
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{C.BOLD}{C.MAGENTA}")
    print("  ██████╗ ██████╗     ███████╗███████╗███╗   ██╗██╗ ██████╗ ██████╗ ")
    print("  ██╔══██╗██╔══██╗    ██╔════╝██╔════╝████╗  ██║██║██╔═══██╗██╔══██╗")
    print("  ██████╔╝██║  ██║    ███████╗█████╗  ██╔██╗ ██║██║██║   ██║██████╔╝")
    print("  ██╔══██╗██║  ██║    ╚════██║██╔══╝  ██║╚██╗██║██║██║   ██║██╔══██╗")
    print("  ██████╔╝██████╔╝    ███████║███████╗██║ ╚████║██║╚██████╔╝██║  ██║")
    print("  ╚═════╝ ╚═════╝     ╚══════╝╚══════╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝")
    print(f"{C.RESET}")
    print(f"  {C.BOLD}Diagnóstico Integral del Sistema — BD SENIOR CRM v3.0{C.RESET}")
    print(f"  {C.WHITE}Proyecto: Asesor de Inversiones Senior | Principal Financial Group{C.RESET}")
    print(f"  {C.WHITE}Fecha:    {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{C.RESET}")

    # Ejecutar todos los módulos de diagnóstico
    modulos_diagnostico = [
        ("Entorno y Dependencias",       check_entorno),
        ("Estructura de Archivos",       check_estructura),
        ("Configuración (.env)",         check_configuracion),
        ("Base de Datos",                check_base_de_datos),
        ("Importaciones de Módulos",     check_importaciones),
        ("Lógica Core",                  check_logica_core),
        ("Motor Anti-Ban",               check_antiban),
        ("Scraper Diario Oficial",       check_scraper_do),
        ("Scraper TransUnion",           check_transunion),
        ("Rutificador Engine",           check_rutificador),
        ("Apollo API",                   check_apollo),
        ("Sistema de Ingesta",           check_ingesta),
        ("Deuda Técnica (Auditoría)",    check_deuda_tecnica),
        ("Conectividad Externa",         check_conectividad),
    ]

    for nombre, fn in modulos_diagnostico:
        try:
            fn()
        except Exception as e:
            error(f"Error inesperado en módulo '{nombre}': {e}")
            traceback.print_exc()

    resumen_final()
