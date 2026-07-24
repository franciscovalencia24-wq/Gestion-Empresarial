from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from fpdf import FPDF, HTMLMixin
import markdown
import os
import urllib.parse
import html

class PDF(FPDF, HTMLMixin):
    # Parche para Python 3.9+ donde html.unescape reemplazó a HTMLParser.unescape
    def unescape(self, s):
        return html.unescape(s)

class ExecutionAgent:
    """
    Agente encargado de la 'Ejecución Autónoma': 
    Pasar de la inteligencia analítica a la acción en el mundo real (PDFs y Emails).
    """
    def __init__(self):
        # Usamos gemini-flash-latest que funciona con la versión v1beta de tu máquina
        self.llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.3)
        self.chain = self.llm | StrOutputParser()

    def generate_pdf_report(self, md_content: str, output_filepath: str):
        """
        Convierte texto a un reporte PDF de forma segura (sin depender de HTMLMixin).
        """
        # Limpieza básica de Markdown
        text = md_content.replace("**", "").replace("#", "").replace("*", "-")
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Reporte Estratégico - FV Asesorías e Inversiones", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=11)
        
        # Codificar a latin-1 ignorando caracteres raros para evitar crasheos en FPDF básico
        for line in text.split('\n'):
            clean_line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, txt=clean_line)
            
        pdf.output(output_filepath)
        return output_filepath

    def generate_email_draft(self, prospect_name: str, strategy_text: str) -> dict:
        """
        Redacta el correo de seguimiento usando el contexto de la estrategia generada.
        Retorna un dict con 'subject', 'body' y el link 'mailto'.
        """
        prompt = f"""
        Actúa como un Wealth Manager de "FV Asesorías e Inversiones".
        Redacta el borrador de un correo electrónico breve, ejecutivo y empático para el cliente {prospect_name}.
        El objetivo es enviarle adjunta su nueva Propuesta Estratégica Patrimonial y agendar una llamada de 15 minutos.
        
        ESTRATEGIA PROPUESTA RECIENTEMENTE (Resumen):
        {strategy_text[:2000]}
        
        Reglas:
        - Tono: Profesional, directo, asesor experto.
        - Asunto: Atractivo y claro (máximo 7 palabras).
        - Saludo: "Estimado/a {prospect_name},"
        - Cuerpo: Máximo 3 párrafos cortos. Menciona 1 hallazgo numérico de la estrategia si aplica.
        - Llamado a la acción: Proponer una llamada de revisión.
        - Despedida: Equipo FV Asesorías.
        
        IMPORTANTE: Devuelve la respuesta EXACTAMENTE en este formato:
        ASUNTO: <tu asunto aquí>
        CUERPO: <tu cuerpo del correo aquí>
        """
        
        response_text = self.chain.invoke(prompt)
        content = response_text.strip()
        
        # Parsear asunto y cuerpo
        subject = "Propuesta Estratégica Patrimonial - FV Asesorías"
        body = content
        
        for line in content.split("\n"):
            if line.startswith("ASUNTO:"):
                subject = line.replace("ASUNTO:", "").strip()
            elif line.startswith("CUERPO:"):
                body = content.split("CUERPO:")[1].strip()
                break
                
        # Crear enlace mailto seguro
        subject_encoded = urllib.parse.quote(subject)
        body_encoded = urllib.parse.quote(body)
        mailto_link = f"mailto:?subject={subject_encoded}&body={body_encoded}"
        
        return {
            "subject": subject,
            "body": body,
            "mailto_link": mailto_link
        }
