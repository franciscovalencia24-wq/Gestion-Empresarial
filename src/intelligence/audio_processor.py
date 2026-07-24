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
        
        try:
            import filetype
            kind = filetype.guess(audio_bytes)
            mime_type = kind.mime if kind else "audio/mp3"
        except Exception:
            mime_type = "audio/mp3" 
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

def process_market_audio(audio_bytes: bytes, filename: str = "reporte_mercado.mp3") -> str:
    """
    Procesa reportes de audio de mercado (ej: audio semanal/diario enviado por Principal Financial Group, Santander, o Corredoras)
    utilizando Gemini Multimodal para extraer transcripción completa, eventos clave, implicancias patrimoniales y contexto macro.
    """
    load_dotenv(override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY no configurada."

    try:
        print(f"[AudioProcessor] Procesando reporte de audio de mercado ({filename})...")
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        try:
            import filetype
            kind = filetype.guess(audio_bytes)
            mime_type = kind.mime if kind else "audio/mp3"
        except Exception:
            mime_type = "audio/mp3"
        if mime_type.startswith("video/"):
            mime_type = mime_type.replace("video/", "audio/")
        elif mime_type == "application/octet-stream":
            if filename.lower().endswith(".m4a"): mime_type = "audio/m4a"
            elif filename.lower().endswith(".wav"): mime_type = "audio/wav"
            elif filename.lower().endswith(".ogg"): mime_type = "audio/ogg"
            else: mime_type = "audio/mp3"

        prompt = f"""
        Eres el Economista Jefe y Estratega Senior de Inversiones de ALTUS AI y FV Asesorías e Inversiones.
        Has recibido el reporte oficial de audio enviado por la institución financiera (ej. Principal Financial Group / Corredora / Banco): '{filename}'.
        
        INSTRUCCIONES DE EXTRACCIÓN Y ANÁLISIS ESTRATÉGICO:
        1. **Transcripción y Síntesis de Noticias de Mercado**: Extrae con máxima precisión los hechos clave mencionados sobre bolsas internacionales (S&P 500, NASDAQ, Nikkei, IPSA, Europa), tasa de interés de la FED/BCCh, inflación, dólar observador (USD/CLP) y materias primas (Cobre, Petróleo, Oro).
        2. **Eventos y Causas Reales**: ¿Qué datos económicos o anuncios causaron estos movimientos? (ej: datos de empleo en EE.UU., IPC Chile, declaraciones de los bancos centrales).
        3. **Implicancias Patrimoniales y Consejos de Inversión**: ¿Cómo debe actuar un cliente de banca privada o patrimonial? ¿Qué recomendaciones se desprenden para Renta Fija (depósitos, bonos), Renta Variable (acciones) y Ahorro Previsional Voluntario (APV)?
        4. **Frases Clave del Audio**: Cita 2 o 3 reflexiones textuales de alto valor dictadas en el reporte.
        
        Genera un informe completo, denso en datos duros y estructurado en Markdown para ser consumido por el motor de diseño de infografías.
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
        return f"Error procesando audio de mercado: {str(e)}"
