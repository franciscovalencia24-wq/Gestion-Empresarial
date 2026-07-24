import streamlit as st
import os
import datetime
import sys
import importlib
import src.osint.market_data_engine
importlib.reload(src.osint.market_data_engine)
from src.osint.market_data_engine import MarketDataEngine

def render_infographic_generator_ui():
    st.title("📱 Generador de Infografías RRSS")
    st.info("Genera posteos automatizados para LinkedIn con datos macro y noticias de mercado.")
    st.write("")
    # Inicializar estado
    if "info_post_content" not in st.session_state:
        st.session_state.info_post_content = None
    if "info_img_file" not in st.session_state:
        st.session_state.info_img_file = None

    modo = st.radio("Selecciona el modo de generación:", ["🤖 Automático (RSS Reuters/Yahoo)", "🇨🇱 Automático (Noticias Chile)", "🔗 URL Personalizada", "🔍 Buscar Tema Libre", "⛏️ Especial: Cumbre SONAMI 2026", "📊 Reporte Cuantitativo (Producción Cobre)"])

    mode_arg = "auto"
    custom_input = None

    if modo == "🇨🇱 Automático (Noticias Chile)":
        mode_arg = "auto_chile"
    elif modo == "🔗 URL Personalizada":
        mode_arg = "url"
        custom_input = st.text_input("Ingresa la URL de la noticia (ej. DF, La Tercera, Bloomberg):")
    elif modo == "🔍 Buscar Tema Libre":
        mode_arg = "topic"
        custom_input = st.text_input("Ingresa el tema a buscar (ej. 'Caída de acciones de Apple hoy'):")
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
            
        with st.spinner("🤖 El motor OSINT está buscando datos y diseñando la infografía (Esto puede tomar 1-2 minutos)..."):
            try:
                engine = MarketDataEngine()
                post_content, img_file = engine.run_daily_routine(mode=mode_arg, custom_input=custom_input)
                
                st.session_state.info_post_content = post_content
                st.session_state.info_img_file = img_file
                st.success("✅ Generación completada con éxito.")
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                st.error(f"🚨 Error crítico en UI:\n{e}\n\nTraceback:\n{tb}")
    # Mostrar Resultados
    if st.session_state.info_post_content and st.session_state.info_img_file:
        st.markdown("---")
        st.markdown("### 📈 Resultados")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Texto del Post (LinkedIn)")
            st.code(st.session_state.info_post_content, language="markdown")
            st.info("💡 Consejo: Copia este texto y pégalo directamente en LinkedIn.")
            
        with col2:
            st.markdown("#### Infografía Generada")
            img_path = os.path.join("linkedin_posts", st.session_state.info_img_file)
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
                with open(img_path, "rb") as file:
                    btn = st.download_button(
                            label="📥 Descargar Imagen",
                            data=file,
                            file_name=os.path.basename(st.session_state.info_img_file),
                            mime="image/png"
                          )
            else:
                st.error("No se encontró el archivo de imagen generado.")
