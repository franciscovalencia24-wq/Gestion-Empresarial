import os
import io
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

def process_client_audio(audio_bytes: bytes) -> str:
    """
    Toma bytes de audio (desde st.audio_input), lo sube a Gemini y genera
    una transcripción y extracción de Insights (Neurociencia).
    """
    load_dotenv(override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY no configurada."

    try:
        print("[AudioProcessor] Codificando audio a Base64...")
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        import filetype
        kind = filetype.guess(audio_bytes)
        mime_type = kind.mime if kind else "audio/mp3" 
        # Si detecta contenedor mp4/m4a a veces lo lee como video, forzamos que lo trate como audio
        if mime_type.startswith("video/"):
            mime_type = mime_type.replace("video/", "audio/")
        prompt = """
        Eres un Analista Psicológico y Estratega Patrimonial.
        Analiza esta nota de voz dictada por un asesor sobre su cliente.
        
        ENTREGABLE (Markdown):
        1. **Transcripción y Perfil Patrimonial:** Resume de qué trata la nota. DEBES extraer y listar todos los datos duros financieros mencionados: edad, montos, instituciones, y EXPLICITAMENTE cualquier ahorro mensual o aportes a APV (ej. descuentos por planilla).
        2. **Perfil Psicológico / Prejuicios:** ¿Qué se infiere del cliente? ¿A qué le teme? ¿Qué le gusta?
        3. **🎁 Oportunidad Oculta:** (Error de Predicción Positivo). Sugiere 1 cosa que el asesor podría hacer por el cliente para sorprenderlo gratamente basándote en lo que se dijo en el audio.
        """
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "media",
                    "mime_type": mime_type,
                    "data": audio_b64,
                },
            ]
        )
        
        response = llm.invoke([message])
        return response.content

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error procesando audio: {str(e)}"
