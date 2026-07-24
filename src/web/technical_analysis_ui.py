import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.utils.finance.technical_engine import get_historical_data, apply_technical_indicators, generate_technical_summary

def render_technical_analysis_ui():
    st.markdown("## 🤖 Altus AI: Analista Técnico Especializado")
    st.markdown("Terminal de análisis técnico cuantitativo para instrumentos financieros en Chile y EE.UU.")
    
    st.markdown("### 1. Seleccionar Instrumento")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    ticker = col1.text_input("Ticker del Instrumento", value="AAPL", help="Usa .SN para acciones chilenas (ej. SQM-B.SN, CHILE.SN)")
    period = col2.selectbox("Período de Análisis", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
    
    # yfinance only allows intraday for max 60 days
    is_intraday = period in ["1d", "5d", "1mo"]
    interval_options = ["15m", "1h", "1d", "1wk"] if is_intraday else ["1d", "1wk", "1mo"]
    interval = col3.selectbox("Frecuencia (Intervalo)", interval_options, index=interval_options.index("1d") if "1d" in interval_options else 0)
    
    if st.button("Ejecutar Análisis Cuantitativo", type="primary"):
        with st.spinner(f"Descargando datos y procesando algoritmos para {ticker}..."):
            try:
                # 1. Obtener y procesar datos
                df = get_historical_data(ticker, period=period, interval=interval)
                df = apply_technical_indicators(df)
                
                if df.empty:
                    st.error("No se pudieron obtener datos válidos para generar el gráfico.")
                    return
                
                # 2. Generar resumen cuantitativo
                summary = generate_technical_summary(df)
                
                # 3. Mostrar KPIs Rápidos
                st.markdown("### 2. Resumen Cuantitativo Actual")
                c1, c2, c3, c4 = st.columns(4)
                
                precio = summary.get('precio_cierre')
                rsi = summary.get('rsi_14')
                tendencia = summary.get('tendencia_largo_plazo', 'N/A')
                
                c1.metric("Último Precio", f"{precio:.2f}" if precio else "N/A")
                c2.metric("RSI (14)", f"{rsi:.1f}" if rsi else "N/A", delta="Sobrevendido" if rsi and rsi < 30 else ("Sobrecomprado" if rsi and rsi > 70 else "Neutral"), delta_color="off")
                c3.metric("Tendencia a Largo Plazo", tendencia)
                c4.metric("Volumen", f"{summary.get('volumen', 0):,.0f}" if summary.get('volumen') else "N/A")
                
                # 4. Renderizar Gráfico Interactivo Avanzado
                st.markdown("### 3. Gráficos de Velas y Osciladores")
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                    vertical_spacing=0.03, subplot_titles=(f'{ticker} - Precio y Medias', 'RSI & MACD'),
                                    row_width=[0.3, 0.7])

                # Velas (Candlesticks)
                fig.add_trace(go.Candlestick(x=df.index,
                                open=df['Open'], high=df['High'],
                                low=df['Low'], close=df['Close'], name='Precio'), row=1, col=1)
                
                # Medias Móviles
                cols = df.columns
                sma20 = next((c for c in cols if 'SMA_20' in c), None)
                sma50 = next((c for c in cols if 'SMA_50' in c), None)
                sma200 = next((c for c in cols if 'SMA_200' in c), None)
                
                if sma20: fig.add_trace(go.Scatter(x=df.index, y=df[sma20], line=dict(color='blue', width=1), name='SMA 20'), row=1, col=1)
                if sma50: fig.add_trace(go.Scatter(x=df.index, y=df[sma50], line=dict(color='orange', width=1), name='SMA 50'), row=1, col=1)
                if sma200: fig.add_trace(go.Scatter(x=df.index, y=df[sma200], line=dict(color='red', width=2), name='SMA 200'), row=1, col=1)
                
                # RSI en el segundo plot
                rsi_col = next((c for c in cols if 'RSI' in c), None)
                if rsi_col:
                    fig.add_trace(go.Scatter(x=df.index, y=df[rsi_col], line=dict(color='purple', width=1.5), name='RSI 14'), row=2, col=1)
                    # Lineas de 30 y 70
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                    
                # Configurar Layout
                fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False,
                                  margin=dict(l=20, r=20, t=40, b=20))
                                  
                st.plotly_chart(fig, use_container_width=True)
                
                # 5. Agente de IA
                st.markdown("### 4. Opinión Fundada de Altus AI")
                
                from src.agents.technical_analyst import generate_technical_opinion
                with st.spinner("Generando análisis cuantitativo fundamentado..."):
                    opinion = generate_technical_opinion(ticker, summary)
                    st.markdown(f"> {opinion}")
                
            except Exception as e:
                st.error(f"Error procesando el análisis: {e}")
