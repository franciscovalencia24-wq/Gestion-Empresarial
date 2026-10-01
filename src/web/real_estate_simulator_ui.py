import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def calculate_pmt(rate_annual, years, loan_amount):
    if rate_annual == 0:
        return loan_amount / (years * 12)
    rate_monthly = rate_annual / 100 / 12
    n_periods = years * 12
    pmt = loan_amount * (rate_monthly * (1 + rate_monthly)**n_periods) / ((1 + rate_monthly)**n_periods - 1)
    return pmt

def render_real_estate_simulator():
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0A2342 0%, #001229 100%); padding: 25px; border-radius: 10px; margin-bottom: 25px; color: white; border-left: 5px solid #D4AF37;'>
            <h1 style='color: white; margin: 0; font-size: 2.2em;'>🏢 Simulador Inmobiliario (Cap Rate & TIR)</h1>
            <p style='margin: 10px 0 0 0; font-size: 1.1em; color: #e2e8f0;'>
                Herramienta comercial para comparar la rentabilidad de una inversión en bienes raíces (con apalancamiento) frente a un portafolio financiero líquido a lo largo del tiempo.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Inputs layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏠 Datos de la Propiedad")
        valor_uf = st.number_input("Valor de Compra (UF)", value=3500, step=100)
        pie_pct = st.number_input("Pie aportado (%)", value=20.0, step=1.0, max_value=100.0)
        uf_value = st.number_input("Valor UF Hoy ($)", value=38000, step=100)
        
    with col2:
        st.markdown("### 🏦 Financiamiento (Crédito)")
        tasa_anual = st.number_input("Tasa Anual Hipotecaria (%)", value=4.5, step=0.1)
        plazo_anios = st.number_input("Plazo del Crédito (Años)", value=20, step=1)
        
    with col3:
        st.markdown("### 📈 Costo de Oportunidad")
        tasa_financiera = st.number_input("Retorno Portafolio Financiero (%)", value=8.0, step=0.5, 
                                          help="¿Cuánto rentaría este mismo Pie invertido en fondos mutuos o S&P 500?")
        plusvalia_anual = st.number_input("Plusvalía Inmobiliaria Esperada (%)", value=2.0, step=0.1,
                                          help="Aumento de valor del activo por el mercado.")

    st.markdown("### 💸 Ingresos y Gastos (CLP)")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        arriendo = st.number_input("Arriendo Mensual ($)", value=450000, step=10000)
    with c2:
        vacancia = st.number_input("Vacancia (Meses/Año sin arriendo)", value=1.0, step=0.5)
    with c3:
        contribuciones = st.number_input("Contribuciones Trimestrales ($)", value=60000, step=5000)
    with c4:
        ggcc_mantencion = st.number_input("GGCC/Mantención Mensual ($)", value=20000, step=5000)

    st.markdown("---")

    # --- CALCULATIONS ---
    # Inversión Inicial
    pie_uf = valor_uf * (pie_pct / 100)
    pie_clp = pie_uf * uf_value
    credito_uf = valor_uf - pie_uf
    
    # Dividendo
    if credito_uf > 0 and plazo_anios > 0:
        dividendo_uf = calculate_pmt(tasa_anual, plazo_anios, credito_uf)
    else:
        dividendo_uf = 0
    dividendo_clp = dividendo_uf * uf_value
    dividendo_anual = dividendo_clp * 12

    # Ingresos y Gastos Anuales
    ingreso_arriendo_anual = arriendo * (12 - vacancia)
    gastos_anuales = (contribuciones * 4) + (ggcc_mantencion * 12)
    ingreso_neto_operativo = ingreso_arriendo_anual - gastos_anuales
    flujo_caja_anual = ingreso_neto_operativo - dividendo_anual
    
    valor_propiedad_clp = valor_uf * uf_value
    
    # Métricas Inmobiliarias
    cap_rate = (ingreso_neto_operativo / valor_propiedad_clp) * 100 if valor_propiedad_clp > 0 else 0
    roe = (flujo_caja_anual / pie_clp) * 100 if pie_clp > 0 else 0

    st.markdown("### 📊 Métricas de Rentabilidad (Año 1)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pie Inicial (Costo Oportunidad)", f"${pie_clp:,.0f}")
    m2.metric("Dividendo Mensual Estimado", f"${dividendo_clp:,.0f}", f"{dividendo_uf:,.2f} UF", delta_color="off")
    m3.metric("Cap Rate (Renta S/Deuda)", f"{cap_rate:,.2f}%", help="Ingreso Operativo Neto / Valor Propiedad")
    m4.metric("Cash-on-Cash / ROE", f"{roe:,.2f}%", help="Flujo de Caja Anual / Pie Invertido")
    
    # --- SIMULACIÓN MULTIANUAL ---
    st.markdown("---")
    anios_sim = st.slider("Horizonte de Proyección (Años)", min_value=1, max_value=40, value=20, step=1)
    df_sim = pd.DataFrame(index=range(1, anios_sim + 1))
    
    # Inmobiliario
    valores_prop = []
    flujos_acumulados = []
    saldos_deuda = []
    patrimonio_inmobiliario = []
    
    flujo_acum = 0
    saldo_actual = credito_uf
    tasa_mensual = tasa_anual / 100 / 12
    
    for y in range(1, anios_sim + 1):
        # Valor propiedad sube por plusvalia
        vp = valor_propiedad_clp * ((1 + plusvalia_anual/100)**y)
        valores_prop.append(vp)
        
        # Asumimos que arriendo y gastos crecen con la UF (inflación neutra, los mantenemos fijos en poder adquisitivo actual para comparar)
        flujo_acum += flujo_caja_anual
        flujos_acumulados.append(flujo_acum)
        
        # Amortización del crédito (rough estimate yearly)
        if y <= plazo_anios and saldo_actual > 0:
            for _ in range(12):
                interes = saldo_actual * tasa_mensual
                amortizacion = dividendo_uf - interes
                saldo_actual -= amortizacion
                if saldo_actual < 0: saldo_actual = 0
        saldos_deuda.append(saldo_actual * uf_value)
        
        # Patrimonio Inmobiliario Líquido = Valor Propiedad - Deuda + Flujo de Caja Acumulado
        pat = vp - (saldo_actual * uf_value) + flujo_acum
        patrimonio_inmobiliario.append(pat)

    # Financiero (Fondo Mutuo / S&P 500)
    patrimonio_financiero = []
    for y in range(1, anios_sim + 1):
        # El pie inicial compuesto a la tasa financiera
        pat_fin = pie_clp * ((1 + tasa_financiera/100)**y)
        # Si la propiedad genera flujo negativo, el financiero también tiene que "pagar" ese déficit para que la comparación sea justa
        # O podemos asumir que el flujo negativo se resta del financiero. 
        # Para mantenerlo simple, solo componemos el Pie Inicial.
        patrimonio_financiero.append(pat_fin)

    df_sim["Patrimonio Inmobiliario"] = patrimonio_inmobiliario
    df_sim["Patrimonio Financiero (Portafolio)"] = patrimonio_financiero
    
    st.markdown("---")
    st.markdown(f"### 🚀 Proyección a {anios_sim} Años: Real Estate vs Portafolio Financiero")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sim.index, y=df_sim["Patrimonio Inmobiliario"], 
                             mode='lines+markers', name='Inversión Inmobiliaria (Propiedad + Flujos - Deuda)',
                             line=dict(color='#2E86AB', width=3)))
    fig.add_trace(go.Scatter(x=df_sim.index, y=df_sim["Patrimonio Financiero (Portafolio)"], 
                             mode='lines+markers', name=f'Inversión Financiera (Pie al {tasa_financiera}%)',
                             line=dict(color='#D4AF37', width=3)))
                             
    fig.update_layout(
        xaxis_title="Años",
        yaxis_title="Patrimonio Neto Liquidable (CLP)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig, width="stretch")

    # Conclusión Automática
    pat_inm_final = patrimonio_inmobiliario[-1]
    pat_fin_final = patrimonio_financiero[-1]
    
    if pat_inm_final > pat_fin_final:
        ganador = "Inmobiliaria"
        dif = pat_inm_final - pat_fin_final
    else:
        ganador = "Financiera"
        dif = pat_fin_final - pat_inm_final
        
    st.info(f"💡 **Conclusión del Simulador:** En un horizonte de {anios_sim} años, la inversión **{ganador}** termina con un patrimonio neto mayor por una diferencia de **${dif:,.0f}**. El Real Estate se apalanca en el crédito para multiplicar el retorno del pie (efecto multiplicador), mientras que el portafolio financiero brilla por el interés compuesto pasivo y la total liquidez sin deudas.")
