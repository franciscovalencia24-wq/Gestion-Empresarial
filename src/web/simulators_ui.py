import streamlit as st
import pandas as pd
import importlib
from src.database.connection import SessionLocal
from src.database.models import Prospect
from src.utils.pdf_generator_reliquidacion import generate_reliquidacion_pdf
from src.utils.simulators.reliquidacion_simulator import ReliquidacionSimulator

import src.utils.excel_kyc_generator as excel_gen
import src.utils.kyc_email_generator as email_gen

# Recargar módulos por si Streamlit mantenía una versión previa en caché
importlib.reload(excel_gen)
importlib.reload(email_gen)

from src.utils.excel_kyc_generator import generar_excel_apv_reliquidacion, generar_excel_kyc_corporativo
from src.utils.kyc_email_generator import generar_comunicacion_apv_reliquidacion, generar_comunicacion_kyc
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_apv_simulator(uf_valor):
    import importlib
    import src.utils.excel_kyc_generator as excel_gen
    import src.utils.kyc_email_generator as email_gen
    importlib.reload(excel_gen)
    importlib.reload(email_gen)

    st.markdown("## 📊 Altus AI: Simulador APV Inteligente")
    st.markdown("Herramienta de simulación para maximizar el beneficio fiscal y calcular bonificaciones estatales.")
    
    st.markdown("### 👤 Ficha del Cliente")
    
    modo_demo = st.toggle("Activar Modo Demo (Autocompletar datos ficticios)")
    
    c_rut, c_nom = st.columns(2)
    
    rut_default = "12345678-9" if modo_demo else ""
    rut_buscado = c_rut.text_input("RUT del Cliente", value=rut_default, placeholder="Ej: 12345678-9")
    
    nombre_cliente = "Cliente Demo" if modo_demo else ""
    if rut_buscado and not modo_demo:
        db = SessionLocal()
        try:
            rut_clean = rut_buscado.replace(".", "").replace("-", "").strip().upper()
            from sqlalchemy import func
            prospect = db.query(Prospect).filter(
                func.replace(func.replace(func.upper(Prospect.rut), '.', ''), '-', '') == rut_clean
            ).first()
            if prospect and prospect.nombre:
                nombre_cliente = prospect.nombre
        finally:
            db.close()
            
    nombre_final = c_nom.text_input("Nombre Completo", value=nombre_cliente, placeholder="Nombre del cliente", key=f"nom_apv_{rut_buscado}")
    
    with st.expander("📩 Generar Solicitud de Datos para este Cliente (Excel Corporativo & Correo sin asteriscos)", expanded=False):
        solic_enfoque = st.radio(
            "🎯 Selecciona el Enfoque de la Solicitud:",
            options=["🎯 Aporte Mensual APV & Reliquidación (Recomendado aquí)", "🏛️ Auditoría Patrimonial 360° (KYC General)"],
            key="sim_solic_enfoque"
        )
        
        target_name = nombre_final.strip() if nombre_final else "Cliente"
        
        if "APV" in solic_enfoque:
            val = excel_gen.generar_excel_apv_reliquidacion(client_name=target_name)
            comm = email_gen.generar_comunicacion_apv_reliquidacion(client_name=target_name)
            f_name = f"Formulario_APV_Reliquidacion_{target_name.replace(' ', '_')}.xlsx"
            btn_txt = f"💾 Descargar Excel APV & Reliquidación para {target_name}"
        else:
            val = excel_gen.generar_excel_kyc_corporativo(client_name=target_name)
            comm = email_gen.generar_comunicacion_kyc(client_name=target_name)
            f_name = f"Altus_KYC_{target_name.replace(' ', '_')}.xlsx"
            btn_txt = f"💾 Descargar Excel KYC Corporativo para {target_name}"
            
        st.download_button(
            label=btn_txt,
            data=val,
            file_name=f_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        st.markdown(f"**Asunto Sugerido:** `{comm['asunto']}`")
        st.markdown("##### 📩 Texto para Correo (Sin asteriscos, listo para pegar en Outlook):")
        st.code(comm['cuerpo_email'], language="text")
        st.markdown("##### 📱 Mensaje Corto para WhatsApp:")
        st.code(comm['mensaje_whatsapp'], language="text")

    st.divider()
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### 1. Parámetros de Ingreso")
        sueldo_default = 3000000 if modo_demo else 3000000
        sueldo = st.number_input("Sueldo Mensual Bruto (CLP)", min_value=0, value=sueldo_default, step=100000)
        
        honorarios_default = 500000 if modo_demo else 0
        honorarios = st.number_input("Honorarios Mensuales Brutos (Boletas) (CLP)", min_value=0, value=honorarios_default, step=100000)
        
    with c2:
        st.markdown("#### 2. Escenario APV")
        aporte_default = 100000 if modo_demo else 100000
        aporte_mensual = st.number_input("Aporte APV Mensual (CLP)", min_value=0, value=aporte_default, step=10000)
    
    st.markdown("#### 3. Resultados de Simulación")
    
    ingreso_mensual_total = sueldo + honorarios
    sueldo_anual = ingreso_mensual_total * 12
    aporte_anual = aporte_mensual * 12
    
    tope_b_anual = 600 * uf_valor
    
    if aporte_anual <= tope_b_anual:
        ahorro_impuestos = aporte_anual * 0.135
    else:
        ahorro_impuestos = tope_b_anual * 0.135
        
    bonificacion_a = aporte_anual * 0.15
    
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Aporte Anual", f"${aporte_anual:,.0f} CLP")
    rc2.metric("Beneficio Régimen B (Ahorro Fiscal)", f"${ahorro_impuestos:,.0f} CLP", "Recomendado si tributas alto")
    rc3.metric("Beneficio Régimen A (Bono Estado)", f"${bonificacion_a:,.0f} CLP", "+15% garantizado")
    
    st.divider()
    st.markdown("### 📄 Generación de Reporte")
    
    if st.button("Generar Propuesta PDF (APV)", type="primary"):
        pdf_path = f"propuesta_apv_{rut_buscado or 'cliente'}.pdf"
        data = {
            "nombre": nombre_final,
            "rut": rut_buscado,
            "sueldo_mensual": sueldo,
            "honorarios_mensuales": honorarios,
            "aporte_mensual": aporte_mensual,
            "beneficio_b": ahorro_impuestos,
            "beneficio_a": bonificacion_a,
            "uf_valor": uf_valor
        }
        
        try:
            # generate_pdf_report(data, pdf_path)
            # with open(pdf_path, "rb") as f:
            #     pdf_bytes = f.read()
                
            # st.download_button(...)
            st.warning("⚠️ La generación de PDF para APV Inteligente está en actualización para incluir proyecciones a largo plazo. Pronto estará disponible.")
        except Exception as e:
            st.error(f"Error preparando PDF: {e}")

def render_reliquidacion_simulator(utm_val: float = 65000.0, uf_val: float = 38000.0):
    st.markdown("## 📊 Altus AI: Simulador Reliquidación (Operación Renta)")
    st.markdown("Herramienta avanzada para calcular devoluciones de impuestos e impacto tributario del APV (Régimen B).")
    
    # UTA anual = UTM mensual * 12
    sim = ReliquidacionSimulator(uta_anual_clp=utm_val * 12, uf_actual=uf_val)
    
    st.markdown("### 👤 Ficha del Cliente")
    
    modo_demo = st.toggle("Activar Modo Demo (Autocompletar datos ficticios)", key="demo_reliq")
    
    c_rut, c_nom = st.columns(2)
    
    rut_default = "12345678-9" if modo_demo else ""
    rut_buscado = c_rut.text_input("RUT del Cliente", value=rut_default, placeholder="Ej: 12345678-9", key="rut_reliquida")
    
    nombre_cliente = "Cliente Demo Reliquidación" if modo_demo else ""
    if rut_buscado and not modo_demo:
        db = SessionLocal()
        try:
            rut_clean = rut_buscado.replace(".", "").replace("-", "").strip().upper()
            from sqlalchemy import func
            prospect = db.query(Prospect).filter(
                func.replace(func.replace(func.upper(Prospect.rut), '.', ''), '-', '') == rut_clean
            ).first()
            if prospect and prospect.nombre:
                nombre_cliente = prospect.nombre
        finally:
            db.close()
            
    nombre_final = c_nom.text_input("Nombre Completo", value=nombre_cliente, placeholder="Nombre del cliente", key=f"nom_reliquida_{rut_buscado}")
    
    st.divider()
    
    st.markdown("### 1. Parámetros Legales (Previsionales e Hipotecario)")
    c1, c2, c3, c4 = st.columns(4)
    afp_name = c1.selectbox("AFP del Cliente", options=list(sim.comisiones_afp.keys()), index=2)
    pct_salud = c2.number_input("Cotización Salud (%)", min_value=0.0, max_value=20.0, value=7.0, step=0.1)
    intereses_hipo = c3.number_input("Hipotecario (Art. 55 Bis)", min_value=0, value=0, step=100000, help="Total anual (tope 8 UTA auto)")
    tipo_afiliado = c4.selectbox("Tipo de Afiliado", ["No pensionado", "Pensionado no cotizante", "Pensionado cotizante", "Sueldo Empresarial"])
    
    st.markdown("### 2. Ingresos y Retenciones Anuales")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        metodo_ingreso = st.radio("Método de Ingreso de Rentas", ["Anual (Global)", "Mensual (Detallado)"], horizontal=True)
        
        sueldo_anual = 0
        honorarios = 0
        
        if metodo_ingreso == "Anual (Global)":
            sueldo_def = 36000000 if modo_demo else 36000000
            sueldo_anual = st.number_input("Sueldo Bruto Anual (CLP)", min_value=0, value=sueldo_def, step=1000000, help="Monto total antes de descuentos legales")
            
            honorarios_def = 15000000 if modo_demo else 0
            honorarios = st.number_input("Boletas de Honorarios Anuales Brutas (CLP)", min_value=0, value=honorarios_def, step=1000000)
        else:
            st.markdown("##### Ingreso Mes a Mes")
            meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            # Create a dataframe to edit
            if "df_rentas" not in st.session_state:
                st.session_state.df_rentas = pd.DataFrame({
                    "Mes": meses,
                    "Sueldo Bruto (CLP)": [3000000 if modo_demo else 0] * 12,
                    "Boletas (CLP)": [1250000 if modo_demo else 0] * 12
                })
            
            edited_df = st.data_editor(
                st.session_state.df_rentas, 
                hide_index=True, 
                use_container_width=True,
                disabled=["Mes"]
            )
            st.session_state.df_rentas = edited_df
            
            sueldo_anual = int(edited_df["Sueldo Bruto (CLP)"].sum())
            honorarios = int(edited_df["Boletas (CLP)"].sum())
            
            st.info(f"**Total Anual Calculado**\n\nSueldos: ${sueldo_anual:,.0f} | Boletas: ${honorarios:,.0f}")
        
        ganancias_def = 5000000 if modo_demo else 0
        ganancias_capital = st.number_input("Ganancias de Capital / Rentas Pasivas (CLP)", min_value=0, value=ganancias_def, step=1000000, help="Mayor valor, rescate fondos mutuos, dividendos, etc.")
        
        st.markdown("#### Retenciones Realizadas")
        ret_sueldos_def = 3500000 if modo_demo else 0
        ret_sueldos = st.number_input("Impuesto Único Retenido (Sueldos)", min_value=0, value=ret_sueldos_def, step=100000)
        
        from src.utils.finance.tax_constants import get_current_retention_rate, get_current_retention_percentage_str
        rate = get_current_retention_rate()
        rate_str = get_current_retention_percentage_str()
        
        ret_honorarios_def = int(honorarios * rate) if honorarios > 0 else 0
        ret_honorarios = st.number_input(f"Retención Boletas ({rate_str} aprox)", min_value=0, value=ret_honorarios_def, step=100000)
        
    with col2:
        st.markdown("#### Aportes y Retiros APV")
        apv_b_def = 1200000 if modo_demo else 1200000
        apv_b = st.number_input("Aporte APV Régimen B Anual (CLP)", min_value=0, value=apv_b_def, step=100000)
        
        retiro_apv_b = st.number_input("Retiro APV Régimen B (CLP)", min_value=0, value=0, step=1000000, help="Los retiros sufren un recargo o impuesto único.")
        
        st.markdown("#### Ajuste IGC (Opcional)")
        forzar_tasa = st.checkbox("Forzar Tasa IGC Fija (Modo Escenario)", value=False)
        tasa_fija = None
        if forzar_tasa:
            tasa_fija = st.slider("Tasa Fija (%)", min_value=0.0, max_value=40.0, value=13.5, step=0.5)

    # Cálculo
    resultado = sim.simular_operacion_renta(
        sueldo_anual_bruto=sueldo_anual,
        afp_name=afp_name,
        pct_salud=pct_salud,
        honorarios_anuales=honorarios,
        retencion_sueldos=ret_sueldos,
        retencion_honorarios=ret_honorarios,
        apv_b_anual=apv_b,
        intereses_hipotecarios=intereses_hipo,
        retiro_apvb_anual=retiro_apv_b,
        tipo_afiliado=tipo_afiliado,
        ganancias_capital=ganancias_capital,
        tasa_override=tasa_fija
    )
    st.divider()
    
    st.markdown("### 🏛️ Inteligencia Jurídico-Tributaria (RAG BCN)")
    with st.expander("Ver Análisis Legal Automático", expanded=True):
        with st.spinner("Cruzando perfil financiero contra leyes de la Biblioteca del Congreso Nacional..."):
            from src.intelligence.rag_advisor import RAGAdvisorV2
            if "rag_engine" not in st.session_state:
                st.session_state.rag_engine = RAGAdvisorV2()
            
            perfil_prompt = (
                f"El cliente tiene un sueldo bruto anual de ${sueldo_anual:,.0f}, "
                f"boletas de honorarios por ${honorarios:,.0f}, "
                f"aporta en APV Régimen B ${apv_b:,.0f} y tiene ganancias de capital por ${ganancias_capital:,.0f}. "
                "¿Existe algún beneficio o artículo específico en la Ley sobre Impuesto a la Renta o Ley 21.133 que debamos tener en cuenta para optimizar sus impuestos o alertarlo de algún riesgo? "
                "Responde siendo directo, citando la norma aplicable. "
                "IMPORTANTE PARA TU RESPUESTA: Revisa cuidadosamente la ortografía y el formato Markdown. NUNCA unas palabras con números (por ejemplo, nunca escribas '36.000.000yunaporte', asegúrate de poner espacios). NUNCA dejes espacios entre los asteriscos de negrita y la palabra (usa **$1.200.000** en vez de * *1.200.000)."
            )
            
            try:
                rag_response = st.session_state.rag_engine.ask(perfil_prompt)
                st.info(f"**🔍 Dictamen Legal (IA):**\n\n{rag_response}")
            except Exception as e:
                st.warning(f"No se pudo consultar el motor RAG Tributario: {e}")

    st.divider()
    
    st.markdown("### 💡 Recomendación Algorítmica (Holgura APV)")
    holgura_data = resultado["holgura_apv"]
    st.warning(f"**Análisis de Eficiencia Tributaria:** {holgura_data['mensaje']}")
    
    col_res1, col_res2 = st.columns([1, 1])
    
    with col_res1:
        st.markdown("### 📈 Detalle de la Operación")
        df_res = pd.DataFrame([
            {"Concepto": "Sueldo Bruto Total", "Monto": f"${resultado['renta_bruta_anual']:,.0f}"},
            {"Concepto": "(-) Descuentos Previsionales (AFP/Salud)", "Monto": f"${resultado['descuentos_legales_anuales']:,.0f}"},
            {"Concepto": "(-) Rebaja Hipotecario (Art. 55 Bis)", "Monto": f"${resultado['rebaja_55bis']:,.0f}"},
            {"Concepto": "Base Imponible Pre-APV", "Monto": f"${resultado['base_imponible_pre_apv']:,.0f}"},
            {"Concepto": "IGC Determinado (Sin APV)", "Monto": f"${resultado['igc_original']:,.0f}"},
            {"Concepto": "Total Retenciones", "Monto": f"${resultado['total_retenciones']:,.0f}"},
            {"Concepto": "(-) Impuesto Único Retiro APV B", "Monto": f"${resultado['impuesto_unico_retiro']:,.0f} ({resultado['tasa_impuesto_unico']:.1f}%)"},
            {"Concepto": "Resultado (Devolución/Pago)", "Monto": f"${resultado['saldo_original']:,.0f}"}
        ])
        st.dataframe(df_res, hide_index=True, use_container_width=True)
        
        st.markdown(f"💡 **Beneficio Tributario por APV**: Ahorraste **${resultado['beneficio_neto_apv']:,.0f} CLP** líquidos gracias a tu aporte. Tu tramo marginal efectivo es del **{resultado['tramo_marginal_efectivo']:.1f}%**.")
        
    with col_res2:
        st.markdown("### 📉 Resultado Operación Renta")
        devolucion = resultado["saldo_optimizado"]
        
        if devolucion > 0:
            st.markdown(f"""
            <div style='background-color:#064e3b; padding: 20px; border-radius:10px; border-left: 5px solid #10b981; margin-bottom: 20px;'>
                <h4 style='color:white; margin:0;'>Devolución de Impuestos Estimada</h4>
                <h2 style='color:#34d399; margin:0;'>${devolucion:,.0f} CLP</h2>
                <p style='color:#a7f3d0; margin:0;'>Tienes un saldo a favor contra el Fisco.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background-color:#7f1d1d; padding: 20px; border-radius:10px; border-left: 5px solid #ef4444; margin-bottom: 20px;'>
                <h4 style='color:white; margin:0;'>Impuestos a Pagar (Deuda)</h4>
                <h2 style='color:#fca5a5; margin:0;'>${abs(devolucion):,.0f} CLP</h2>
                <p style='color:#fecaca; margin:0;'>Tus retenciones no cubren el IGC total.</p>
            </div>
            """, unsafe_allow_html=True)

        # Preparar data del PDF
        data_pdf = {
            "nombre": nombre_final,
            "rut": rut_buscado,
            "renta_bruta_anual": resultado["renta_bruta_anual"],
            "descuentos_legales": resultado["descuentos_legales_anuales"],
            "rebaja_55bis": resultado["rebaja_55bis"],
            "renta_bruta": resultado["base_imponible_pre_apv"], 
            "igc_original": resultado["igc_original"],
            "retenciones": resultado["total_retenciones"],
            "aporte_apv": apv_b,
            "renta_neta": resultado["base_imponible_optimizada"],
            "igc_optimizado": resultado["igc_optimizado"],
            "retiro_apvb_anual": resultado["retiro_apvb_anual"],
            "tasa_impuesto_unico": resultado["tasa_impuesto_unico"],
            "impuesto_unico_retiro": resultado["impuesto_unico_retiro"],
            "saldo_final": devolucion,
            "beneficio_apv": resultado["beneficio_neto_apv"],
            "holgura_mensaje": holgura_data["mensaje"],
            "holgura_monto": holgura_data["holgura_optima_clp"],
            "ganancias_capital": ganancias_capital
        }
        
        pdf_path = f"reliquidacion_{rut_buscado or 'cliente'}.pdf"
        
        try:
            generate_reliquidacion_pdf(data_pdf, pdf_path)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                
            st.download_button(
                label="📄 Descargar Documento PDF Entregable",
                data=pdf_bytes,
                file_name=f"Reporte_AltusAI_{rut_buscado or 'cliente'}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error(f"Error preparando PDF: {e}")

def render_credito_vs_inversion_simulator():
    st.markdown("## ⚖️ Simulador Comparativo: Crédito vs Rescate de Inversión")
    st.markdown("Ingresa los datos para generar un reporte PDF personalizado que compara el costo de un crédito vs el costo de oportunidad de descapitalizar.")

    # No requerimos seleccionar al cliente de antemano, pero si ya hay uno en sesión, podemos usarlo
    nombre_default = st.session_state.get("current_client_name", "")
    rut_default = st.session_state.get("current_client_rut", "")
    
    col_cli1, col_cli2 = st.columns(2)
    cliente_nombre = col_cli1.text_input("Nombre del Cliente", value=nombre_default)
    cliente_rut = col_cli2.text_input("RUT del Cliente", value=rut_default)

    st.divider()

    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        st.markdown("#### Datos del Crédito / Retiro")
        monto_credito = st.number_input("Monto a Financiar ($ CLP)", min_value=1000000, value=38000000, step=1000000, key="sim_monto")
        valor_cuota = st.number_input("Valor Cuota Mensual ($ CLP)", min_value=0, value=1054625, step=10000, key="sim_cuota")
        plazo_meses = st.number_input("Plazo (Meses)", min_value=12, max_value=240, value=48, step=12, key="sim_plazo")
        
    with col_sim2:
        st.markdown("#### Rendimientos de Inversión (Tasa Anual %)")
        tasa_inv_cons = st.number_input("Escenario Pesimista (%)", value=5.0, step=0.5, key="sim_tc")
        tasa_inv_mod = st.number_input("Escenario Base (%)", value=8.0, step=0.5, key="sim_tm")
        tasa_inv_opt = st.number_input("Escenario Optimista (%)", value=12.0, step=0.5, key="sim_to")
        
    if st.button("📊 Generar Reporte Comparativo (PDF)", type="primary", use_container_width=True):
        if not cliente_nombre:
            st.warning("Por favor, ingresa el nombre del cliente.")
            st.stop()
            
        with st.spinner("Procesando datos, generando gráficos y emitiendo PDF..."):
            try:
                import os
                import tempfile
                import importlib
                import src.reporting.credito_vs_inversion
                importlib.reload(src.reporting.credito_vs_inversion)
                from src.reporting.credito_vs_inversion import CreditoVsInversionReport
                
                output_dir = os.path.join(os.getcwd(), "src", "web", "assets", "reports")
                os.makedirs(output_dir, exist_ok=True)
                
                templates_dir = os.path.join(os.getcwd(), "src", "web", "templates")
                assets_dir = os.path.join(os.getcwd(), "src", "web", "assets")
                
                # Inferir si es empresa basado en session state o rut (heuristica simple)
                k_tp = f"tipo_persona_{cliente_rut}" if cliente_rut else "PN"
                es_emp = (st.session_state.get(k_tp, "PN") == "PJ")
                
                report = CreditoVsInversionReport(templates_dir, assets_dir, output_dir)
                tasas_inv = [tasa_inv_cons, tasa_inv_mod, tasa_inv_opt]
            
                pdf_path = report.generate_report(
                    client_name=cliente_nombre,
                    es_empresa=es_emp,
                    monto=monto_credito,
                    valor_cuota=valor_cuota,
                    plazo_meses=plazo_meses,
                    tasas_inv=tasas_inv
                )
                
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    
                    st.success("✅ Reporte generado exitosamente.")
                    
                    import base64
                    b64 = base64.b64encode(pdf_bytes).decode()
                    href = f'''
                    <a id="auto_download" href="data:application/pdf;base64,{b64}" download="{os.path.basename(pdf_path)}" style="display:none;">Download</a>
                    <script>
                        setTimeout(function() {{
                            document.getElementById("auto_download").click();
                        }}, 500);
                    </script>
                    '''
                    st.components.v1.html(href, height=0, width=0)
                else:
                    st.error(f"Ocurrió un error al generar el PDF. pdf_path={pdf_path}, exists={os.path.exists(pdf_path) if pdf_path else False}")
            except Exception as e:
                import traceback
                st.error(f"Excepción al generar PDF: {e}")
                st.code(traceback.format_exc())
