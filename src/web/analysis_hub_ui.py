import streamlit as st
import os

import plotly.graph_objects as go

from plotly.subplots import make_subplots

import importlib

from src.utils.finance.technical_engine import get_historical_data, apply_technical_indicators, generate_technical_summary

from src.agents.technical_analyst import generate_technical_opinion
import src.agents.technical_analyst
importlib.reload(src.agents.technical_analyst)

from src.utils.finance.fundamental_engine import get_fundamental_data
import src.utils.finance.fundamental_engine
importlib.reload(src.utils.finance.fundamental_engine)

from src.agents.fundamental_analyst import generate_fundamental_opinion
import src.agents.fundamental_analyst
importlib.reload(src.agents.fundamental_analyst)

from src.agents.integral_analyst import generate_integral_opinion
import src.agents.integral_analyst
importlib.reload(src.agents.integral_analyst)



def render_technical_chart(df, ticker):

    # Crear gráfico con subplots: 2 filas. Superior: Precio + SMAs + Bollinger. Inferior: MACD o RSI (elegimos RSI y MACD)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 

                        vertical_spacing=0.03, subplot_titles=(f'Precio y Tendencias de {ticker}', 'Oscilador MACD', 'Oscilador RSI'),

                        row_width=[0.2, 0.2, 0.6])



    # 1. Candlestick

    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Precio'), row=1, col=1)

    # SMAs

    if 'SMA_20' in df: fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='orange', width=1), name='SMA 20'), row=1, col=1)

    if 'SMA_50' in df: fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='blue', width=1), name='SMA 50'), row=1, col=1)

    if 'SMA_200' in df: fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='red', width=1.5), name='SMA 200'), row=1, col=1)

    # Bollinger Bands

    if 'BBU_20_2.0' in df: fig.add_trace(go.Scatter(x=df.index, y=df['BBU_20_2.0'], line=dict(color='gray', width=1, dash='dot'), name='BB Upper'), row=1, col=1)

    if 'BBL_20_2.0' in df: fig.add_trace(go.Scatter(x=df.index, y=df['BBL_20_2.0'], line=dict(color='gray', width=1, dash='dot'), name='BB Lower', fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)



    # 2. MACD

    if 'MACD_12_26_9' in df: fig.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'], line=dict(color='blue', width=1), name='MACD'), row=2, col=1)

    if 'MACDs_12_26_9' in df: fig.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], line=dict(color='orange', width=1), name='Signal'), row=2, col=1)

    if 'MACDh_12_26_9' in df: 

        colors = ['green' if val >= 0 else 'red' for val in df['MACDh_12_26_9']]

        fig.add_trace(go.Bar(x=df.index, y=df['MACDh_12_26_9'], marker_color=colors, name='Histogram'), row=2, col=1)



    # 3. RSI

    if 'RSI_14' in df: 

        fig.add_trace(go.Scatter(x=df.index, y=df['RSI_14'], line=dict(color='purple', width=1.5), name='RSI 14'), row=3, col=1)

        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)

        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)



    fig.update_layout(height=800, template='plotly_dark', showlegend=True, margin=dict(l=20, r=20, t=40, b=20))

    fig.update_xaxes(rangeslider_visible=False)

    return fig



