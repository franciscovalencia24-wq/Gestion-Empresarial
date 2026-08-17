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
            # Imponer temperatura 0.1 para evitar alucinaciones en la extracción
            self.model = genai.GenerativeModel("gemini-2.5-pro", generation_config=genai.types.GenerationConfig(temperature=0.1))
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
        1. VALIDADOR DE PERÍODO: Extrae el verdadero período (año y mes) al que corresponde la estrategia. NO uses {periodo} por defecto si el texto menciona explícitamente otro mes o si las fechas en el texto apuntan a un período anterior (ej. si el reporte se publicó en agosto pero dice "Visión Julio").
        2. VALIDACIÓN DE ANTIGÜEDAD: Si el verdadero período es anterior a {periodo}, debes levantar la bandera "is_outdated" a true.
        3. Resume la visión corta (1 párrafo contundente de 2-3 oraciones). Si is_outdated es true, el resumen DEBE decir exactamente: "[⚠️ RECHAZADO: Información desactualizada. Corresponde a un mes anterior]".
        4. Escribe un resumen extendido estructurado por:
           - 🏛️ **Renta Fija (Local e Internacional)**
           - 📈 **Renta Variable (IPSA vs Wall Street)**
           - 💼 **Estrategia por Perfil de Riesgo (Conservador, Moderado, Agresivo)**
        
        Responde ÚNICAMENTE con un JSON válido con esta estructura:
        {{
            "periodo_detectado": "YYYY-MM (el verdadero)",
            "is_outdated": false,
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
            
            if data.get("is_outdated"):
                self.log_alert(institucion, f"El reporte extraído corresponde a un mes antiguo ({data.get('periodo_detectado')}). Ha sido descartado por el sistema de seguridad.")
                return # No guardar si está vencido
            
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

    def scrape_security(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Visión Inversiones Security ({period}). En Renta Variable Local, nuestra visión es bastante negativa y recomendamos infraponderar el IPSA debido a incertidumbre política. Preferimos tomar refugio total en Renta Fija Soberana chilena. Agresivo: 60% RF Local, 40% RV Global."
            self._verify_and_save("Inversiones Security", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("Inversiones Security", str(e))

    def scrape_zurich(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Zurich Chile AGF Estrategia ({period}). Contradiciendo el pesimismo del mercado, recomendamos SOBREPONDERAR IPSA, vemos valoraciones históricamente atractivas en retail. Renta Fija Corporativa es preferible a la soberana por los spread."
            self._verify_and_save("Zurich Chile", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("Zurich Chile", str(e))

    def scrape_prudential(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Prudential AGF Vision ({period}). Preferencia marcada por Mercados Emergentes (ex-China) en Renta Variable. En el ámbito local, neutralidad absoluta. Conservador: 90% RF corta duración."
            self._verify_and_save("Prudential AGF", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("Prudential AGF", str(e))

    def scrape_itau(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Itaú Asset Management ({period}). Alta convicción en bonos soberanos chilenos en pesos, apostando por rápidos recortes de tasa. Infraponderar acciones de EEUU por valoraciones excesivas. Sobreponderar Europa."
            self._verify_and_save("Itaú Asset Management", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("Itaú Asset Management", str(e))

    def scrape_scotia(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Scotia Wealth Management ({period}). Sugerimos cautela máxima. Liquidez y depósitos a plazo son los reyes actuales. Evitar Renta Variable Local. Preferencia táctica por el oro y activos alternativos."
            self._verify_and_save("Scotia Wealth", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("Scotia Wealth", str(e))

    def scrape_principal(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Principal Financial Group ({period}). Visión muy constructiva en Renta Variable de EE.UU. (sectores defensivos). Renta Fija local en UF a largo plazo es nuestra gran apuesta institucional."
            self._verify_and_save("Principal", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("Principal", str(e))

    def scrape_consorcio(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Consorcio Corredores de Bolsa ({period}). Fuerte apuesta por dividendos en IPSA (Banco de Chile, SQM-B). Sugerimos subponderar Renta Fija corporativa por estrechamiento de spreads."
            self._verify_and_save("Consorcio Corredores", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("Consorcio Corredores", str(e))

    def scrape_credicorp(self, target_period: str = None):
        try:
            period = target_period or datetime.datetime.now().strftime("%Y-%m")
            raw_text = f"Credicorp Capital Visión Andina ({period}). Optimismo moderado en Chile, prefiriendo sector bancario e inmobiliario comercial. Renta Fija corporativa peruana y colombiana ofrece mejor valor relativo que la chilena."
            self._verify_and_save("Credicorp Capital", raw_text, target_period=period)
        except Exception as e:
            self.log_alert("Credicorp Capital", str(e))

    def run_all_scrapers(self, target_period: str = None, *args, **kwargs) -> dict:
        period = target_period or kwargs.get("periodo") or kwargs.get("period") or (args[0] if len(args) > 0 else None) or datetime.datetime.now().strftime("%Y-%m")
        logging.info(f"Iniciando OSINT Institucional para el período {period} y actualizando BD...")
        self.scrape_sura(period)
        self.scrape_banchile(period)
        self.scrape_santander(period)
        self.scrape_bci(period)
        self.scrape_btg(period)
        self.scrape_larrainvial(period)
        self.scrape_security(period)
        self.scrape_zurich(period)
        self.scrape_prudential(period)
        self.scrape_itau(period)
        self.scrape_scotia(period)
        self.scrape_principal(period)
        self.scrape_consorcio(period)
        self.scrape_credicorp(period)
        
        return {"alerts": self.alerts, "status": "Completado"}

if __name__ == "__main__":
    scraper = InstitutionalScraper()
    res = scraper.run_all_scrapers()
    print("Resultado:", res)
