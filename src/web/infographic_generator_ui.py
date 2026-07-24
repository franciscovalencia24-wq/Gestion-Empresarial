import streamlit as st
import os
import datetime
import sys
import importlib
import src.osint.market_data_engine
importlib.reload(src.osint.market_data_engine)
from src.osint.market_data_engine import MarketDataEngine
from src.intelligence.audio_processor import process_market_audio

def render_infographic_generator_ui():
    st.title("📱 Generador de Infografías y Contenido RRSS")
    st.info("Crea infografías 4K, carruseles y publicaciones automatizadas para LinkedIn a partir de noticias o reportes de audio de mercado.")
    st.write("")
    
    # Inicializar estado de sesión
    if "info_post_content" not in st.session_state:
        st.session_state.info_post_content = None
    if "info_img_file" not in st.session_state:
        st.session_state.info_img_file = None
    if "audio_extracted_text" not in st.session_state:
        st.session_state.audio_extracted_text = None

    modo = st.radio("Selecciona la fuente de contenido:", [
        "🤖 Automático Global (RSS Reuters/Yahoo)",
        "🇨🇱 Automático Nacional (Noticias Chile)",
        "🎙️ Procesar Audio de Mercado (Ej: Reporte de Principal / Corredora)",
        "🔗 URL Personalizada (DF, La Tercera, Bloomberg)",
        "🔍 Buscar Tema Libre",
        "⛏️ Especial: Cumbre SONAMI 2026",
        "📊 Reporte Cuantitativo (Producción Cobre)"
    ])

    mode_arg = "auto"
    custom_input = None
    uploaded_audio = None

    if modo == "🇨🇱 Automático Nacional (Noticias Chile)":
        mode_arg = "auto_chile"
    elif modo == "🎙️ Procesar Audio de Mercado (Ej: Reporte de Principal / Corredora)":
        mode_arg = "audio"
        st.markdown("#### 🎙️ Carga de Reporte de Audio de Mercado")
        st.caption("Carga la nota de voz o archivo de audio (MP3, M4A, WAV, OGG) enviado por **Principal Financial Group**, un Banco o Corredora de Bolsa. La IA procesará el audio, extraerá los datos duros y generará la infografía con la línea gráfica institucional.")
        
        uploaded_audio = st.file_uploader(
            "📁 Selecciona o arrastra tu archivo de audio:",
            type=["mp3", "wav", "m4a", "ogg", "mpeg", "aac", "mp4"],
            key="uploader_market_audio"
        )
        
        if uploaded_audio is not None:
            audio_bytes = uploaded_audio.read()
            st.audio(audio_bytes, format=f"audio/{uploaded_audio.name.split('.')[-1]}")
            st.success(f"🎵 Audio cargado exitosamente: **{uploaded_audio.name}** ({len(audio_bytes)/1024:.1f} KB)")
            
    elif modo == "🔗 URL Personalizada (DF, La Tercera, Bloomberg)":
        mode_arg = "url"
        custom_input = st.text_input("Ingresa la URL de la noticia (ej. DF, La Tercera, Bloomberg):")
    elif modo == "🔍 Buscar Tema Libre":
        mode_arg = "topic"
        custom_input = st.text_input("Ingresa el tema a buscar (ej. 'Decisión de Tasas de la FED hoy'):")
    elif modo == "⛏️ Especial: Cumbre SONAMI 2026":
        mode_arg = "sonami"
        st.info("Este modo buscará las últimas noticias, proyecciones e insights relacionados con la Cumbre SONAMI 2026 y la industria minera chilena para generar un reporte y post enfocado en inversiones patrimoniales.")
    elif modo == "📊 Reporte Cuantitativo (Producción Cobre)":
        mode_arg = "cochilco"
        st.info("Generará un análisis duro sobre la producción de cobre por faena, extrayendo estadísticas recientes y relacionándolas con el escenario macro global.")

    if st.button("🚀 Generar Infografía y Post", type="primary", use_container_width=True):
        if (mode_arg == "url" or mode_arg == "topic") and not custom_input:
            st.error("Por favor, ingresa un valor en la caja de texto para continuar.")
            return

        if mode_arg == "audio":
            if uploaded_audio is None:
                st.error("Por favor, carga un archivo de audio antes de presionar el botón de generación.")
                return
            
            with st.spinner("🎙️ Gemini 2.5 procesando y escuchando el reporte de audio de mercado..."):
                try:
                    audio_bytes = uploaded_audio.getvalue() if hasattr(uploaded_audio, "getvalue") else uploaded_audio.read()
                    extracted_text = process_market_audio(audio_bytes, filename=uploaded_audio.name)
                    if "Error" in extracted_text and len(extracted_text) < 120:
                        st.error(f"🚨 Falló el procesamiento de audio: {extracted_text}")
                        return
                    
                    st.session_state.audio_extracted_text = extracted_text
                    custom_input = extracted_text
                except Exception as ex_aud:
                    st.error(f"🚨 Error al leer el archivo de audio: {ex_aud}")
                    return

        with st.spinner("🤖 El motor de Inteligencia y Diseño está creando la infografía 4K y el post de LinkedIn..."):
            try:
                engine = MarketDataEngine()
                post_content, img_file = engine.run_daily_routine(mode=mode_arg, custom_input=custom_input)
                
                st.session_state.info_post_content = post_content
                st.session_state.info_img_file = img_file
                st.success("✅ Infografía y publicación generadas con éxito.")
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                st.error(f"🚨 Error crítico en UI:\n{e}\n\nTraceback:\n{tb}")

    # MOSTRAR RESULTADOS
    if st.session_state.audio_extracted_text:
        with st.expander("📝 Ver Transcripción e Insights Extraídos del Audio", expanded=False):
            st.markdown(st.session_state.audio_extracted_text)

    if st.session_state.info_post_content and st.session_state.info_img_file:
        st.markdown("---")
        st.markdown("### 📈 Resultados Generados")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Texto del Post (LinkedIn)")
            st.code(st.session_state.info_post_content, language="markdown")
            st.info("💡 Consejo: Copia este texto y pégalo directamente en tu perfil o página de empresa en LinkedIn.")
            
        with col2:
            st.markdown("#### Infografía Diseñada (4K / SVG Vectorial)")
            img_path = os.path.join("linkedin_posts", st.session_state.info_img_file)
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
                with open(img_path, "rb") as file:
                    btn = st.download_button(
                        label="📥 Descargar Imagen 4K (.png)",
                        data=file,
                        file_name=os.path.basename(st.session_state.info_img_file),
                        mime="image/png"
                    )
            else:
                st.error("No se encontró el archivo de imagen generado.")
