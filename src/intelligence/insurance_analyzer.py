import os
import base64
import filetype
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class InsurancePolicyAnalyst:
    """
    Analista de Pólizas de Seguro (Vida, Salud, Oncológico, etc).
    Lee PDFs extensos y extrae el resumen de costos, beneficios y letra chica.
    """
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            # flash es excelente para lectura rápida de documentos largos (hasta 1M tokens)
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                temperature=0.1, 
                google_api_key=self.api_key
            )
        else:
            self.llm = None

    def analyze_policy(self, file_bytes: bytes, filename: str) -> dict:
        if not self.llm:
            raise Exception("Falta GOOGLE_API_KEY")

        print(f"[InsuranceAnalyst] Analizando póliza: {filename}")
        
        # Determinar mime_type
        kind = filetype.guess(file_bytes)
        mime_type = kind.mime if kind else "application/pdf"
        
        content_parts = []
        
        prompt = """
        Eres un Abogado y Actuario experto en Seguros en Chile.
        He adjuntado el documento completo de una póliza de seguro (puede ser vida, salud, oncológico, APV, vehículos o general).
        
        Tu trabajo es leer atentamente el contrato y extraer EXACTAMENTE la siguiente información clave, ignorando la burocracia comercial. 
        Si un dato no existe, responde "No especificado".
        
        ESTRUCTURA OBLIGATORIA DE LA RESPUESTA:
        
        **TIPO DE SEGURO Y COMPAÑÍA:** [Ej: Seguro Complementario de Salud - MetLife]
        **NÚMERO DE PÓLIZA:** [Si lo encuentras]
        **PRIMA MENSUAL/ANUAL:** [Costo que paga el cliente]
        **CAPITAL ASEGURADO O TOPE MÁXIMO:** [Ej: UF 500, USD 100.000]
        **DEDUCIBLE:** [Ej: UF 50 por evento]
        
        **BENEFICIOS CLAVE:**
        - [Beneficio 1]
        - [Beneficio 2]
        
        **EXCLUSIONES CRÍTICAS (La Letra Chica):**
        - [Lo que NO cubre]
        - [Enfermedades preexistentes, plazos de carencia, etc.]
        
        **COMENTARIO DEL ASESOR (Opcional):** [Si notas algo inusualmente malo o bueno en esta póliza, menciónalo aquí brevemente].
        """
        
        content_parts.append({"type": "text", "text": prompt})
        
        if mime_type.startswith("text/"):
            try:
                text_content = file_bytes.decode('utf-8', errors='ignore')
                content_parts.append({"type": "text", "text": f"\n\nCONTENIDO DE LA PÓLIZA:\n{text_content}"})
            except:
                pass
        else:
            file_b64 = base64.b64encode(file_bytes).decode("utf-8")
            if mime_type == "application/pdf" or mime_type.startswith("image/"):
                content_parts.append({
                    "type": "media" if mime_type == "application/pdf" else "image_url",
                    "mime_type": mime_type,
                    "data": file_b64,
                } if mime_type == "application/pdf" else {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{file_b64}"}
                })

        try:
            message = HumanMessage(content=content_parts)
            response = self.llm.invoke([message])
            return response.content
        except Exception as e:
            raise Exception(f"Error analizando póliza: {str(e)}")

    def analyze_cmf_coberturas(self, tipo_seguro: str, coberturas: str) -> str:
        if not self.llm:
            return "Análisis IA no disponible (Falta GOOGLE_API_KEY)"
            
        if not coberturas or len(coberturas.strip()) < 10:
            return "Información insuficiente para análisis detallado."
            
        prompt = f"""
        Eres un Abogado y Actuario experto en Seguros en Chile.
        Te entregaré las cláusulas técnicas extraídas del portal CMF (Conoce Tu Seguro) para una póliza.
        
        TIPO DE SEGURO PRINCIPAL: {tipo_seguro}
        CLÁUSULAS TÉCNICAS (Letra Chica):
        {coberturas}
        
        Tu objetivo es traducir esta jerga técnica en un "Resumen Comercial y Diagnóstico" corto y directo (máximo 4-5 líneas) para un Asesor Financiero.
        
        ESTRUCTURA DE RESPUESTA REQUERIDA (Responde solo esto):
        - **Diagnóstico:** [¿Es una cobertura robusta, básica, o tiene vacíos importantes?]
        - **Cubre:** [Lo más importante que cubre]
        - **Falta/Alerta:** [Lo que NO cubre según las cláusulas, o vacíos típicos de este tipo de seguros que el cliente debería contratar aparte].
        - **Oportunidad Comercial:** [¿Qué producto le podrías hacer up-sell o cross-sell basado en esto? (ej: "Ofrecer Seguro Catastrófico de Salud", "Ofrecer Sismo")].
        """
        
        try:
            message = HumanMessage(content=[{"type": "text", "text": prompt}])
            response = self.llm.invoke([message])
            return response.content
        except Exception as e:
            return f"Error en IA: {str(e)}"
