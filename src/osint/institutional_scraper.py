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

    def _verify_and_save(self, institucion: str, raw_text: str):
        """
        Usa IA para determinar de qué mes habla el reporte y resumirlo.
        Si corresponde a un mes antiguo ya ingresado, no lo duplica.
        """
        if not self.model:
            self.log_alert(institucion, "API Key de Gemini no configurada.")
            return

        prompt = f"""
        Eres un analista de datos financieros. Lee el siguiente reporte crudo extraído de la web de {institucion}:
        
        {raw_text[:8000]}
        
        OBJETIVO:
        1. Determina a qué MES y AÑO corresponde principalmente esta visión de mercado.
        2. Resume la visión corta (1 párrafo contundente).
        3. Escribe un resumen extendido estructurado por Renta Fija, Variable, Alternativos y Perfiles de Riesgo.
        
        Responde ÚNICAMENTE con un JSON válido con esta estructura:
        {{
            "periodo_detectado": "YYYY-MM",
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
            
            periodo = data.get("periodo_detectado")
            
            # Guardar en DB si no existe para ese periodo
            db = SessionLocal()
            exists = db.query(MarketVision).filter_by(institucion=institucion, periodo=periodo).first()
            if exists:
                logging.info(f"{institucion} ({periodo}): Ya existe en la base de datos. Saltando.")
            else:
                nueva_vision = MarketVision(
                    institucion=institucion,
                    periodo=periodo,
                    fuente="Web Scraper",
                    contenido_bruto=raw_text,
                    resumen_corto=data.get("resumen_corto"),
                    resumen_extendido=data.get("resumen_extendido")
                )
                db.add(nueva_vision)
                db.commit()
                logging.info(f"{institucion} ({periodo}): Guardado exitosamente en DB.")
            db.close()
            
        except Exception as e:
            self.log_alert(institucion, f"Error al procesar con IA: {e}")

    def scrape_sura(self):
        try:
            # Mock de extracción web (En prod: requests.get() -> BeautifulSoup)
            raw_text = "Reporte SURA Visión de Mercados Junio 2026. Recomendamos sobreponderar Renta Variable Internacional, especialmente EE.UU. sector tecnológico. Mantener duración corta en Renta Fija Local. Perfil conservador: 60% RF Corto Plazo. Agresivo: 70% RV Internacional."
            self._verify_and_save("SURA", raw_text)
        except Exception as e:
            self.log_alert("SURA", str(e))

    def scrape_banchile(self):
        try:
            raw_text = "Estrategia Banchile Inversiones Junio 2026. Visión neutral en Renta Variable Local (IPSA). Favoritos: SQM, Banco de Chile. Atractivo en Renta Fija Corporativa UF. Conservador: 80% RF Local. Agresivo: 50% RV Local, 50% RV Int."
            self._verify_and_save("Banchile", raw_text)
        except Exception as e:
            self.log_alert("Banchile", str(e))

    def scrape_santander(self):
        try:
            raw_text = "Visión de Mercados Santander Junio 2026. Proyectamos recortes de tasa TPM adicionales. Oportunidades en bonos corporativos locales de alta clasificación. En Renta Variable, neutrales con sesgo positivo en mercados desarrollados."
            self._verify_and_save("Santander", raw_text)
        except Exception as e:
            self.log_alert("Santander", str(e))

    def scrape_bci(self):
        try:
            raw_text = "Estrategia Mensual BCI Junio 2026. Mantenemos cautela ante volatilidad inflacionaria global. Preferimos activos alternativos y caja remunerada en pesos. Exposición acotada a acciones emergentes."
            self._verify_and_save("BCI", raw_text)
        except Exception as e:
            self.log_alert("BCI", str(e))

    def scrape_btg(self):
        try:
            raw_text = "Perspectivas BTG Pactual Junio 2026. Fuerte convicción en Small Caps de EE.UU. y Japón. A nivel local, vemos valor en utilities y banca. Riesgos concentrados en geopolítica. Portafolios agresivos deben maximizar exposición equity."
            self._verify_and_save("BTG Pactual", raw_text)
        except Exception as e:
            self.log_alert("BTG Pactual", str(e))

    def scrape_larrainvial(self):
        try:
            raw_text = "Estrategia de Inversiones LarrainVial Junio 2026. Enfoque en protección patrimonial. Renta Fija corporativa en UF es nuestra principal recomendación local. Infraponderamos Europa. Dólar se mantendría fuerte en el corto plazo."
            self._verify_and_save("LarrainVial", raw_text)
        except Exception as e:
            self.log_alert("LarrainVial", str(e))

    def run_all_scrapers(self) -> dict:
        logging.info("Iniciando OSINT Institucional y actualizando BD...")
        self.scrape_sura()
        self.scrape_banchile()
        self.scrape_santander()
        self.scrape_bci()
        self.scrape_btg()
        self.scrape_larrainvial()
        
        return {"alerts": self.alerts, "status": "Completado"}

if __name__ == "__main__":
    scraper = InstitutionalScraper()
    res = scraper.run_all_scrapers()
    print("Resultado:", res)
