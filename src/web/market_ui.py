import streamlit as st
import os
import json
import datetime
from src.intelligence.market_researcher import MarketResearcherAgent

def render_market_ui():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0f172a 0%, #334155 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px;'>
        <h1 style='margin:0; font-size: 2.2rem; color: white;'>🌍 Inteligencia de Mercado Autónoma</h1>
        <p style='margin:10px 0 0 0; opacity: 0.9; font-size: 1.1rem;'>Vigilancia competitiva profunda y búsqueda de nichos abandonados.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Directorio para guardar historial de reportes
    _PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    reports_dir = os.path.join(_PROJECT_ROOT, "data", "market_reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Control del Agente")
        st.info("El Agente buscará automáticamente en la web, leerá noticias de la competencia y extraerá tendencias.")
        
        if st.button("🚀 Ejecutar Investigación Manual", type="primary", use_container_width=True):
            with st.spinner("🕵️‍♂️ El agente está buscando en la web..."):
                agent = MarketResearcherAgent()
                try:
                    report_text = agent.generate_weekly_report()
                    
                    # Guardar reporte
                    filename = f"reporte_{datetime.date.today().strftime('%Y-%m-%d')}.json"
                    filepath = os.path.join(reports_dir, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump({"date": str(datetime.date.today()), "content": report_text}, f, ensure_ascii=False, indent=2)
                    
                    st.success("✅ Reporte generado y guardado exitosamente.")
                    st.session_state.current_market_report = report_text
                except Exception as e:
                    st.error(f"⚠️ El Agente se topó con un problema de conexión (API sobrecargada). Intenta de nuevo en unos minutos. Detalles: {e}")
                
    with col2:
        st.subheader("📜 Brief Semanal de Mercado")
        
        # Verificar si hay que ejecutarlo automáticamente (Lunes)
        today = datetime.date.today()
        auto_filename = f"reporte_{today.strftime('%Y-%m-%d')}.json"
        auto_filepath = os.path.join(reports_dir, auto_filename)
        
        if today.weekday() == 0 and not os.path.exists(auto_filepath): # 0 es Lunes
            with st.spinner("Lunes detectado: Ejecutando reporte semanal automáticamente..."):
                agent = MarketResearcherAgent()
                try:
                    report_text = agent.generate_weekly_report()
                    with open(auto_filepath, 'w', encoding='utf-8') as f:
                        json.dump({"date": str(today), "content": report_text}, f, ensure_ascii=False, indent=2)
                    st.session_state.current_market_report = report_text
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ No se pudo generar el reporte automático porque el servidor IA está ocupado. Usa el botón manual más tarde.")

        # Helper para limpiar el texto antes de renderizar
        def get_clean_text(val):
            if isinstance(val, list):
                if len(val) > 0 and isinstance(val[0], dict):
                    val = val[0].get('text', str(val))
            val = str(val)
            # Limpiar si es string de lista
            if val.startswith("[{'type':") or val.startswith('[{"type":'):
                import re
                match = re.search(r"['\"]text['\"]:\s*['\"](.*)['\"]\s*\}", val, re.DOTALL)
                if match:
                    val = match.group(1).encode('utf-8').decode('unicode_escape')
            return val

        # Mostrar historial o el actual
        if "current_market_report" in st.session_state:
            st.markdown(get_clean_text(st.session_state.current_market_report))
        else:
            # Intentar cargar el último reporte
            files = sorted(os.listdir(reports_dir), reverse=True)
            if files:
                last_file = os.path.join(reports_dir, files[0])
                try:
                    with open(last_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    st.caption(f"Último reporte generado: {data['date']}")
                    st.markdown(get_clean_text(data['content']))
                except:
                    st.write("No hay reportes previos.")
            else:
                st.write("Presiona 'Ejecutar Investigación' para generar tu primer reporte de mercado.")
