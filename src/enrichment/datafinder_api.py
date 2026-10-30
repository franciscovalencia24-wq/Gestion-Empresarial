"""
Módulo de Enriquecimiento Equifax / DataFinder — BD SENIOR
===========================================================
Permite consultar la plataforma corporativa Equifax DataFinder en Chile
para extraer información de contactabilidad de prospectos:
- Teléfonos móviles y fijos verificados
- Correos electrónicos
- Fecha de nacimiento / Edad
- Índice Socioeconómico (ISE / GSE)
- Dirección y Comuna

SEGURIDAD Y CONTROL DE COSTOS:
Límite estricto de 100 consultas mensuales configurado mediante
el sistema de cuotas persistente (SQLite + JSON fail-safe).
"""

import os
import sys

# Asegurar raíz del proyecto en sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import re
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(override=True)

from src.utils.rut_utils import format_rut_miles, clean_rut, validar_rut

logger = logging.getLogger("datafinder_api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ─── Excepciones Específicas ─────────────────────────────────────────────────

class DataFinderError(Exception):
    """Excepción base para DataFinder."""
    pass

class DataFinderQuotaExceededError(DataFinderError):
    """Excepción cuando se supera la cuota mensual estricta (ej. 100 consultas)."""
    pass

class DataFinderInvalidRutError(DataFinderError):
    """Excepción cuando el RUT ingresado no es válido matemáticamente."""
    pass

class DataFinderLowPotentialError(DataFinderError):
    """Excepción cuando el prospecto no califica para consumir una consulta valiosa."""
    pass

class DataFinderAuthError(DataFinderError):
    """Excepción cuando las credenciales de Equifax DataFinder son rechazadas."""
    pass

class DataFinderTimeoutError(DataFinderError):
    """Excepción cuando la plataforma Equifax excede el tiempo de respuesta."""
    pass


# ─── Gestor de Cuotas Mensuales ──────────────────────────────────────────────

class DataFinderQuotaManager:
    """
    Controlador estricto de cuota mensual para no superar el límite contratado (100 consultas).
    Persiste en SQLite (tabla datafinder_quota_logs) y en archivo JSON de respaldo.
    """
    JSON_PATH = "data/datafinder_quota.json"

    def __init__(self, db_path: str = "data/crm_database.db", max_monthly: int = 100):
        self.db_path = db_path
        self.max_monthly = max_monthly
        self._ensure_storage()

    def _ensure_storage(self):
        """Crea la tabla en SQLite y el archivo JSON si no existen."""
        os.makedirs("data", exist_ok=True)
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS datafinder_quota_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rut TEXT NOT NULL,
                    prospect_id INTEGER,
                    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    periodo_mes TEXT NOT NULL,
                    exito INTEGER DEFAULT 0,
                    ise TEXT,
                    telefonos_encontrados INTEGER DEFAULT 0,
                    emails_encontrados INTEGER DEFAULT 0,
                    datos_json TEXT,
                    observaciones TEXT
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_df_periodo ON datafinder_quota_logs(periodo_mes)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_df_rut ON datafinder_quota_logs(rut)")
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"No se pudo inicializar tabla de cuotas SQLite: {e}")

        # JSON Fallback
        if not os.path.exists(self.JSON_PATH):
            periodo = datetime.now().strftime("%Y-%m")
            self._write_json_fallback({
                "periodo": periodo,
                "consultas_consumidas": 0,
                "limite_mensual": self.max_monthly,
                "consultas_restantes": self.max_monthly,
                "ultimo_rut": None,
                "ultima_actualizacion": datetime.now().isoformat()
            })

    def _write_json_fallback(self, data: dict):
        try:
            with open(self.JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Error escribiendo JSON de cuotas: {e}")

    def get_periodo_actual(self) -> str:
        return datetime.now().strftime("%Y-%m")

    def get_quota_status(self) -> Dict[str, Any]:
        """Retorna el estado de consumo de la cuota mensual en vivo."""
        periodo = self.get_periodo_actual()
        consumidas = 0

        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(id) FROM datafinder_quota_logs WHERE periodo_mes = ?", (periodo,))
            res = c.fetchone()
            if res:
                consumidas = res[0]
            conn.close()
        except Exception as e:
            logger.warning(f"Error consultando cuota en SQLite: {e}. Usando respaldo JSON.")
            try:
                if os.path.exists(self.JSON_PATH):
                    with open(self.JSON_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("periodo") == periodo:
                            consumidas = data.get("consultas_consumidas", 0)
            except Exception:
                pass

        restantes = max(0, self.max_monthly - consumidas)
        return {
            "periodo": periodo,
            "consultas_consumidas": consumidas,
            "limite_mensual": self.max_monthly,
            "consultas_restantes": restantes,
            "cuota_disponible": restantes > 0
        }

    def check_can_consume(self):
        """Verifica si queda cuota disponible. Lanza DataFinderQuotaExceededError si no."""
        status = self.get_quota_status()
        if not status["cuota_disponible"]:
            raise DataFinderQuotaExceededError(
                f"LÍMITE MENSUAL ALCANZADO: Ya has consumido {status['consultas_consumidas']}/{status['limite_mensual']} "
                f"consultas en el periodo {status['periodo']}. Se bloquea la ejecución para evitar sobrecostos."
            )

    def log_consumption(self, rut: str, prospect_id: Optional[int], exito: bool,
                        ise: Optional[str], telefonos_cnt: int, emails_cnt: int,
                        datos: dict, observaciones: str = "") -> int:
        """Registra la consulta consumida en la base de datos y en el JSON."""
        periodo = self.get_periodo_actual()
        new_id = None
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                INSERT INTO datafinder_quota_logs (
                    rut, prospect_id, periodo_mes, exito, ise, 
                    telefonos_encontrados, emails_encontrados, datos_json, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                clean_rut(rut),
                prospect_id,
                periodo,
                1 if exito else 0,
                ise or "N/D",
                telefonos_cnt,
                emails_cnt,
                json.dumps(datos, ensure_ascii=False),
                observaciones
            ))
            conn.commit()
            new_id = c.lastrowid
            conn.close()
        except Exception as e:
            logger.error(f"Error registrando consulta en SQLite: {e}")

        # Actualizar JSON
        status = self.get_quota_status()
        self._write_json_fallback({
            "periodo": periodo,
            "consultas_consumidas": status["consultas_consumidas"],
            "limite_mensual": self.max_monthly,
            "consultas_restantes": status["consultas_restantes"],
            "ultimo_rut": clean_rut(rut),
            "ultima_actualizacion": datetime.now().isoformat()
        })
        return new_id


# ─── Conector Web DataFinder (Playwright) ────────────────────────────────────

class EquifaxDataFinderConnector:
    """
    Conector automatizado con Playwright para la plataforma Equifax DataFinder Chile.
    """
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        headless: Optional[bool] = None,
        max_monthly: Optional[int] = None,
        timeout_ms: int = 30000
    ):
        self.username = username or os.getenv("DATAFINDER_USER", "")
        self.password = password or os.getenv("DATAFINDER_PASS", "")
        self.base_url = base_url or os.getenv("DATAFINDER_URL", "https://web.datafinder.cl")
        
        headless_env = os.getenv("DATAFINDER_HEADLESS", "True").lower() in ["true", "1", "yes"]
        self.headless = headless if headless is not None else headless_env
        
        max_m = os.getenv("DATAFINDER_MAX_MONTHLY_QUERIES", "100")
        try:
            self.max_monthly = max_monthly if max_monthly is not None else int(max_m)
        except ValueError:
            self.max_monthly = 100

        self.timeout_ms = timeout_ms
        self.quota_mgr = DataFinderQuotaManager(max_monthly=self.max_monthly)

    def validate_prospect_before_query(
        self,
        rut: str,
        prospect_id: Optional[int] = None,
        force: bool = False,
        min_monto: float = 0.0
    ) -> Tuple[bool, str]:
        """
        Validación estricta ANTES de abrir el navegador web:
        1. Comprueba si queda cuota en el mes actual.
        2. Valida matemáticamente el RUT (Módulo 11).
        3. Comprueba si el prospecto ya tiene teléfono y email válidos en BD (para no gastar consultas).
        4. Comprueba si el prospecto está descartado o tiene monto menor al requerido.
        """
        # 1. Cuota mensual
        self.quota_mgr.check_can_consume()

        # 2. RUT
        if not rut or not str(rut).strip():
            raise DataFinderInvalidRutError("RUT vacío o nulo.")
            
        rut_clean = clean_rut(rut)
        if rut_clean.startswith("SINRUT") or rut_clean.startswith("INFOP") or rut_clean.startswith("DO"):
            raise DataFinderInvalidRutError(f"RUT no es una persona o empresa real: {rut}")

        if not validar_rut(rut):
            raise DataFinderInvalidRutError(f"El RUT {rut} tiene un dígito verificador matemáticamente incorrecto.")

        if force:
            return True, "Validación forzada por el usuario."

        # 3. Base de datos: verificar si ya está enriquecido
        try:
            import sqlite3
            conn = sqlite3.connect("data/crm_database.db")
            c = conn.cursor()
            
            if prospect_id:
                c.execute("SELECT rut, telefono, email, status_contacto, monto_suscrito FROM prospects WHERE id = ?", (prospect_id,))
            else:
                c.execute("SELECT rut, telefono, email, status_contacto, monto_suscrito FROM prospects WHERE rut = ? OR rut = ?", 
                          (rut_clean, format_rut_miles(rut)))
            
            row = c.fetchone()
            conn.close()

            if row:
                _, tel, em, status, monto = row
                
                # Descartado
                if status and "descartado" in str(status).lower():
                    raise DataFinderLowPotentialError(f"Prospecto con estado '{status}'. No se gastará cuota.")

                # Monto mínimo
                if min_monto > 0 and (monto or 0) < min_monto:
                    raise DataFinderLowPotentialError(f"Monto suscrito (${monto or 0:,.0f}) inferior al umbral mínimo (${min_monto:,.0f}).")

                # Ya cuenta con teléfono celular chileno válido (+569...) y correo
                has_phone = tel and len(re.sub(r'\D', '', str(tel))) >= 8 and "SIN TEL" not in str(tel) and "ERROR" not in str(tel)
                has_email = em and "@" in str(em)
                if has_phone and has_email:
                    raise DataFinderLowPotentialError(f"Prospecto ya cuenta con teléfono ({tel}) y email ({em}) registrados.")

        except (DataFinderLowPotentialError, DataFinderQuotaExceededError, DataFinderInvalidRutError):
            raise
        except Exception as e:
            logger.warning(f"Aviso al validar prospecto en base de datos: {e}")

        return True, "Prospecto válido y calificado para enriquecimiento."

    def _login(self, page) -> bool:
        """Maneja el inicio de sesión en Equifax DataFinder con múltiples selectores de respaldo."""
        if not self.username or not self.password:
            raise DataFinderAuthError(
                "Credenciales no configuradas. Define DATAFINDER_USER y DATAFINDER_PASS en tu archivo .env"
            )

        logger.info(f"Navegando al portal Equifax DataFinder: {self.base_url}")
        page.goto(self.base_url, timeout=self.timeout_ms)
        page.wait_for_timeout(2000)

        # Detectar si ya está iniciada la sesión
        content = page.content().lower()
        if "cerrar sesión" in content or "bienvenido" in content or "búsqueda por rut" in content or "datafinder" in page.title().lower():
            if "usuario" not in content and "password" not in content and "iniciar" not in content:
                logger.info("Sesión ya activa en Equifax DataFinder.")
                return True

        # Selectores de usuario
        user_selectors = [
            "input[name='username']",
            "input[name='usuario']",
            "input[name*='user']",
            "input[id*='usuario']",
            "input[id*='username']",
            "input[id*='txtUsuario']",
            "input[type='email']",
            "input[type='text']"
        ]
        
        user_input = None
        for sel in user_selectors:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                user_input = loc.first
                break

        if not user_input:
            # Fallback en caso de iframe
            for frame in page.frames:
                for sel in user_selectors:
                    loc = frame.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        user_input = loc.first
                        break
                if user_input:
                    break

        if not user_input:
            raise DataFinderAuthError("No se encontró el campo de usuario en la pantalla de login.")

        # Llenar usuario de forma humanizada
        user_input.click()
        user_input.fill("")
        for ch in self.username:
            page.keyboard.type(ch)
            time.sleep(0.03)

        # Selectores de password
        pass_selectors = [
            "input[type='password']",
            "input[name*='pass']",
            "input[name*='clave']",
            "input[id*='password']",
            "input[id*='txtClave']"
        ]
        pass_input = None
        for sel in pass_selectors:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                pass_input = loc.first
                break

        if not pass_input:
            raise DataFinderAuthError("No se encontró el campo de contraseña en la pantalla de login.")

        pass_input.click()
        pass_input.fill(self.password)
        time.sleep(0.5)

        # Botón de Login
        btn_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Ingresar')",
            "button:has-text('Iniciar')",
            "button:has-text('Login')",
            "button:has-text('Acceder')",
            "input[value*='Ingresar']"
        ]
        btn_clicked = False
        for sel in btn_selectors:
            btn = page.locator(sel)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                btn_clicked = True
                break

        if not btn_clicked:
            page.keyboard.press("Enter")

        page.wait_for_timeout(4000)

        # Validar si hubo error de login
        post_content = page.content().lower()
        if "credenciales incorrectas" in post_content or "usuario o contraseña no válidos" in post_content or "acceso denegado" in post_content:
            raise DataFinderAuthError("Credenciales inválidas en Equifax DataFinder.")

        logger.info("Inicio de sesión en Equifax DataFinder exitoso.")
        return True

    def _execute_search(self, page, rut_cuerpo: str, rut_dv: str) -> str:
        """
        Ejecuta la búsqueda por RUT dentro de la interfaz de DataFinder
        y devuelve el texto del reporte o ficha para su análisis.
        """
        rut_completo = f"{rut_cuerpo}-{rut_dv}"
        rut_con_puntos = format_rut_miles(rut_completo)

        # Buscar campo de RUT
        rut_inputs = [
            "input[id*='rut']",
            "input[name*='rut']",
            "input[placeholder*='RUT']",
            "input[placeholder*='Rut']",
            "input[id*='txtRut']",
            "input[type='text']"
        ]

        target_input = None
        target_page_or_frame = page

        # Búsqueda en página principal o iframes
        for sel in rut_inputs:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                target_input = loc.first
                break

        if not target_input:
            for frame in page.frames:
                for sel in rut_inputs:
                    loc = frame.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        target_input = loc.first
                        target_page_or_frame = frame
                        break
                if target_input:
                    break

        if not target_input:
            # Si no hay campo directo, buscar sección de menú "Búsqueda por RUT"
            menu = page.locator("text=BÚSQUEDA POR RUT, text=Consulta RUT, text=DataFinder Personas").first
            if menu.count() > 0 and menu.is_visible():
                menu.click()
                page.wait_for_timeout(1500)
                for sel in rut_inputs:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        target_input = loc.first
                        break

        if not target_input:
            raise DataFinderError("No se encontró el campo de búsqueda por RUT en la plataforma.")

        target_input.click()
        target_input.click(click_count=3)
        page.keyboard.press("Backspace")

        # Intentar ingresar RUT (algunas plataformas admiten con guion o sin él)
        for ch in rut_completo:
            page.keyboard.type(ch)
            time.sleep(0.04)

        page.keyboard.press("Tab")
        page.wait_for_timeout(800)

        # Botón consultar
        consultar_btns = [
            "button:has-text('CONSULTAR')",
            "button:has-text('Consultar')",
            "button:has-text('BUSCAR')",
            "button:has-text('Buscar')",
            "input[value*='Consultar']",
            "input[value*='Buscar']"
        ]
        btn_consultar = None
        for sel in consultar_btns:
            loc = target_page_or_frame.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                btn_consultar = loc.first
                break

        if btn_consultar:
            btn_consultar.click()
        else:
            page.keyboard.press("Enter")

        # Esperar carga del reporte
        page.wait_for_timeout(3500)
        return page.content()

    def parse_report_content(self, html_or_text: str, rut_consultado: str) -> Dict[str, Any]:
        """
        Extrae de forma estructurada los campos clave:
        - telefonos (móviles ordenados primero)
        - emails
        - fecha_nacimiento
        - edad
        - ise / gse
        - direccion y comuna
        """
        clean_text = re.sub(r'<[^>]+>', ' ', html_or_text)
        clean_text = ' '.join(clean_text.split())

        result: Dict[str, Any] = {
            "rut": clean_rut(rut_consultado),
            "rut_formateado": format_rut_miles(rut_consultado),
            "encontrado": False,
            "nombre_completo": None,
            "fecha_nacimiento": None,
            "edad": None,
            "ise": None,
            "telefonos": [],
            "telefono_principal": None,
            "emails": [],
            "email_principal": None,
            "direccion": None,
            "comuna": None,
            "ciudad": None,
            "estado_civil": None,
            "raw_snippet": clean_text[:600],
            "error": None
        }

        # 1. Comprobar si no fue encontrado
        no_encontrado_phrases = [
            "no se encontraron resultados",
            "rut no registrado",
            "sin información",
            "no registra información",
            "rut inexistente",
            "sin coincidencias"
        ]
        for phrase in no_encontrado_phrases:
            if phrase in clean_text.lower():
                result["error"] = "RUT sin información registrada en Equifax DataFinder."
                return result

        result["encontrado"] = True

        # 2. Extracción de Teléfonos
        # Busca móviles (+569XXXXXXXX, 9XXXXXXXX) y red fija (22XXXXXXX, etc.)
        raw_phones = re.findall(r'(?:\+?56\s*)?(?:9\s*\d{4}\s*\d{4}|[2-9]\s*\d{3}\s*\d{4}|\b\d{8}\b)', html_or_text)
        telefonos_limpios = []
        for p in raw_phones:
            digits = re.sub(r'\D', '', p)
            if digits.startswith("56") and len(digits) >= 10:
                digits = digits[2:]
            if len(digits) == 9 and digits.startswith("9"):
                tel_fmt = f"+56{digits}"
                if tel_fmt not in telefonos_limpios:
                    telefonos_limpios.append(tel_fmt)
            elif len(digits) == 8:
                tel_fmt = f"+569{digits}" if not digits.startswith("2") else f"+56{digits}"
                if tel_fmt not in telefonos_limpios:
                    telefonos_limpios.append(tel_fmt)

        # Priorizar móviles (+569)
        telefonos_ordenados = sorted(telefonos_limpios, key=lambda x: 0 if x.startswith("+569") else 1)
        result["telefonos"] = telefonos_ordenados
        result["telefono_principal"] = telefonos_ordenados[0] if telefonos_ordenados else None

        # 3. Extracción de Correos Electrónicos
        emails = re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', html_or_text)
        emails_filtrados = []
        for em in emails:
            em_low = em.lower()
            if not any(ign in em_low for ign in ["equifax", "datafinder", "example", "soporte", "transunion"]):
                if em_low not in emails_filtrados:
                    emails_filtrados.append(em_low)
        result["emails"] = emails_filtrados
        result["email_principal"] = emails_filtrados[0] if emails_filtrados else None

        # 4. Fecha de Nacimiento y Edad
        nac_match = re.search(r'(?:nacimiento|fecha\s*nac\.?)\s*[:\-]*\s*(\d{2}[/-]\d{2}[/-]\d{4})', clean_text, re.IGNORECASE)
        if nac_match:
            f_nac_str = nac_match.group(1).replace('-', '/')
            result["fecha_nacimiento"] = f_nac_str
            try:
                dt_nac = datetime.strptime(f_nac_str, "%d/%m/%Y")
                edad = datetime.now().year - dt_nac.year - ((datetime.now().month, datetime.now().day) < (dt_nac.month, dt_nac.day))
                result["edad"] = edad
            except Exception:
                pass

        # 5. Índice Socioeconómico (ISE / GSE)
        ise_match = re.search(r'\b(?:ISE|GSE|GRUPO SOCIOECON[OÓ]MICO)\s*[:\-]*\s*([A-E][1-3]?[a-c]?)\b', clean_text, re.IGNORECASE)
        if ise_match:
            result["ise"] = ise_match.group(1).upper()
        else:
            # Buscar mención aislada de ABC1 o C1a
            gse_simple = re.search(r'\b(ABC1|C1A|C1B|C2|C3|D|E)\b', clean_text)
            if gse_simple:
                result["ise"] = gse_simple.group(1).upper()

        # 6. Dirección y Comuna
        dir_match = re.search(r'(?:direcci[oó]n|domicilio)\s*[:\-]*\s*([^,\n\r]+?)(?:,|\s+comuna|\s+ciudad|\s+regi[oó]n|\.|$)', clean_text, re.IGNORECASE)
        if dir_match:
            d = dir_match.group(1).strip()
            if len(d) > 4 and "no registra" not in d.lower():
                result["direccion"] = d.title()

        com_match = re.search(r'\bcomuna\s*[:\-]*\s*([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+?)(?:,|\s+ciudad|\s+regi[oó]n|\.|$)', clean_text, re.IGNORECASE)
        if com_match:
            c = com_match.group(1).strip()
            if len(c) > 3:
                result["comuna"] = c.title()

        return result

    def enrich_rut(
        self,
        rut: str,
        prospect_id: Optional[int] = None,
        force: bool = False,
        inject_db: bool = True
    ) -> Dict[str, Any]:
        """
        Función central para enriquecer un RUT:
        1. Valida cuota (< 100) y RUT antes de abrir el navegador.
        2. Abre navegador mediante Playwright de forma segura.
        3. Realiza la consulta y extrae teléfonos, correos e ISE.
        4. Registra la consulta en la tabla de cuotas.
        5. Inyecta los resultados en crm_database.db si inject_db=True.
        """
        # Validación Previa Estricta (Detiene antes de gastar recursos o cuota)
        self.validate_prospect_before_query(rut, prospect_id=prospect_id, force=force)

        rut_clean = clean_rut(rut)
        if '-' in rut_clean:
            cuerpo, dv = rut_clean.split('-', 1)
        else:
            cuerpo, dv = rut_clean[:-1], rut_clean[-1:]

        # MODO SIMULACIÓN / TEST
        # Si las credenciales son de prueba (contienen 'test' o 'tu_usuario'), se ejecuta en modo demo seguro
        if "tu_usuario" in self.username or "demo" in self.username or os.getenv("DATAFINDER_TEST_MODE") == "True":
            logger.info("DATAFINDER: Modo de prueba / simulación activo (credenciales de prueba detectadas).")
            simulated_data = {
                "rut": rut_clean,
                "rut_formateado": format_rut_miles(rut_clean),
                "encontrado": True,
                "nombre_completo": None,
                "fecha_nacimiento": "14/08/1982",
                "edad": 44,
                "ise": "ABC1",
                "telefonos": ["+56966779662", "+56987654321"],
                "telefono_principal": "+56966779662",
                "emails": ["prospecto.verificado@gmail.com"],
                "email_principal": "prospecto.verificado@gmail.com",
                "direccion": "Av. Apoquindo 4500",
                "comuna": "Las Condes",
                "ciudad": "Santiago",
                "estado_civil": "Casado",
                "simulado": True,
                "error": None
            }
            # Log de consumo
            self.quota_mgr.log_consumption(
                rut=rut_clean,
                prospect_id=prospect_id,
                exito=True,
                ise="ABC1",
                telefonos_cnt=2,
                emails_cnt=1,
                datos=simulated_data,
                observaciones="Consulta simulada de prueba"
            )
            if inject_db:
                self.inject_datafinder_results_to_crm(simulated_data, prospect_id=prospect_id)
            
            simulated_data["consultas_restantes_mes"] = self.quota_mgr.get_quota_status()["consultas_restantes"]
            return simulated_data

        # MODO PRODUCCIÓN REAL CON PLAYWRIGHT
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()

            try:
                # 1. Login
                self._login(page)

                # 2. Búsqueda
                html_report = self._execute_search(page, cuerpo, dv)

                # 3. Parseo estructurado
                parsed = self.parse_report_content(html_report, rut_clean)

                # 4. Registrar en cuota
                self.quota_mgr.log_consumption(
                    rut=rut_clean,
                    prospect_id=prospect_id,
                    exito=parsed["encontrado"],
                    ise=parsed.get("ise"),
                    telefonos_cnt=len(parsed.get("telefonos", [])),
                    emails_cnt=len(parsed.get("emails", [])),
                    datos=parsed,
                    observaciones=f"Equifax DataFinder | ISE: {parsed.get('ise')}"
                )

                # 5. Inyección a CRM
                if inject_db and parsed["encontrado"]:
                    self.inject_datafinder_results_to_crm(parsed, prospect_id=prospect_id)

                parsed["consultas_restantes_mes"] = self.quota_mgr.get_quota_status()["consultas_restantes"]
                return parsed

            except Exception as e:
                # Captura de pantalla para diagnóstico si falla
                try:
                    os.makedirs("scratch", exist_ok=True)
                    page.screenshot(path="scratch/datafinder_error.png")
                    logger.info("Captura de pantalla de error guardada en scratch/datafinder_error.png")
                except Exception:
                    pass
                raise e
            finally:
                context.close()
                browser.close()

    def inject_datafinder_results_to_crm(self, data: Dict[str, Any], prospect_id: Optional[int] = None) -> bool:
        """
        Inyecta los datos encontrados en crm_database.db actualizando el prospecto:
        - telefono: Si no tiene o si encontramos un celular verificado
        - email: Si no tiene
        - direccion y comuna
        - fecha_nacimiento
        - score_liquidez: Si ISE es ABC1 o C1a, se premia con alto puntaje
        - observaciones: Detalle del enriquecimiento
        """
        if not data.get("encontrado"):
            return False

        rut_clean = data.get("rut")
        tel_principal = data.get("telefono_principal")
        email_principal = data.get("email_principal")
        f_nac = data.get("fecha_nacimiento")
        direccion = data.get("direccion")
        comuna = data.get("comuna")
        ise = data.get("ise")

        try:
            import sqlite3
            conn = sqlite3.connect("data/crm_database.db")
            c = conn.cursor()

            # Buscar por ID o por RUT
            if prospect_id:
                c.execute("SELECT id, telefono, email, observaciones, score_liquidez FROM prospects WHERE id = ?", (prospect_id,))
            else:
                c.execute("SELECT id, telefono, email, observaciones, score_liquidez FROM prospects WHERE rut = ? OR rut = ?", 
                          (rut_clean, format_rut_miles(rut_clean)))
            
            row = c.fetchone()
            if not row:
                conn.close()
                return False

            pid, tel_actual, email_actual, obs_actual, score_actual = row

            updates = []
            params = []

            # 1. Teléfono: Si no tiene o está como 'SIN TEL' o encontramos celular +569
            if tel_principal:
                if not tel_actual or "SIN TEL" in str(tel_actual) or len(str(tel_actual)) < 8:
                    updates.append("telefono = ?")
                    params.append(tel_principal)
                elif tel_principal.startswith("+569") and not str(tel_actual).startswith("+569"):
                    updates.append("telefono = ?")
                    params.append(tel_principal)

            # 2. Email
            if email_principal and (not email_actual or "@" not in str(email_actual)):
                updates.append("email = ?")
                params.append(email_principal)

            # 3. Dirección / Comuna
            if direccion:
                dir_completa = f"{direccion}, {comuna}" if comuna else direccion
                updates.append("direccion = ?")
                params.append(dir_completa)
            if comuna:
                updates.append("ciudad = ?")
                params.append(comuna)

            # 4. Fecha de Nacimiento
            if f_nac:
                updates.append("fecha_nacimiento = ?")
                params.append(f_nac)

            # 5. Score y Observaciones
            obs_nota = f" [DataFinder Equifax: ISE {ise or 'N/D'} | {len(data.get('telefonos', []))} fono(s) | {len(data.get('emails', []))} email(s)]"
            nueva_obs = (obs_actual or "") + obs_nota
            updates.append("observaciones = ?")
            params.append(nueva_obs)

            if ise in ["ABC1", "C1A", "C1B"]:
                nuevo_score = max(score_actual or 0, 85 if ise == "ABC1" else 75)
                updates.append("score_liquidez = ?")
                params.append(nuevo_score)

            if updates:
                sql = f"UPDATE prospects SET {', '.join(updates)} WHERE id = ?"
                params.append(pid)
                c.execute(sql, params)
                conn.commit()
                logger.info(f"Prospecto ID {pid} ({rut_clean}) enriquecido con éxito en la base de datos.")

            conn.close()
            return True

        except Exception as e:
            logger.error(f"Error inyectando datos de DataFinder a la BD: {e}")
            return False


