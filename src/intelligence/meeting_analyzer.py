import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

class MeetingAnalyst:
    """
    Analista de Reuniones de Video (Teams/Zoom).
    Utiliza el SDK directo de Google Generative AI para subir archivos pesados 
    usando la API File API y luego genera el análisis multimodal.
    """
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
        else:
            self.model = None

    def analyze_meeting(self, temp_video_path: str, client_name: str) -> str:
        if not self.model:
            raise Exception("Falta GOOGLE_API_KEY")

        print(f"[MeetingAnalyst] Subiendo video a Google File API: {temp_video_path}")
        
        # Subir archivo usando la API de archivos de Gemini (ideal para videos pesados)
        video_file = genai.upload_file(path=temp_video_path)
        
        # Esperar a que el video termine de procesarse en Google (state=ACTIVE)
        print("[MeetingAnalyst] Video subido. Esperando procesamiento en servidor...")
        while video_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            raise Exception("El procesamiento del video falló en el servidor de Google.")

        print("\n[MeetingAnalyst] Video listo. Generando Acta de Reunión...")
        
        prompt = f"""
        Eres el Asistente Ejecutivo y Analista de Negocios de FV Inversiones.
        Has asistido a la reunión grabada adjunta con el cliente {client_name}.
        
        Por favor, mira y escucha atentamente toda la reunión. Presta atención tanto al audio de la conversación como a cualquier presentación, Excel o documento que se comparta en pantalla.
        
        Tu tarea es redactar DOS SECCIONES CLARAMENTE SEPARADAS en formato Markdown:
        
        # 📝 Acta Interna (Solo para el Asesor)
        
        ## 1. Resumen Ejecutivo
        (Resumen de 2-3 párrafos sobre de qué trató la reunión, el tono general).
        
        ## 2. Ejemplos y Casos Explicados
        (Si se mostraron ejemplos hipotéticos de planes, rentabilidades o simulaciones, enuméralos aquí. Aclara que son SOLO EJEMPLOS EDUCATIVOS y no compromisos de venta).
        
        ## 3. Acuerdos Reales y Próximos Pasos (Next Steps)
        (Enumera ÚNICAMENTE las tareas que el cliente explícitamente solicitó o acordó que se hicieran, y las tareas reales del asesor).
        
        ## 4. Análisis Psicológico y No Verbal
        (Observaciones sobre dudas, entusiasmo u objeciones del cliente. Recomendaciones de abordaje).

        ---
        
        # 📧 Borrador de Correo para el Cliente
        
        (Redacta un correo electrónico formal, cercano y profesional dirigido al cliente {client_name}. 
        Resume los puntos clave de la reunión y los próximos pasos reales acordados. 
        NO incluyas análisis psicológico ni menciones que eres una IA. 
        El asunto del correo debe ir en la primera línea como: "Asunto: Resumen de nuestra reunión - FV Inversiones".)
        """
        
        try:
            response = self.model.generate_content(
                [video_file, prompt],
                request_options={"timeout": 600} # Las llamadas a video toman mucho tiempo
            )
            
            # Limpiar archivo de Google Cloud después de usarlo
            genai.delete_file(video_file.name)
            
            return response.text
        except Exception as e:
            try:
                genai.delete_file(video_file.name)
            except:
                pass
            raise Exception(f"Error generando análisis de reunión: {str(e)}")
