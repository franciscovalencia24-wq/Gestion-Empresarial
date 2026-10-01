import streamlit as st

def render_showcase(set_nav_callback):
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 15px; margin-bottom: 30px; color: white; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.4); border: 1px solid #D4AF37;'>
            <h1 style='color: white; margin: 0; font-size: 2.8em; font-weight: 900;'>🌟 Catálogo de Soluciones ALTUS CORE</h1>
            <p style='color: #e2e8f0; margin: 15px 0 0 0; font-size: 1.2em;'>Demostrador comercial interactivo de las capacidades tecnológicas de cara al cliente.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Inyectar CSS para las tarjetas
    st.markdown("""
    <style>
    .showcase-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .showcase-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: #D4AF37;
    }
    .card-title {
        color: #1e293b;
        font-weight: 800;
        font-size: 1.2em;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .card-desc {
        color: #64748b;
        font-size: 0.95em;
        line-height: 1.5;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    pilares = {
        "🎯 Visión Integral 360°": [
            {
                "icon": "📑", "name": "Reporte Patrimonial 360°",
                "desc": "El pilar central de ALTUS CORE. Una ficha KYC (Know Your Customer o Conoce a tu Cliente) hiper-detallada que consolida todo tu panorama financiero: estructuras societarias, vehículos de inversión, flujos de liquidez, y herederos en una sola matriz interactiva. El verdadero punto de partida para una gestión patrimonial de alto nivel, permitiendo un control, transparencia y orquestación total de tu legado familiar.",
                "action": "Ver Reporte",
                "nav_args": ("👤 1. Gestión de Clientes",)
            }
        ],
        "🏛️ Recuperación de Capital & Eficiencia Fiscal": [
            {
                "icon": "💸", "name": "Identificación de Excesos Provisionales (DPE)",
                "desc": "Identifica y gestiona la recuperación de fondos pagados en exceso a las AFP. A través de un cruce paramétrico, transformamos ineficiencias administrativas del pasado en capital líquido y disponible hoy.",
                "action": "Simular Excesos",
                "nav_args": ("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Rescate Excesos AFP (DPE)") 
            },
            {
                "icon": "⚖️", "name": "Motor de Reliquidación Automática",
                "desc": "Simula decenas de escenarios de rescate y rentabilidad para identificar matemáticamente el punto exacto de neutralidad fiscal, liberando liquidez atrapada que el mercado tradicional suele dejar sobre la mesa.",
                "action": "Calcular Reliquidación",
                "nav_args": ("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Reliquidación")
            }
        ],
        "🧮 Inteligencia de Inversiones": [
            {
                "icon": "🏢", "name": "Valuación Integral Multi-Activo",
                "desc": "Integra tus activos inmobiliarios y financieros en una única matriz de riesgo. Calcula en tiempo real tu Cap Rate, ROE y flujos de caja apalancados, permitiendo contrastar el costo de oportunidad frente a fondos líquidos.",
                "action": "Evaluar Portafolios",
                "nav_args": ("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Simulador Real Estate")
            },
            {
                "icon": "🏛️", "name": "Estrategia Previsional Optimizada",
                "desc": "Determina la ruta fiscalmente más eficiente (Régimen A o B) para tu Ahorro Previsional. Nuestro algoritmo proyecta tu curva de ingresos para recomendar el monto exacto que maximiza subsidios y reduce impuestos futuros.",
                "action": "Optimizar APV",
                "nav_args": ("📊 2. Análisis de Inversiones", "sub_nav_analisis", "APV Inteligente")
            },
            {
                "icon": "💰", "name": "Comparador Crédito vs Inversión",
                "desc": "Calcula matemáticamente si es más eficiente prepagar una deuda o invertir ese capital, comparando las tasas de interés reales contra retornos ajustados por inflación, asegurando la decisión financiera óptima.",
                "action": "Comparar Alternativas",
                "nav_args": ("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Comparador Crédito vs Inversión")
            },
            {
                "icon": "📈", "name": "Auditor de Portafolios",
                "desc": "Escaneo milimétrico de los fondos mutuos de tu portafolio actual (competencia) para detectar ineficiencias y altas comisiones (TAC) disfrazadas, proyectando el impacto de ese capital a lo largo del tiempo.",
                "action": "Auditar Fondos",
                "nav_args": ("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Auditor de Portafolio")
            },
            {
                "icon": "💼", "name": "Inversión Patrimonial y Cuenta 2 AFP",
                "desc": "Estructura portafolios de liquidez con beneficio sucesorio (hasta 4.000 UF exentas de herencia según Art. 72 D.L. 3.500) y exención de 30 UTM en ganancias de capital, respaldado por PRINCIPAL.",
                "action": "Simular Inversión",
                "nav_args": ("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Retiro Cuenta 2")
            }
        ],
        "🤖 Asesoría Inteligente (IA)": [
            {
                "icon": "🧠", "name": "Asesor Patrimonial Senior (Omni)",
                "desc": "Copiloto conversacional avanzado, impulsado por IA, con contexto total de tu portafolio. Capaz de cruzar la normativa de la CMF y leyes tributarias para generar diagnósticos en tiempo real basados en datos en vivo y alertas de mercado.",
                "action": "Iniciar Chat",
                "nav_args": ("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Asesor Patrimonial Senior (Omni)")
            }
        ],
        "🔒 Privacidad & Seguridad Institucional": [
            {
                "icon": "📄", "name": "Acuerdo de Confidencialidad (NDA)",
                "desc": "El pilar de nuestra relación. Operamos bajo estrictos contratos legales de confidencialidad (NDA) para garantizar que toda tu información patrimonial, familiar y societaria se mantenga bajo un secreto profesional inviolable en todo momento.",
                "action": "Ver Política",
                "nav_args": None
            },
            {
                "icon": "🛡️", "name": "Seguridad Informática Avanzada",
                "desc": "Tu información viaja y se almacena bajo protocolos de encriptación de grado bancario. Con controles de acceso ultra-restringidos y arquitectura Cloud dedicada, tus datos permanecen totalmente blindados contra amenazas externas o comerciales.",
                "action": "Ver Arquitectura",
                "nav_args": None
            }
        ]
    }

    # RENDERIZAR PILARES
    for pilar_name, tools in pilares.items():
        st.markdown(f"<h3 style='color: #0f172a; margin-top: 30px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;'>{pilar_name}</h3>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Crear filas de 2 o 3 columnas
        cols = st.columns(len(tools) if len(tools) <= 3 else 2)
        
        for idx, tool in enumerate(tools):
            col = cols[idx % len(cols)]
            with col:
                st.markdown(f"""
                <div class="showcase-card">
                    <div class="card-title">{tool['icon']} {tool['name']}</div>
                    <div class="card-desc">{tool['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # El botón de Streamlit se dibuja debajo de la tarjeta visual para manejar el estado en backend
                if tool.get('nav_args'):
                    st.button(f"{tool['action']} ➡️", key=f"btn_showcase_{tool['name']}", width="stretch", type="primary", on_click=set_nav_callback, args=tool['nav_args'])
                else:
                    st.button(f"{tool['action']} ➡️", key=f"btn_showcase_{tool['name']}", width="stretch", type="secondary", disabled=True)

    st.markdown("---")
    
    st.markdown("<h3 style='color: #0f172a; margin-top: 30px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;'>📘 Brochure Comercial ALTUS CORE</h3>", unsafe_allow_html=True)
    
    import os
    import sys
    import streamlit.components.v1 as components
    from src.utils.pdf_generator import generate_pdf_from_html
    
    brochure_path = "dist/brochure_comercial_altus.html"
    
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.markdown("Visualiza y exporta el material comercial institucional con todos los pilares y oferta de valor.")
    with col2:
        if st.button("🔄 Actualizar / Reconstruir Brochure", width="stretch"):
            with st.spinner("Reconstruyendo brochure..."):
                if "scripts.build_commercial_brochure" in sys.modules:
                    del sys.modules["scripts.build_commercial_brochure"]
                from scripts.build_commercial_brochure import build_brochure
                build_brochure()
                st.success("Brochure actualizado.")
                st.rerun()

    if not os.path.exists(brochure_path):
        with st.spinner("Construyendo brochure comercial inicial..."):
            if "scripts.build_commercial_brochure" in sys.modules:
                del sys.modules["scripts.build_commercial_brochure"]
            from scripts.build_commercial_brochure import build_brochure
            build_brochure()
            
    if os.path.exists(brochure_path):
        with open(brochure_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        st.markdown("**Vista Previa:**")
        components.html(html_content, height=800, scrolling=True)
        
        st.markdown("### ⬇️ Exportar Brochure")
        bcol1, bcol2 = st.columns(2)
        with bcol1:
            st.download_button(
                label="🌐 Descargar HTML (Interactivo & Offline)",
                data=html_content,
                file_name="Brochure_Comercial_ALTUS_CORE.html",
                mime="text/html",
                width="stretch"
            )
            
        with bcol2:
            try:
                pdf_bytes = generate_pdf_from_html(html_content)
                if pdf_bytes:
                    st.download_button(
                        label="📄 Descargar PDF (Impresión)",
                        data=pdf_bytes,
                        file_name="Brochure_Comercial_ALTUS_CORE.pdf",
                        mime="application/pdf",
                        width="stretch",
                        type="primary"
                    )
                else:
                    st.warning("El motor PDF arrojó una respuesta vacía.")
            except Exception as e:
                st.error(f"Error renderizando PDF: {str(e)}")

    st.markdown("<div style='text-align: center; color: #888; font-size: 0.9rem; margin-top: 50px;'>Nota: Al lanzar una herramienta, serás redirigido directamente al módulo operativo.</div>", unsafe_allow_html=True)
