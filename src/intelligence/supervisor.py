import os
import glob
import time
import pandas as pd
from datetime import datetime
from src.ingestion.cartola_reader import CartolaReaderAgent
from src.intelligence.omni_advisor import OmniAdvisorAgent

class AgentSupervisor:
    """
    Controlador Autónomo (Agente Supervisor).
    Orquesta el flujo:
    1. Escanea cartolas nuevas en el sistema.
    2. Invoca al Lector de Cartolas para extraer datos.
    3. Invoca al OmniAdvisor para generar una propuesta.
    4. Guarda el reporte en el perfil del cliente.
    """
    def __init__(self):
        self.reader = CartolaReaderAgent()
        
        _PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.pdfs_dir = os.path.join(_PROJECT_ROOT, "data", "raw", "cartolas")
        self.reports_dir = os.path.join(_PROJECT_ROOT, "data", "processed", "reports")
        os.makedirs(self.pdfs_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    def run_autonomous_cycle(self):
        """
        Ejecuta un ciclo completo de supervisión:
        Encuentra PDFs de cartolas no procesadas y genera reportes patrimoniales.
        """
        logs = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Iniciando Ciclo de Supervisión Autónoma...")
        
        pdf_files = glob.glob(os.path.join(self.pdfs_dir, "*.pdf"))
        if not pdf_files:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 😴 No se encontraron nuevas cartolas para procesar.")
            return logs
            
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Se encontraron {len(pdf_files)} cartola(s). Iniciando delegación...")
        
        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            client_id = filename.split(".")[0] # Asumimos que el nombre del archivo es el RUT/ID
            
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📄 Analizando: {filename}")
            
            # 1. Extraer datos con Lector de Cartolas
            try:
                extraction = self.reader.extract_cartola_data(pdf_path)
                resumen = extraction.get("analisis_gemini", "Sin datos.")
            except Exception as e:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error en extracción de {filename}: {e}")
                continue
                
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Datos financieros extraídos. Derivando al OmniAdvisor...")
            
            # 2. Invocar OmniAdvisor con memoria del cliente
            advisor = OmniAdvisorAgent(client_id=client_id)
            prompt = f"Acabo de leer la cartola de este cliente. Aquí tienes el resumen financiero: {resumen}. Por favor, genera un análisis patrimonial y tributario proactivo de 3 párrafos, recomendando estrategias específicas de inversión o ahorro tributario."
            
            try:
                estrategia = advisor.ask(prompt)
            except Exception as e:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error generando estrategia para {filename}: {e}")
                continue
                
            # 3. Guardar el reporte
            report_path = os.path.join(self.reports_dir, f"reporte_{client_id}_{datetime.now().strftime('%Y%m%d')}.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"# Reporte Autónomo - Cliente {client_id}\n\n")
                f.write(f"## 1. Resumen de Cartola\n{resumen}\n\n")
                f.write(f"## 2. Estrategia Patrimonial (OmniAdvisor)\n{estrategia}\n")
                
            # Opcional: Mover el PDF a una carpeta "procesados" para no leerlo de nuevo
            procesados_dir = os.path.join(self.pdfs_dir, "procesados")
            os.makedirs(procesados_dir, exist_ok=True)
            os.rename(pdf_path, os.path.join(procesados_dir, filename))
            
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🏁 Reporte guardado con éxito para {client_id}.")
            
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 💤 Ciclo finalizado. El Supervisor vuelve a dormir.")
        return logs

if __name__ == "__main__":
    sup = AgentSupervisor()
    for log in sup.run_autonomous_cycle():
        print(log)
