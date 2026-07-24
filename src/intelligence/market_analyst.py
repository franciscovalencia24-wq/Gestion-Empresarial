"""
Módulo UI de Inteligencia de Mercado (CMF) — BD SENIOR
Renderiza el análisis de la industria de fondos mutuos chilena con datos reales
de la tabla cmf_market_trends o con datos de ejemplo si el ingestor no se ha ejecutado.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from src.database.connection import SessionLocal
import src.database.models as models
from src.analytics.market_science import get_market_summary, analyze_sector_performance


def _scale_billones(v):
    if not v: return 0.0
    # Industria total es ~80 Billones de CLP.
    if v >= 1_000_000_000_000:       # Datos en Pesos (ej: 80,000,000,000,000)
        return v / 1_000_000_000_000
    elif v >= 1_000_000_000:         # Datos en Miles de Pesos M$ (ej: 80,000,000,000)
        return v / 1_000_000_000
    elif v >= 1_000_000:             # Datos en Millones MM$ (ej: 80,000,000)
        return v / 1_000_000
    else:                            # Datos parseados mal por pandas (ej: 80,000.0)
        return v / 1_000

def _fmt_trillones(v):
    """Formatea un valor en CLP a Billones chilenos (millones de millones)."""
    if not v:
        return "$ 0.0 Billones CLP"
    t = _scale_billones(v)
    return f"$ {t:,.2f} Billones CLP".replace(",", ".")


def render_market_intelligence():
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
                    padding: 28px; border-radius: 15px; margin-bottom: 25px; color: white;'>
            <h1 style='color: white; margin: 0; font-size: 2.2em; font-weight: 900;'>
                🔬 Inteligencia de Mercado (CMF)
            </h1>
            <p style='color: #94a3b8; margin: 8px 0 0 0; font-size: 1.1em;'>
                Análisis de la Industria de Fondos Mutuos — Datos Oficiales CMF Chile
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📈 Tendencias CMF", "🎯 Matriz de Oponentes (War Room)"])
    
    with tab2:
        render_competitor_matrix()

    with tab1:
        # ── Carga de datos ────────────────────────────────────────────────────────
        with st.spinner("Cargando datos de mercado..."):
            try:
                summary     = get_market_summary()
                performance = analyze_sector_performance()
            except Exception as e:
                st.error(f"⚠️ Error crítico al cargar datos: {e}")
                st.info("Ejecuta el **Ingestor CMF** en la Bóveda de Ingesta para activar datos reales.")
                return

        # Aviso si estamos en modo offline
        data_source = summary.get("data_source", "live_db")
        if "offline" in data_source or "sample" in data_source:
            st.warning(
                "📊 **Modo Demostración:** Mostrando datos de referencia de la industria (2024). "
                "Para datos reales, ejecuta el **Ingestor CMF** en la Bóveda de Ingesta.",
                icon="⚠️"
            )

        last_update = summary.get("last_update", "N/D")

        # ── KPIs principales ──────────────────────────────────────────────────────
        st.markdown(f"### 📊 Métricas Clave de la Industria <span style='font-size: 0.5em; color: gray;'>Última actualización CMF: {last_update}</span>", unsafe_allow_html=True)
        top_agfs = summary.get("top_agfs", pd.DataFrame())

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "💰 AUM Total Industria",
            _fmt_trillones(summary.get("total_aum")),
            help="Total de activos bajo administración en fondos mutuos (FFMM) en Chile."
        )
        c2.metric(
            "🏆 Líder de Mercado",
            top_agfs.iloc[0]["administradora"] if not top_agfs.empty else "N/D",
            help="Administradora con mayor patrimonio administrado."
        )
        c3.metric(
            "📈 Mejor Retorno (Tipo)",
            f"{performance.iloc[0]['avg_retorno']:.2f}% mensual" if not performance.empty else "N/D",
            help="Tipo de fondo con mayor retorno promedio mensual."
        )
        c4.metric(
            "🔢 Top 20 representan",
            f"{(top_agfs['aum'].sum() / summary['total_aum'] * 100):.0f}% del AUM" if not top_agfs.empty and summary.get('total_aum') else "N/D",
            help="Concentración de mercado en las principales AGF."
        )

        st.markdown("---")

        # ── Top AGFs + Evolución partícipes ──────────────────────────────────────
        col_left, col_right = st.columns([1, 2])

        with col_left:
            st.markdown("### 🏆 Top 20 AGF por Patrimonio")
            if not top_agfs.empty:
                top_agfs_display = top_agfs.copy()
                top_agfs_display["aum"] = top_agfs_display["aum"].apply(
                    lambda v: f"$ {_scale_billones(v):.2f} Bill.".replace(".", ",", 1)
                )
                top_agfs_display.columns = ["Administradora", "AUM"]
                st.dataframe(top_agfs_display, hide_index=True, use_container_width=True)
            else:
                st.info("Sin datos de AGF disponibles.")

        with col_right:
            st.markdown("### 📈 Evolución de Partícipes en la Industria")
            growth_df = summary.get("growth", pd.DataFrame())
            if not growth_df.empty:
                # Crear columna período legible
                growth_df["periodo"] = growth_df["ano"].astype(str) + "-" + growth_df["mes"].astype(str).str.zfill(2)
                fig_growth = px.area(
                    growth_df,
                    x="periodo",
                    y="total_participes",
                    title="Crecimiento de Inversores — Industria FFMM",
                    color_discrete_sequence=["#00B140"],
                    labels={"periodo": "Período", "total_participes": "N° Partícipes"}
                )
                fig_growth.update_layout(
                    template="plotly_white",
                    showlegend=False,
                    xaxis_tickangle=-45,
                    margin=dict(l=0, r=0, t=40, b=60)
                )
                st.plotly_chart(fig_growth, use_container_width=True)

        st.markdown("---")

        # ── Performance por tipo de fondo ─────────────────────────────────────────
        st.markdown("### 📊 Retorno Mensual Promedio por Tipo de Fondo")
        if not performance.empty:
            colors = ["#00B140" if v > 0.8 else "#f59e0b" if v > 0.4 else "#ef4444"
                      for v in performance["avg_retorno"]]
            fig_perf = go.Figure(go.Bar(
                x=performance["tipo_fondo"],
                y=performance["avg_retorno"],
                marker_color=colors,
                text=[f"{v:.2f}%" for v in performance["avg_retorno"]],
                textposition="outside",
            ))
            fig_perf.update_layout(
                title="Retorno Promedio Mensual por Categoría de Fondo",
                xaxis_title="Tipo de Fondo",
                yaxis_title="Retorno Mensual (%)",
                template="plotly_white",
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0),
            )
            st.plotly_chart(fig_perf, use_container_width=True)
        else:
            st.info("Sin datos de performance disponibles.")

        # ── CTA ────────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.info(
            "💡 **Tip Estratégico:** Para sincronizar datos reales de la CMF, "
            "ve a **🏰 Bóveda de Ingesta → Pestaña CMF** y ejecuta el ingestor.",
            icon="ℹ️"
        )


def render_competitor_matrix():
    st.markdown("### 🎯 Matriz de Inteligencia Competitiva (War Room)")
    st.write("Registro histórico y profundo de debilidades y estrategias de la competencia.")
    c1, c2 = st.columns([3, 1])
    with c1:
        if st.button("🕵️‍♂️ Ejecutar Deep OSINT Competitivo (Todos)", type="primary", use_container_width=True):
            with st.spinner("Analizando competencia (Deep OSINT v2)... Esto tomará varios minutos."):
                from src.intelligence.market_researcher import MarketResearcherAgent
                agent = MarketResearcherAgent()
                res = agent.run_deep_osint()
                st.success(res)
    with c2:
        with st.popover("➕ Añadir Competidor"):
            nuevo_comp = st.text_input("Nombre (ej. Fintual):")
            if st.button("Agregar solo nombre", use_container_width=True):
                if nuevo_comp:
                    db = SessionLocal()
                    if not db.query(models.CompetitorProfile).filter_by(nombre=nuevo_comp).first():
                        db.add(models.CompetitorProfile(nombre=nuevo_comp, tipo="Institución Financiera"))
                        db.commit()
                        st.success(f"{nuevo_comp} agregado.")
                        st.rerun()
                    else:
                        st.warning("Ya existe.")
                    db.close()
            
            st.divider()
            nueva_url = st.text_input("Ingestar desde URL (ej. https://...):")
            if st.button("🕵️‍♂️ Analizar con IA", use_container_width=True):
                if nueva_url:
                    with st.spinner("Leyendo web y estructurando con IA..."):
                        from src.intelligence.market_researcher import MarketResearcherAgent
                        agent = MarketResearcherAgent()
                        res = agent.ingest_competitor_from_url(nueva_url)
                        if "✅" in res:
                            st.success(res)
                            st.rerun()
                        else:
                            st.error(res)
    
    st.markdown("---")
    
    db = SessionLocal()
    competidores = db.query(models.CompetitorProfile).all()
    db.close()
    
    if competidores:
        opciones = {c.nombre: c for c in competidores}
        seleccion = st.selectbox("Selecciona un Oponente para abrir su Dossier", [""] + list(opciones.keys()))
        
        if seleccion:
            comp = opciones[seleccion]
            
            # Modo Oscuro Dossier Card
            import textwrap
            dossier_html = textwrap.dedent(f"""
            <div style="background-color: #1e1e1e; color: #ffffff; padding: 25px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-top: 15px;">
                <h2 style="color: #ff4b4b; margin-top: 0;">🎯 {comp.nombre}</h2>
                <p style="opacity: 0.8; font-size: 0.9rem;">Tipo: {comp.tipo or 'Desconocido'} | Última actualización: {comp.updated_at.strftime('%Y-%m-%d') if comp.updated_at else 'N/A'}</p>
                <hr style="border-color: #333;">
                
                <h4 style="color: #4CAF50;">✅ Pros (Fortalezas)</h4>
                <p style="margin-left: 15px; font-size: 1rem;">{comp.pros or 'N/D'}</p>
                
                <h4 style="color: #f44336;">❌ Contras (Debilidades y Fricción)</h4>
                <p style="margin-left: 15px; font-size: 1rem;">{comp.contras or 'N/D'}</p>
                
                <h4 style="color: #2196F3;">🚀 Estrategias Comunicadas</h4>
                <p style="margin-left: 15px; font-size: 1rem;">{comp.estrategias or 'N/D'}</p>
                
                <h4 style="color: #FFC107;">🎯 Público Objetivo</h4>
                <p style="margin-left: 15px; font-size: 1rem;">{comp.publico_objetivo or 'N/D'}</p>
                
                <div style="background-color: #2d2d2d; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #FFC107;">
                    <h4 style="color: #FFC107; margin-top: 0;">💎 Nichos Abandonados (Nuestra Ventana de Ataque)</h4>
                    <p style="margin-bottom: 0;">{comp.nichos_abandonados or 'N/D'}</p>
                </div>
            </div>
            """)
            st.markdown(dossier_html, unsafe_allow_html=True)
    else:
        st.info("La base de datos de competidores está vacía. Presiona el botón de 'Deep OSINT' para inicializar.")

if __name__ == "__main__":
    render_market_intelligence()
