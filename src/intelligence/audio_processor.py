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
        Este audio dura varios minutos y contiene múltiples detalles macroeconómicos, porcentajes, tendencias y opiniones analíticas.
        
        INSTRUCCIONES DE EXTRACCIÓN Y ANÁLISIS ESTRATÉGICO EXHAUSTIVO:
        1. **Transcripción Completa y Síntesis Detallada de Noticias de Mercado**: Extrae con MÁXIMO DETALLE y exhaustividad todos los hechos comentados sobre bolsas internacionales (S&P 500, NASDAQ, Nikkei, Europa, IPSA), decisiones o expectativas sobre la tasa de interés de la FED/BCCh, inflación, tipo de cambio (USD/CLP) y materias primas (Cobre, Petróleo, Oro). No resumas en 2 líneas; detalla cada tema.
        2. **Eventos y Causas Reales**: Describe con precisión qué datos económicos o anuncios gatillaron estos movimientos (ej: reporte NFP de empleo en EE.UU., datos de actividad económica Imacec/IPC en Chile, resultados corporativos, discurso del Presidente de la FED).
        3. **Implicancias Patrimoniales y Consejos de Inversión por Clase de Activo**: Explica en profundidad las recomendaciones para Renta Fija (depósitos a plazo, bonos soberanos/corporativos), Renta Variable (acciones chilenas vs internacionales) y Ahorro Previsional Voluntario (APV / Multifondos A, B, C, D, E).
        4. **Frases Clave y Citas Textuales**: Incluye 3 a 5 frases textuales o reflexiones clave dictadas en la grabación.
        
        Genera un informe altamente detallado, rico en datos numéricos y conceptos financieros, en formato Markdown extenso para que el generador de infografías y publicaciones disponga de todo el material necesario.
        """
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)
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
