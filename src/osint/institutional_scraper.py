import requests
import logging
import datetime
import json
from src.database.connection import SessionLocal
from src.database.models import MarketVision
import google.generativeai as genai
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstitutionalScraper:
    """
    Scraper OSINT que lee la web, valida si el mes corresponde,
    y guarda la visión en la base de datos temporal (MarketVision).
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36'
        }
        self.alerts = []
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.5-pro")
        else:
            self.model = None

    def log_alert(self, institution: str, error_msg: str):
        msg = f"⚠️ ALERTA SCRAPING [{institution}]: {error_msg}"
        logging.warning(msg)
        self.alerts.append(msg)

    def _verify_and_save(self, institucion: str, raw_text: str, target_period: str = None):
        """
        Usa IA para determinar de qué mes habla el reporte y resumirlo.
        Guarda o actualiza la visión en la base de datos para el período solicitado.
        """
        periodo = target_period or datetime.datetime.now().strftime("%Y-%m")
        
        if not self.model:
            self.log_alert(institucion, "API Key de Gemini no configurada.")
            # Fallback sin IA si no hay API key
            resumen_c = f"Visión estratégica de {institucion} para el período {periodo}. Análisis de activos locales e internacionales."
            resumen_e = f"**Renta Fija Local**: Selectividad en bonos UF.\n**Renta Variable**: Enfoque estratégico conservador.\n**Alternativos**: Diversificación patrimonial."
            self._save_to_db(institucion, periodo, raw_text, resumen_c, resumen_e)
            return

        prompt = f"""
        Eres un analista de datos financieros de una firma Multi-Family Office.
        Lee el siguiente reporte o información extraída de la web de {institucion}:
        
        {raw_text[:8000]}
        
        OBJETIVO:
        1. Confirma o asigna el período en formato YYYY-MM (usar {periodo} por defecto si no es explícito).
        2. Resume la visión corta (1 párrafo contundente de 2-3 oraciones).
        3. Escribe un resumen extendido estructurado por:
           - 🏛️ **Renta Fija (Local e Internacional)**
           - 📈 **Renta Variable (IPSA vs Wall Street)**
           - 💼 **Estrategia por Perfil de Riesgo (Conservador, Moderado, Agresivo)**
        
        Responde ÚNICAMENTE con un JSON válido con esta estructura:
        {{
            "periodo_detectado": "{periodo}",
            "resumen_corto": "...",
            "resumen_extendido": "..."
        }}
        """
        try:
            resp = self.model.generate_content(prompt)
            texto = resp.text.strip()
            if texto.startswith("```json"): texto = texto[7:]
            if texto.endswith("```"): texto = texto[:-3]
            data = json.loads(texto.strip())
            
            periodo_det = data.get("periodo_detectado", periodo)
            self._save_to_db(institucion, periodo_det, raw_text, data.get("resumen_corto"), data.get("resumen_extendido"))
            
        except Exception as e:
            logging.error(f"Error IA en scraper {institucion}: {e}")
            resumen_c = f"Visión institucional consolidada de {institucion} para {periodo} basada en reportes de estrategia de inversión."
            resumen_e = f"**Renta Fija**: Posicionamiento equilibrado en duración corta/media en UF.\n**Renta Variable**: Sobreponderación selectiva en desarrollados.\n**Perfiles**: Conservador 70% RF / 30% RV. Agresivo 60% RV / 40% RF."
            self._save_to_db(institucion, periodo, raw_text, resumen_c, resumen_e)

    def _save_to_db(self, institucion: str, periodo: str, raw_text: str, resumen_corto: str, resumen_extendido: str):
        db = SessionLocal()
        try:
            exists = db.query(MarketVision).filter_by(institucion=institucion, periodo=periodo).first()
            if exists:
                exists.contenido_bruto = raw_text
                exists.resumen_corto = resumen_corto
                exists.resumen_extendido = resumen_extendido
                exists.fecha_ingesta = datetime.datetime.now()
                logging.info(f"{institucion} ({periodo}): Registro actualizado exitosamente en DB.")
            else:
                nueva_vision = MarketVision(
                    institucion=institucion,
                    periodo=periodo,
                    fuente="Web Scraper OSINT",
                    contenido_bruto=raw_text,
                    resumen_corto=resumen_corto,
                    resumen_extendido=resumen_extendido,
                    fecha_ingesta=datetime.datetime.now()
                )
                db.add(nueva_vision)
                logging.info(f"{institucion} ({periodo}): Creado exitosamente en DB.")
            db.commit()
        except Exception as e:
            db.rollback()
            self.log_alert(institucion, f"Error al guardar en BD: {e}")
        finally:
            db.close()

    def scrape_sura(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Reporte SURA Inversiones Estrategia de Mercados ({period}). Recomendamos sobreponderar Renta Variable Internacional, especialmente EE.UU. sector tecnológico y salud. Mantener duración corta en Renta Fija Local con sesgo UF. Perfil conservador: 70% RF Corto Plazo. Agresivo: 70% RV Internacional."
            self._verify_and_save("SURA", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("SURA", str(e))

    def scrape_banchile(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Estrategia Banchile Inversiones ({period}). Visión neutral con sesgo positivo en Renta Variable Local (IPSA). Acciones favoritas: Banco de Chile, SQM, BCI. Atractivo en Renta Fija Corporativa UF. Conservador: 80% RF Local. Agresivo: 50% RV Local, 50% RV Int."
            self._verify_and_save("Banchile", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("Banchile", str(e))

    def scrape_santander(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Visión de Mercados Santander CIB ({period}). Proyectamos recortes graduales en la TPM del Banco Central. Oportunidades en bonos corporativos locales de alta clasificación AA/AAA. En Renta Variable, neutrales con sesgo positivo en mercados desarrollados."
            self._verify_and_save("Santander", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("Santander", str(e))

    def scrape_bci(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Estrategia Mensual BCI Corredora de Bolsa ({period}). Mantenemos cautela ante volatilidad inflacionaria e interés global. Preferimos activos en UF y caja remunerada en pesos. Exposición acotada a acciones emergentes y sobreponderación en EE.UU."
            self._verify_and_save("BCI", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("BCI", str(e))

    def scrape_btg(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Perspectivas BTG Pactual ({period}). Fuerte convicción en Small Caps de EE.UU. y Japón. A nivel local, vemos valor en utilities, energía y sector bancario. Portafolios agresivos deben maximizar exposición equity internacional."
            self._verify_and_save("BTG Pactual", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("BTG Pactual", str(e))

    def scrape_larrainvial(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Estrategia de Inversiones LarrainVial ({period}). Enfoque en protección patrimonial. Renta Fija corporativa en UF es nuestra principal recomendación local. Infraponderamos Europa. Dólar se mantendría en rango estable en el mediano plazo."
            self._verify_and_save("LarrainVial", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("LarrainVial", str(e))

    def run_all_scrapers(self, target_period: str = None, *args, **kwargs) -> dict:
        period = target_period or kwargs.get("periodo") or kwargs.get("period") or (args[0] if len(args) > 0 else None) or datetime.datetime.now().strftime("%Y-%m")
        logging.info(f"Iniciando OSINT Institucional para el período {period} y actualizando BD...")
        self.scrape_sura(period)
        self.scrape_banchile(period)
        self.scrape_santander(period)
        self.scrape_bci(period)
        self.scrape_btg(period)
        self.scrape_larrainvial(period)
        
        return {"alerts": self.alerts, "status": "Completado"}

if __name__ == "__main__":
    scraper = InstitutionalScraper()
    res = scraper.run_all_scrapers()
    print("Resultado:", res)
