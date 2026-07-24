import os
import json
import pdfplumber
import io
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class LegalReportParser:
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            # gemini-2.5-flash is great for long text and fast extraction
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                temperature=0.1, 
                google_api_key=self.api_key,
                model_kwargs={"response_mime_type": "application/json"}
            )
        else:
            self.llm = None

    def parse_pdfs(self, file_bytes_list: list) -> dict:
        """
        Envía los PDFs completos directamente a Gemini, quien procesa texto e imágenes (OCR nativo),
        y extrae los datos de la sociedad en JSON estructurado.
        """
        if not self.llm:
            raise Exception("No hay API KEY de Google configurada.")

        import base64
        b64_pdfs = [base64.b64encode(fb).decode('utf-8') for fb in file_bytes_list]

        # 2. Prompt estructurado para extraer JSON
        prompt = f"""
        Eres un Abogado Corporativo experto en Chile. A continuación te proporciono un Informe de Sociedad / Informe Legal en formato PDF adjunto.
        Tu tarea es extraer los datos clave en el formato JSON estricto que se muestra abajo.
        
        Si algún dato no está presente, usa el valor null o déjalo vacío (""), pero siempre respeta la estructura JSON.
        Trata de inferir las fechas en formato 'YYYY-MM-DD'. Si no es posible, pon el texto crudo.

        Estructura requerida (responde SOLO el JSON válido):
        {{
            "fecha_constitucion": "YYYY-MM-DD",
            "notaria_constitucion": "Nombre de la Notaría y Ciudad",
            "repertorio_constitucion": "Número de Repertorio",
            "fecha_ultima_vigencia": "YYYY-MM-DD",
            "socios": [
                {{
                    "rut": "Rut del socio",
                    "nombre": "Nombre del socio",
                    "porcentaje_participacion": número float (ej. 90.0),
                    "capital_aportado": número float (si está en pesos, ej 9000000.0, sino 0.0)
                }}
            ],
            "representantes": [
                {{
                    "rut": "Rut del representante",
                    "nombre": "Nombre del representante",
                    "poderes_restricciones": "Resumen de las restricciones, ej. 'Sólo delegar parcialmente sus facultades'"
                }}
            ]
        }}
        """

        try:
            content = [{"type": "text", "text": prompt}]
            for pdf_b64 in b64_pdfs:
                content.append({"type": "image_url", "image_url": {"url": f"data:application/pdf;base64,{pdf_b64}"}})
            message = HumanMessage(content=content)
            response = self.llm.invoke([message])
            raw_content = response.content
            
            # Limpiar posibles bloques Markdown (```json ... ```)
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
                if raw_content.endswith("```"):
                    raw_content = raw_content[:-3]
            elif raw_content.startswith("```"):
                raw_content = raw_content[3:]
                if raw_content.endswith("```"):
                    raw_content = raw_content[:-3]

            parsed_data = json.loads(raw_content.strip())
            return parsed_data
        except Exception as e:
            raise Exception(f"Error procesando el informe con IA: {str(e)}")