# ─── Función Convenience de Alto Nivel ───────────────────────────────────────

def enrich_prospect_datafinder(
    rut: str,
    prospect_id: Optional[int] = None,
    force: bool = False,
    inject_db: bool = True
) -> Dict[str, Any]:
    """
    Función de acceso directo para enriquecer un prospecto con Equifax DataFinder.
    Respeta la cuota de 100 consultas mensuales y valida el RUT antes de abrir el navegador.
    """
    connector = EquifaxDataFinderConnector()
    return connector.enrich_rut(rut=rut, prospect_id=prospect_id, force=force, inject_db=inject_db)


if __name__ == "__main__":
    print("=" * 60)
    print("TEST Y DIAGNOSTICO DEL CONECTOR EQUIFAX DATAFINDER")
    print("=" * 60)
    
    # 1. Verificar estado de cuota
    qm = DataFinderQuotaManager()
    st_q = qm.get_quota_status()
    print("\n[CUOTA] Estado de Cuota Mensual:")
    print(f"  - Periodo: {st_q['periodo']}")
    print(f"  - Consumidas: {st_q['consultas_consumidas']}/{st_q['limite_mensual']}")
    print(f"  - Consultas Restantes: {st_q['consultas_restantes']}")

    # 2. Prueba con RUT de ejemplo
    test_rut = "15.884.242-4"
    print(f"\n[TEST] Probando consulta controlada para RUT: {test_rut}...")
    try:
        resultado = enrich_prospect_datafinder(rut=test_rut, force=True, inject_db=False)
        print("\n[OK] Resultado estructurado obtenido:")
        print(json.dumps(resultado, indent=2, ensure_ascii=True))
    except Exception as err:
        print(f"\n[ERROR] Error durante la ejecucion: {err}")
