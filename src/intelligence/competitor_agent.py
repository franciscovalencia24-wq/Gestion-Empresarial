from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import base64

class CompetitorAgent:
    """
    Agente especializado en analizar propuestas de la competencia (PDFs, Imágenes) 
    y generar contra-argumentos (Benchmarking).
    """
    def __init__(self):
        # Usamos flash-latest que tiene capacidades multimodales excelentes y rápidas
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

    def generate_counter_proposal(self, file_bytes: bytes, mime_type: str, prospect_name: str) -> str:
        """
        Lee el archivo de la competencia y devuelve una tabla comparativa y un guion de objeciones.
        """
        encoded_file = base64.b64encode(file_bytes).decode("utf-8")
        
        prompt_text = f"""
        Eres un Analista Financiero Senior y experto en Wealth Management de 'FV Asesorías e Inversiones'.
        Se te acaba de entregar una propuesta comercial / folleto de un fondo mutuo, APV o seguro de la COMPETENCIA para el cliente {prospect_name}.

        TU MISIÓN:
        1. Leer el documento adjunto y extraer las "letras chicas", cobros ocultos, TAC (Tasa Anual de Costos), y restricciones de liquidez.
        2. Comparar esta propuesta contra el estándar de 'FV Asesorías e Inversiones' (nuestra propuesta de valor: arquitectura abierta, asesoría proactiva, comisiones transparentes, optimización tributaria).
        3. Redactar un reporte estructurado y contundente para que el asesor humano pueda rebatirle al cliente.

        FORMATO DE SALIDA (Usa Markdown hermoso):
        ### 🔍 Análisis de la Propuesta de la Competencia
        (Resumen de lo que es el producto y quién lo emite)

        ### 🚩 Red Flags y Costos Ocultos
        (Lista de viñetas con los costos, penalizaciones o falta de flexibilidad descubiertas)

        ### 📊 Tabla Comparativa: Competencia vs FV Asesorías
        (Tabla Markdown comparando 3-4 atributos clave como Costos, Asesoría, Independencia, Flexibilidad)

        ### 💬 Guion de Objeciones (Talking Points)
        (3 puntos clave hablados en primera persona, listos para que el asesor se los diga al cliente por teléfono o reunión para ganar el negocio).
        """
        
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": prompt_text,
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{encoded_file}"},
                },
            ]
        )

        try:
            print("[CompetitorAgent] Analizando propuesta de la competencia...")
            response = self.llm.invoke([message])
            return response.content
        except Exception as e:
            return f"❌ Error al procesar el archivo de la competencia: {str(e)}"
