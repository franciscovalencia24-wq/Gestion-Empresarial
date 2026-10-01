import os
import shutil
import datetime
import logging
from PyPDF2 import PdfReader
from src.agents.macro_analyst import MacroAnalystAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MarketConsensusEngine")

class MarketConsensusEngine:
    def __init__(self):
        self.raw_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "market_research_raw")
        self.processed_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "market_research_processed")
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        self.analyst = MacroAnalystAgent()

    def _extract_text_from_pdf(self, pdf_path):
        text = ""
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            logger.error(f"Error extrayendo texto de PDF {pdf_path}: {e}")
        return text

    def _determine_institution(self, filename):
        """Intenta deducir la institucion desde el nombre del archivo (generado por IMAP)."""
        filename_lower = filename.lower()
        instituciones = {
            "larrainvial": "LarrainVial",
            "jpmorgan": "JP Morgan",
            "morganstanley": "Morgan Stanley",
            "btg": "BTG Pactual",
            "banchile": "Banchile Inversiones",
            "credicorp": "Credicorp Capital",
            "santander": "Santander",
            "bci": "BCI",
            "scotiabank": "Scotiabank"
        }
        for key, name in instituciones.items():
            if key in filename_lower:
                return name
        return "Institución Desconocida"

    def process_pending_files(self):
        """Procesa todos los archivos TXT y PDF en el directorio raw."""
        logger.info("Iniciando procesamiento de reportes de mercado pendientes...")
        
        periodo_actual = datetime.date.today().strftime('%Y-%m')
        
        if not os.path.exists(self.raw_dir):
            return
            
        files = os.listdir(self.raw_dir)
        if not files:
            logger.info("No hay archivos pendientes por procesar.")
            return

        for filename in files:
            filepath = os.path.join(self.raw_dir, filename)
            
            if not os.path.isfile(filepath):
                continue
                
            logger.info(f"Procesando: {filename}")
            institucion = self._determine_institution(filename)
            text_content = ""
            
            try:
                if filename.endswith(".pdf"):
                    text_content = self._extract_text_from_pdf(filepath)
                elif filename.endswith(".txt"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        text_content = f.read()
                else:
                    logger.warning(f"Formato no soportado: {filename}")
                    continue
                
                if len(text_content.strip()) < 50:
                    logger.warning(f"Contenido muy corto en {filename}, ignorando.")
                    continue
                
                # Ingestar en la DB a través del Agente Macro
                logger.info(f"Ingestando reporte de {institucion} al agente macro...")
                resultado = self.analyst.ingest_document_vision(
                    institucion=institucion,
                    periodo=periodo_actual,
                    text_content=text_content
                )
                
                logger.info(f"Resultado de ingesta para {filename}: Exitoso")
                
                # Mover a procesados
                shutil.move(filepath, os.path.join(self.processed_dir, filename))
                
            except Exception as e:
                logger.error(f"Error procesando {filename}: {e}")

if __name__ == "__main__":
    engine = MarketConsensusEngine()
    engine.process_pending_files()