def render_analysis_hub():

    st.title("🎯 Análisis Técnico y Fundamental (IA)")

    st.markdown("Evaluación Integral con agentes cuantitativos de Altus AI.")



    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:

        ticker = st.text_input("Símbolo (Ticker)", value="SQM-B.SN", help="Añade .SN para acciones de Chile. Ej: AAPL, CHILE.SN")

    with col2:

        periodo = st.selectbox("Período de Análisis", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

    with col3:

        tipo_analisis = st.selectbox("Modo de Inteligencia", [

            "Análisis Integral (Técnico + Fundamental)",

            "Solo Análisis Técnico (Quant)",

            "Solo Análisis Fundamental"

        ])



    if st.button("Ejecutar Análisis IA", type="primary", use_container_width=True):
        st.session_state["run_analysis_hub"] = True
        cache_key_int = f"int_{ticker}_{periodo}"
        if cache_key_int in st.session_state:
            del st.session_state[cache_key_int]

    if st.session_state.get("run_analysis_hub"):

        if not ticker:

            st.warning("Debes ingresar un Ticker válido.")

            return



        with st.spinner(f"Altus AI está extrayendo datos para {ticker}..."):

            

            do_tech = "Técnico" in tipo_analisis or "Integral" in tipo_analisis

            do_fund = "Fundamental" in tipo_analisis or "Integral" in tipo_analisis

            

            # VARIABLES PARA IA

            tech_opinion = ""

            fund_opinion = ""

            integral_opinion = ""

            

            if do_tech:
                cache_key_tech = f"tech_{ticker}_{periodo}"
                if cache_key_tech not in st.session_state:
                    df = get_historical_data(ticker, period=periodo)
                    if df is None or df.empty:
                        st.session_state[cache_key_tech] = None
                    else:
                        df = apply_technical_indicators(df)
                        summary = generate_technical_summary(df)
                        with st.spinner("Agente Quant emitiendo dictamen..."):
                            t_op = generate_technical_opinion(ticker, summary)
                        st.session_state[cache_key_tech] = {"df": df, "summary": summary, "tech_opinion": t_op}

                cached_t = st.session_state.get(cache_key_tech)
                if not cached_t:
                    st.error("No se encontraron datos históricos de precio para este ticker.")
                    do_tech = False
                else:
                    df = cached_t["df"]
                    summary = cached_t["summary"]
                    tech_opinion = cached_t["tech_opinion"]
                    
                    st.markdown("### 📈 Análisis Técnico")
                    colA, colB, colC = st.columns(3)
                    colA.metric("Último Precio", f"USD {float(summary['precio_cierre']):,.2f}")
                    colB.metric("RSI (14)", f"{float(summary['rsi_14']):.2f}")
                    colC.metric("Tendencia Largo Plazo", summary['tendencia_largo_plazo'])
                    
                    st.plotly_chart(render_technical_chart(df, ticker), use_container_width=True)
            
            if do_fund:
                cache_key_fund = f"fund_{ticker}"
                if cache_key_fund not in st.session_state:
                    f_data = get_fundamental_data(ticker)
                    if not f_data.get("success"):
                        st.session_state[cache_key_fund] = None
                    else:
                        with st.spinner("Agente Fundamental emitiendo dictamen..."):
                            f_op = generate_fundamental_opinion(ticker, f_data)
                        st.session_state[cache_key_fund] = {"fund_data": f_data, "fund_opinion": f_op}
                
                cached_f = st.session_state.get(cache_key_fund)
                if not cached_f:
                    st.error("No se encontraron datos fundamentales para este ticker.")
                    do_fund = False
                else:
                    fund_data = cached_f["fund_data"]
                    fund_opinion = cached_f["fund_opinion"]
                    sum_f = fund_data["summary"]
                    
                    st.markdown("---")
                    st.markdown("### 🏢 Análisis Fundamental")

                    colX, colY, colZ = st.columns(3)

                    colX.metric("P/E Ratio", f"{float(sum_f.get('pe_ratio', 0)):.2f}" if sum_f.get("pe_ratio") else "N/A")
                    colY.metric("P/B Ratio", f"{float(sum_f.get('pb_ratio', 0)):.2f}" if sum_f.get("pb_ratio") else "N/A")

                    colZ.metric("Flujo de Caja Libre", f"USD {int(sum_f.get('free_cashflow', 0)):,}" if sum_f.get("free_cashflow") else "N/A")

                    

                    with st.expander("Ver Noticias Extraídas"):

                        for n in fund_data.get("news", []):

                            st.markdown(f"- [{n['title']}]({n['link']}) - *{n['publisher']}*")

            

            # SECCIÓN DE RESULTADOS IA

            st.markdown("---")

            st.markdown("## 🧠 Dictamen Oficial Altus AI")
            
            if do_tech and do_fund:
                cache_key_int = f"int_{ticker}_{periodo}"
                if cache_key_int not in st.session_state:
                    with st.spinner("Agente Integral emitiendo dictamen combinado..."):
                        # Extraer consenso de fund_data
                        market_consensus_str = "No disponible"
                        market_consensus_ui = "No disponible"
                        try:
                            if 'fund_data' in locals() and fund_data and fund_data.get('success'):
                                fsum = fund_data['summary']
                                target = fsum.get('target_mean_price', 'N/A')
                                if isinstance(target, (int, float)):
                                    target = f"{target:.2f}"
                                rec_key_raw = fsum.get('recommendation_key', 'N/A')
                                if rec_key_raw is None:
                                    rec_key_raw = 'N/A'
                                rec_key_raw = str(rec_key_raw).replace("_", " ").title()
                                analysts = fsum.get('number_of_analyst_opinions', 'N/A')
                                grade_map = {
                                    "Outperform": "Rendimiento Superior", "Equal-Weight": "Rendimiento Promedio", 
                                    "Overweight": "Sobreponderar", "Underweight": "Subponderar",
                                    "Buy": "Comprar", "Sell": "Vender", "Neutral": "Neutral", "Hold": "Mantener",
                                    "Strong Buy": "Fuerte Compra", "Market Perform": "Rendimiento de Mercado",
                                    "Sector Perform": "Rendimiento del Sector", "Underperform": "Rendimiento Inferior",
                                    "Peer Perform": "Rendimiento Promedio", "Reduce": "Reducir"
                                }
                                # Buscar traduccion case-insensitive
                                rec_key_es = rec_key_raw
                                for k, v in grade_map.items():
                                    if k.lower() in rec_key_raw.lower():
                                        rec_key_es = v
                                        break
                                
                                market_consensus_str = f"Precio Objetivo: {target} | Recomendación Promedio: {rec_key_es} | N° Analistas: {analysts}"
                                market_consensus_ui = f"<b>Precio Objetivo Promedio:</b> {target}<br><b>Recomendación Promedio:</b> {rec_key_es}<br><b>N° Analistas:</b> {analysts}"
                                
                                actions = fsum.get('recent_analyst_actions', [])
                                if actions:
                                      actions_str = ", ".join([f"{a['firm']} ({a['action']} a {a['to_grade']})" for a in actions])
                                      market_consensus_str += f" | Últimas Acciones: {actions_str}"
                                      
                                      actions_ui = "<div style='margin-top: 5px;'><b>Últimas acciones institucionales:</b><div style='margin-top: 2px; font-size: 8.5pt;'>"
                                      for a in actions:
                                          date_str = a.get('date', '')
                                          actions_ui += f"<div style='margin-bottom: 0px; margin-left: 10px; line-height: 1.1;'>• {date_str}: <b>{a['firm']}</b> ({a['action']} a {a['to_grade']})</div>"
                                      actions_ui += "</div></div>"
                                      market_consensus_ui += actions_ui
                        except Exception as e:
                            st.error(f"Error parsing consensus: {e}")
                        
                        i_op = generate_integral_opinion(ticker, tech_opinion, fund_opinion, market_consensus_str)
                        st.session_state[cache_key_int] = i_op
                        st.session_state[f"{cache_key_int}_ui"] = market_consensus_ui
                
                integral_opinion_raw = st.session_state.get(cache_key_int, "")
                market_consensus_ui = st.session_state.get(f"{cache_key_int}_ui", "No disponible")
                
                import json
                try:
                    integral_opinion_json = json.loads(integral_opinion_raw)
                except Exception:
                    integral_opinion_json = {"conclusion": integral_opinion_raw, "recomendacion": "N/A", "conviccion": "N/A", "justificacion": ""}
                
                st.info("**Consenso de Mercado & Perspectiva Oficial Altus AI**")
                
                # Desplegar Consenso y Veredicto en columnas para la UI
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### 📊 Consenso de Mercado (Yahoo Finance)")
                    st.markdown(f'<div translate="no" style="text-align: justify;">{market_consensus_ui}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown('<h4 translate="no">🧠 Posición Altus AI</h4>', unsafe_allow_html=True)
                    st.markdown(f'<div translate="no" style="text-align: justify;"><b>Recomendación:</b> {integral_opinion_json.get("recomendacion", "N/A")} (Convicción {integral_opinion_json.get("conviccion", "N/A")})<br><br>'
                                f'<b>Justificación:</b> {integral_opinion_json.get("justificacion", "")}<br><br>'
                                f'<b>Síntesis Integral:</b> {integral_opinion_json.get("conclusion", "")}</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Pasaremos integral_opinion_json a la funcion PDF en vez de string
                integral_opinion = integral_opinion_json
                
                t_col, f_col = st.columns(2)
                with t_col:
                    st.success("**Veredicto Cuantitativo (Técnico):**")
                    st.markdown(tech_opinion)
                with f_col:
                    st.info("**Veredicto Corporativo (Fundamental):**")
                    st.markdown(fund_opinion)

            elif do_tech:

                st.success("**Veredicto Cuantitativo (Técnico):**")

                st.markdown(tech_opinion)

            elif do_fund:

                st.info("**Veredicto Corporativo (Fundamental):**")

                st.markdown(fund_opinion)


            # OPCIONES Y DESCARGA DE PDF
            st.markdown("---")
            st.markdown("### 📄 Exportar Documento PDF")
            
            tipo_reporte = st.radio("Formato de Reporte", ["Genérico (Mercado)", "Personalizado (Cliente)"], horizontal=True)
            rut_input = ""
            if tipo_reporte == "Personalizado (Cliente)":
                rut_input = st.text_input("Ingresa RUT del Cliente (ej: 12345678-9)")
            
            if tipo_reporte == "Personalizado (Cliente)" and not rut_input.strip():
                st.warning("⚠️ Ingresa el RUT del cliente y presiona 'Enter' para preparar el documento PDF.")
            else:
                # Generar el PDF silenciosamente para el download_button
                import sys
                import importlib
                import src.utils.pdf_generator_analysis
                importlib.reload(src.utils.pdf_generator_analysis)
                from src.utils.pdf_generator_analysis import generar_pdf_analisis_integral
                
                target = summary.get("target_mean_price", "N/A") if 'summary' in locals() else "N/A"
                
                # Export chart to bytes for PDF
                chart_bytes = None
                if 'df' in locals() and df is not None and not df.empty:
                    try:
                        fig = render_technical_chart(df, ticker)
                        chart_bytes = fig.to_image(format="png", scale=4)
                    except Exception as e:
                        pass
                
                try:
                    pdf_bytes = generar_pdf_analisis_integral(
                        ticker=ticker,
                        tech_opinion=tech_opinion if do_tech else "No solicitado.",
                        fund_opinion=fund_opinion if do_fund else "No solicitado.",
                        integral_opinion=integral_opinion if (do_tech and do_fund) else None,
                        market_consensus=market_consensus_ui if 'market_consensus_ui' in locals() else "N/A",
                        is_generic=(tipo_reporte == "Genérico (Mercado)"),
                        client_rut=rut_input if tipo_reporte == "Personalizado (Cliente)" else None,
                        target_price=target,
                        chart_bytes=chart_bytes
                    )
                    if pdf_bytes:
                        st.download_button(
                            label="📥 Descargar Reporte PDF Institucional",
                            data=pdf_bytes,
                            file_name=f"Reporte_Analisis_{ticker}.pdf",
                            mime="application/pdf",
                            type="primary"
                        )
                    else:
                        st.error("No se pudo generar el PDF (ver logs).")
                except Exception as e:
                    st.error(f"Error generando PDF: {e}")
