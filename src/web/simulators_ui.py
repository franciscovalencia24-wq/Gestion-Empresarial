import streamlit as st
import pandas as pd
import importlib
from src.database.connection import SessionLocal
from src.database.models import Prospect
from src.utils.pdf_generator_reliquidacion import generate_reliquidacion_pdf
from src.utils.simulators.reliquidacion_simulator import ReliquidacionSimulator

import src.utils.excel_kyc_generator as excel_gen
import src.utils.kyc_email_generator as email_gen
import src.utils.simulators.reliquidacion_simulator as rel_sim_module

# Recargar módulos por si Streamlit mantenía una versión previa en caché
importlib.reload(excel_gen)
importlib.reload(email_gen)
importlib.reload(rel_sim_module)

from src.utils.simulators.reliquidacion_simulator import ReliquidacionSimulator

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
            width="stretch"
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
        
        edad_default = 45 if modo_demo else 40
        edad = st.number_input("Edad Actual (Opcional)", min_value=18, max_value=100, value=edad_default)
        genero = st.selectbox("Género", ["Masculino (Retiro 65)", "Femenino (Retiro 60)"])
        
        deposito_convenido = st.number_input("Depósito Convenido Anual (CLP)", min_value=0, value=0, step=100000)
        saldo_apv_actual = st.number_input("Saldo APV Actual (CLP)", min_value=0, value=0, step=500000)

    st.markdown("#### 3. Resultados de Simulación")
    
    ingreso_mensual_total = sueldo + honorarios
    sueldo_anual = ingreso_mensual_total * 12
    aporte_anual = aporte_mensual * 12
    
    from src.utils.simulators.apv_simulator import APVSimulator
    sim_apv = APVSimulator(uf_actual=uf_valor)
    
    # Calcular beneficios
    res_b = sim_apv.calcular_beneficio_regimen_b(sueldo_bruto_clp=ingreso_mensual_total, aporte_mensual_clp=aporte_mensual)
    res_a = sim_apv.calcular_beneficio_regimen_a(aporte_mensual_clp=aporte_mensual, meses=12)
    
    ahorro_impuestos = res_b.get("ahorro_tributario_anual", 0.0)
    bonificacion_a = res_a.get("bonificacion_anual_maxima", 0.0)
    
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Aporte Anual", f"${aporte_anual:,.0f} CLP")
    rc2.metric("Beneficio Régimen B (Ahorro Fiscal)", f"${ahorro_impuestos:,.0f} CLP", "Recomendado si tributas alto")
    rc3.metric("Beneficio Régimen A (Bono Estado)", f"${bonificacion_a:,.0f} CLP", "+15% garantizado")
    
    # Calcular proyección
    edad_retiro = 65 if "Masculino" in genero else 60
    anos_restantes = max(1, edad_retiro - edad)
    
    df_proy = sim_apv.proyectar_pension_detallada(
        saldo_obligatorio_actual=0.0,
        saldo_apva_actual=saldo_apv_actual if ahorro_impuestos < bonificacion_a else 0.0,
        saldo_apvb_actual=saldo_apv_actual if ahorro_impuestos >= bonificacion_a else 0.0,
        saldo_dc_actual=0.0,
        sueldo_bruto_clp=ingreso_mensual_total,
        aporte_apv_mensual=aporte_mensual,
        aporte_dc_anual=deposito_convenido,
        anos_restantes=anos_restantes,
        rentabilidad_anual=0.05
    )
    
    st.divider()
    st.markdown("### 📄 Generación de Reporte")
    
    try:
        from src.utils.pdf_generator_apv import generar_pdf_apv
        pdf_out_path = generar_pdf_apv(
            rut=rut_buscado or "Sin RUT",
            nombre=nombre_final or "Cliente Confidencial",
            sueldo=ingreso_mensual_total,
            aporte=aporte_mensual,
            aporte_dc_anual=deposito_convenido,
            anos=anos_restantes,
            rentabilidad=0.05,
            ahorro_anual=ahorro_impuestos,
            bono_estado=bonificacion_a,
            df_proy=df_proy
        )
        with open(pdf_out_path, "rb") as f:
            pdf_bytes = f.read()
            
        st.download_button(
            label="📄 Descargar Propuesta APV Oficial (PDF)",
            data=pdf_bytes,
            file_name=f"Propuesta_APV_{rut_buscado or 'Oficial'}.pdf",
            mime="application/pdf",
            type="primary",
            width="stretch"
        )
    except Exception as e:
        st.error(f"Error preparando PDF: {e}")

def render_reliquidacion_simulator():
    from src.osint.indicadores import get_uf_info, get_utm_info
    uf_info = get_uf_info()
    utm_info = get_utm_info()
    uf_val = uf_info["valor"]
    utm_val = utm_info["valor"]

    st.markdown("## 📊 Altus AI: Simulador Reliquidación (Operación Renta)")
    st.markdown("Herramienta avanzada para calcular devoluciones de impuestos e impacto tributario del APV (Régimen B).")
    
    fecha_uf = uf_info.get("fecha", "Desconocida")
    estado_uf = "⚠️ Valor de resguardo local" if uf_info.get("is_fallback") else "✅ API en línea"
    st.info(f"**📌 Valores tributarios utilizados:** UF = ${uf_val:,.2f} | UTM = ${utm_val:,.0f} (Última actualización: {fecha_uf} | {estado_uf})")
    
    # UTA anual = UTM mensual * 12
    sim = ReliquidacionSimulator(uta_anual_clp=utm_val * 12, uf_actual=uf_val)
    
    st.markdown("### 👤 Ficha del Cliente")
    
    modo_demo = st.toggle("Activar Modo Demo (Autocompletar datos ficticios)", key="demo_reliq")
    
    c_rut, c_nom = st.columns(2)
    
    rut_default = "12345678-9" if modo_demo else ""
    rut_buscado = c_rut.text_input("RUT del Cliente", value=rut_default, placeholder="Ej: 12345678-9", key="rut_reliquida")
    
    nombre_cliente = "Cliente Demo Reliquidación" if modo_demo else ""
    pre_intereses_hipo = 0.0
    pre_gastos_edu = 0.0
    pre_retenciones = 0.0
    
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
                pre_intereses_hipo = getattr(prospect, 'intereses_hipotecario', 0.0) or 0.0
                pre_gastos_edu = getattr(prospect, 'gastos_educacion', 0.0) or 0.0
                pre_retenciones = getattr(prospect, 'retenciones_2da_cat', 0.0) or 0.0
        finally:
            db.close()
            
    nombre_final = c_nom.text_input("Nombre Completo", value=nombre_cliente, placeholder="Nombre del cliente", key=f"nom_reliquida_{rut_buscado}")
    
    st.divider()
    
    st.markdown("### 1. Parámetros Legales (Previsionales e Hipotecario)")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        afp_name = st.selectbox("AFP del Cliente", options=list(sim.comisiones_afp.keys()), index=0)
        tasa_afp = 10.0 + (sim.comisiones_afp[afp_name] * 100)
        st.caption(f"Tasa total: **{tasa_afp:.2f}%** (Tope 84.3 UF)")
        
    with c2:
        sis_salud = st.selectbox("Sistema de Salud", ["Fonasa (7%)", "Isapre (UF)"])
        if sis_salud == "Isapre (UF)":
            c_is1, c_is2 = st.columns(2)
            isapre_name = c_is1.text_input("Isapre", value="Consalud", label_visibility="collapsed")
            isapre_uf = c_is2.number_input("Plan (UF)", min_value=0.0, value=7.178, step=0.1, label_visibility="collapsed")
            st.caption("Para base imponible se topa al 7%")
            pct_salud = 7.0
        else:
            pct_salud = 7.0
            st.caption("Legal obligatorio 7%")
            
    with c3:
        intereses_hipo = st.number_input("Hipotecario (Art. 55 Bis)", min_value=0, value=int(pre_intereses_hipo), step=100000, help="Total anual (tope 8 UTA auto)")
        gastos_edu = st.number_input("Educación (Art. 55 Ter)", min_value=0, value=int(pre_gastos_edu), step=100000, help="Crédito anual directo")
    with c4:
        tipo_afiliado = st.selectbox("Tipo de Afiliado", ["No pensionado", "Pensionado no cotizante", "Pensionado cotizante", "Sueldo Empresarial"])
    
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
            
            import pandas as pd
            # Prorrateo anual para el reporte
            df_rentas_final = pd.DataFrame([{
                "Mes": "Promedio Anualizado (Prorrateo)",
                "Sueldo Bruto (CLP)": sueldo_anual,
                "Boletas (CLP)": honorarios
            }])
        else:
            st.markdown("##### Ingreso Mes a Mes")
            meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            # Create a dataframe to edit
            import pandas as pd
            if "df_rentas" not in st.session_state:
                st.session_state.df_rentas = pd.DataFrame({
                    "Mes": meses,
                    "Sueldo Bruto (CLP)": [3000000 if modo_demo else 0] * 12,
                    "Boletas (CLP)": [1250000 if modo_demo else 0] * 12
                })
            
            edited_df = st.data_editor(
                st.session_state.df_rentas, 
                hide_index=True, 
                width="stretch",
                disabled=["Mes"]
            )
            st.session_state.df_rentas = edited_df
            df_rentas_final = edited_df
            
            sueldo_anual = int(edited_df["Sueldo Bruto (CLP)"].sum())
            honorarios = int(edited_df["Boletas (CLP)"].sum())
            
            st.info(f"**Total Anual Calculado**\n\nSueldos: ${sueldo_anual:,.0f} | Boletas: ${honorarios:,.0f}")
        
        ganancias_def = 5000000 if modo_demo else 0
        ganancias_capital = st.number_input("Ganancias de Capital / Rentas Pasivas (CLP)", min_value=0, value=ganancias_def, step=1000000, help="Mayor valor, rescate fondos mutuos, dividendos, etc.")
        
        st.markdown("#### Simulación de Bonos y Depósito Convenido")
        st.info("Calcula el costo empresa de un bono líquido y simula qué pasa si lo destinas a Depósito Convenido (DC).")
        c_b1, c_b2 = st.columns(2)
        bono_liquido = c_b1.number_input("Bono Líquido a Recibir (CLP)", min_value=0, value=0, step=1000000)
        
        # Estimar el bruto asumiendo una tasa marginal alta (ej. 35%) 
        bono_bruto_est = int(bono_liquido / 0.65) if bono_liquido > 0 else 0
        c_b2.metric("Bono Bruto Aprox (Costo Empresa)", f"${bono_bruto_est:,.0f}")
        
        usar_como_dc = st.checkbox("Destinar este Bono a Depósito Convenido (Tope 900 UF)", value=False)
        deposito_convenido = 0
        if usar_como_dc and bono_bruto_est > 0:
            tope_dc = 900 * uf_val
            deposito_convenido = min(bono_bruto_est, tope_dc)
            st.success(f"Se inyectarán ${deposito_convenido:,.0f} a Depósito Convenido libre de impuestos.")
            if bono_bruto_est > tope_dc:
                st.warning(f"Excedes el tope de 900 UF. El remanente (${bono_bruto_est - tope_dc:,.0f}) tributará normalmente.")
        
        # (Retenciones will be rendered below)
        
    with col2:
        st.markdown("#### Aportes y Retiros APV")
        c2_b = st.container()
        apv_b_def = 1200000 if modo_demo else 0
        apv_b = c2_b.number_input("Aporte APV Régimen B Anual (CLP)", min_value=0, value=apv_b_def, step=1000000)
        modal_apv_b = c2_b.selectbox("Modalidad del Aporte APV-B", ["Aporte Directo (Cuenta Corriente)", "Descuento por Planilla (Vía Empleador)"])
        retiro_apv_b = c2_b.number_input("Retiro APV Régimen B (CLP)", min_value=0, value=0, step=1000000, help="Los retiros sufren un recargo o impuesto único.")
        
        st.markdown("#### Ajuste IGC (Opcional)")
        forzar_tasa = st.checkbox("Forzar Tasa IGC Fija (Modo Escenario)", value=False)
        tasa_fija = None
        if forzar_tasa:
            tasa_fija = st.slider("Tasa Fija (%)", min_value=0.0, max_value=40.0, value=13.5, step=0.5)

    with col1:
        st.markdown("#### Retenciones Realizadas")
        # Estimar impuesto único retenido asumiendo sueldo parejo
        estimated_tax = 0
        if sueldo_anual > 0:
            renta_dict = sim.calcular_renta_tributable(
                sueldo_bruto_mensual=sueldo_anual / 12,
                afp_name=afp_name,
                pct_salud=pct_salud,
                descuento_cesantia=True,
                tipo_afiliado=tipo_afiliado
            )
            base_anual = renta_dict["renta_tributable_mensual"] * 12
            
            # Si el APV fue por planilla, el empleador calculó el IGC sobre una base menor
            if modal_apv_b == "Descuento por Planilla (Vía Empleador)":
                base_anual = max(0, base_anual - apv_b)
                
            estimated_tax = int(sim.calcular_igc(base_anual))
            
        ret_sueldos_def = 3500000 if modo_demo else estimated_tax
        ret_sueldos = st.number_input("Impuesto Único Retenido (Sueldos)", min_value=0, value=ret_sueldos_def, step=100000, help="Autocalculado asumiendo sueldo estable. Ajuste si tiene el dato real.")
        
        from src.utils.finance.tax_constants import get_current_retention_rate, get_current_retention_percentage_str
        rate = get_current_retention_rate()
        rate_str = get_current_retention_percentage_str()
        
        ret_honorarios_def = int(honorarios * rate) if honorarios > 0 else 0
        if pre_retenciones > 0:
            ret_honorarios_def = int(pre_retenciones)
        ret_honorarios = st.number_input(f"Retención Boletas ({rate_str} aprox)", min_value=0, value=ret_honorarios_def, step=100000)

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
        gastos_educacion=gastos_edu,
        retiro_apvb_anual=retiro_apv_b,
        tipo_afiliado=tipo_afiliado,
        ganancias_capital=ganancias_capital,
        tasa_override=tasa_fija,
        deposito_convenido_anual=deposito_convenido
    )
    
    st.session_state.modal_apv_b = modal_apv_b  
    # Calculate marginal rate for the RAG prompt
    base_uta = resultado["base_imponible_pre_apv"] / sim.uta_anual_clp if sim.uta_anual_clp > 0 else 0
    tasa_marginal = 0.0
    for tramo in sim.tramos_igc:
        if base_uta <= tramo["hasta"]:
            tasa_marginal = tramo["factor"]
            break
    st.divider()
    
    st.markdown("### 🏛️ Inteligencia Jurídico-Tributaria (RAG BCN)")
    with st.expander("Ver Análisis Legal Automático", expanded=True):
        with st.spinner("Cruzando perfil financiero contra leyes de la Biblioteca del Congreso Nacional..."):
            from src.intelligence.rag_advisor import RAGAdvisorV2
            if "rag_engine" not in st.session_state:
                st.session_state.rag_engine = RAGAdvisorV2()
            
            nombre_cliente_str = nombre_final.split()[0] if nombre_final else 'cliente'
            
            perfil_prompt = (
                f"Actúa como un asesor tributario experto. Redacta un dictamen legal MUY RESUMIDO, DE ALTO NIVEL EJECUTIVO, en formato de viñetas (bullet points). "
                f"OBLIGATORIO: Empieza tu respuesta EXACTAMENTE con esta frase y luego da un salto de línea: 'Estimado {nombre_cliente_str}. FV presenta a usted el siguiente dictamen ejecutivo respecto a su situación tributaria.' "
                f"NO uses párrafos densos, sé directo y estratégico. "
                f"El cliente tiene un sueldo bruto anual de ${sueldo_anual:,.0f}. "
                f"Su tasa marginal de impuesto actual es del {tasa_marginal*100:.1f}%. "
                f"Aporta en APV Régimen B ${apv_b:,.0f}. "
            )
            if honorarios > 0:
                perfil_prompt += f"Tiene boletas de honorarios por ${honorarios:,.0f}. "
            if ganancias_capital > 0:
                perfil_prompt += f"Tiene ganancias de capital por ${ganancias_capital:,.0f}. "
            
            perfil_prompt += (
                "IMPORTANTE: Si no tiene boletas de honorarios, NO menciones la ley 21.133. "
                "Si no tiene ganancias de capital, NO hables de enajenaciones ni rentas de capital. "
                "NUNCA unas palabras con números (por ejemplo, nunca escribas '36.000.000yunaporte'). "
                "NUNCA dejes espacios entre los asteriscos de negrita y la palabra. "
                "PROHIBIDO CITAR nombres de archivo o metadatos de las fuentes (por ejemplo, NO escribas 'Marco Jurídico Vigente.pdf' ni 'Categoría: MANUALES DE ESTUDIO'). Debes referirte siempre a 'la Ley sobre Impuesto a la Renta' o la legislación chilena aplicable."
            )
            
            rag_response = ""
            try:
                rag_response = st.session_state.rag_engine.ask(perfil_prompt)
                
                # Formatear el HTML para que se vea justificado y elegante
                import markdown
                html_rag = markdown.markdown(rag_response)
                st.markdown(f"""
                <div style='background-color:#f8fafc; border-left: 4px solid #3b82f6; padding: 20px; border-radius: 6px; color: #1e293b; text-align: justify; line-height: 1.6; font-size: 14.5px;'>
                    <h4 style='color: #0f172a; margin-top: 0; margin-bottom: 15px;'>🔍 Dictamen Técnico - Tributario (IA)</h4>
                    {html_rag}
                </div>
                """, unsafe_allow_html=True)
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
        st.dataframe(df_res, hide_index=True, width="stretch")
        
        beneficio_texto = ""
        if apv_b > 0:
            beneficio_texto = f"💡 **Beneficio Tributario por APV:** Tu decisión de aportar **${apv_b:,.0f}** en APV-B rebajó tu base imponible en la misma cantidad. Esto te generó un beneficio fiscal neto de **${resultado['beneficio_neto_apv']:,.0f} CLP**. Tu tramo marginal efectivo es del **{resultado['tramo_marginal_efectivo']:.1f}%**."
            
        st.markdown(f"""
        <div style='background-color: white; padding: 25px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 25px;'>
            {beneficio_texto}
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('modal_apv_b') == "Descuento por Planilla (Vía Empleador)":
            st.info("ℹ️ **Aporte vía Planilla:** Como tu APV-B fue descontado mensualmente por tu empleador, tu *Impuesto Único Retenido* ya era menor cada mes. El beneficio tributario arriba indicado representa el total de impuestos que dejaste de pagar en el año, no necesariamente un saldo a favor en la Operación Renta, ya que el ahorro lo disfrutaste mes a mes en tu sueldo líquido.")
        
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

        st.markdown("### 📊 Comparación de Escenarios (Ahorro Tributario Final)")
        
        # Función auxiliar para calcular beneficio APV-A (15% del aporte, topado a 6 UTM)
        def beneficio_apva(aporte_clp):
            tope_utm = 6 * utm_val
            return min(aporte_clp * 0.15, tope_utm)
            
        aporte_apva_clp = 40 * utm_val
        beneficio_apva_clp = beneficio_apva(aporte_apva_clp)

        # Escenario 1: Actual (0 APV, 0 DC)
        res_actual = sim.simular_operacion_renta(
            sueldo_anual, afp_name, pct_salud, honorarios, ret_sueldos, ret_honorarios,
            apv_b_anual=0, intereses_hipotecarios=intereses_hipo, tipo_afiliado=tipo_afiliado,
            ganancias_capital=ganancias_capital, tasa_override=tasa_fija, deposito_convenido_anual=0
        )
        
        # Escenario 2: Max APV-B (600 UF)
        res_apvb = sim.simular_operacion_renta(
            sueldo_anual, afp_name, pct_salud, honorarios, ret_sueldos, ret_honorarios,
            apv_b_anual=600 * uf_val, intereses_hipotecarios=intereses_hipo, tipo_afiliado=tipo_afiliado,
            ganancias_capital=ganancias_capital, tasa_override=tasa_fija, deposito_convenido_anual=0
        )
        
        # Escenarios Ficticios (Depósito Convenido Tope 900 UF)
        tope_dc = 900 * uf_val
        res_dc = sim.simular_operacion_renta(
            sueldo_anual, afp_name, pct_salud, honorarios, ret_sueldos, ret_honorarios,
            apv_b_anual=0, intereses_hipotecarios=intereses_hipo, tipo_afiliado=tipo_afiliado,
            ganancias_capital=ganancias_capital, tasa_override=tasa_fija, 
            deposito_convenido_anual=tope_dc
        )
        
        res_dc_apvb = sim.simular_operacion_renta(
            sueldo_anual, afp_name, pct_salud, honorarios, ret_sueldos, ret_honorarios,
            apv_b_anual=600 * uf_val, intereses_hipotecarios=intereses_hipo, tipo_afiliado=tipo_afiliado,
            ganancias_capital=ganancias_capital, tasa_override=tasa_fija, 
            deposito_convenido_anual=tope_dc
        )
        
        monto_600uf = 600 * uf_val
        monto_900uf = 900 * uf_val
        monto_40utm = 40 * utm_val
        
        compare_data = [
            {
                "Escenario": "1. Situación Actual (Sin APV)", 
                "Saldo": res_actual["saldo_optimizado"], 
                "Ahorro": 0, 
                "Inversion": 0,
                "Color": "#94a3b8"
            },
            {
                "Escenario": f"2. Topando APV-B (600 UF ≈ ${monto_600uf:,.0f})", 
                "Saldo": res_apvb["saldo_optimizado"], 
                "Ahorro": res_apvb["beneficio_neto_apv"], 
                "Inversion": monto_600uf,
                "Color": "#3b82f6"
            },
            {
                "Escenario": f"3. APV-B (600 UF) + APV-A (40 UTM) (≈ ${(monto_600uf + monto_40utm):,.0f})", 
                "Saldo": res_apvb["saldo_optimizado"], 
                "Ahorro": res_apvb["beneficio_neto_apv"] + beneficio_apva_clp, 
                "Inversion": monto_600uf + monto_40utm,
                "Color": "#10b981"
            },
            {
                "Escenario": f"4. Ficticio: DC (900 UF ≈ ${monto_900uf:,.0f})", 
                "Saldo": res_dc["saldo_optimizado"], 
                "Ahorro": res_actual["igc_original"] - res_dc["igc_original"], 
                "Inversion": monto_900uf,
                "Color": "#8b5cf6"
            },
            {
                "Escenario": f"5. Ideal: DC + APV-B + APV-A (≈ ${(monto_900uf + monto_600uf + monto_40utm):,.0f})", 
                "Saldo": res_dc_apvb["saldo_optimizado"], 
                "Ahorro": (res_actual["igc_original"] - res_dc_apvb["igc_original"]) + beneficio_apva_clp, 
                "Inversion": monto_900uf + monto_600uf + monto_40utm,
                "Color": "#f59e0b"
            }
        ]
        
        html_cards = "<div style='display: grid; gap: 15px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); margin-bottom: 20px;'>"
        for item in compare_data:
            if item['Saldo'] > 0:
                saldo_str = f"Devolución TGR (Saldo a favor): <strong style='color:#10b981;'>+${item['Saldo']:,.0f}</strong>"
            else:
                saldo_str = f"Deuda Fisco (A Pagar): <strong style='color:#ef4444;'>-${abs(item['Saldo']):,.0f}</strong>"
                
            inversion_str = f"${item['Inversion']:,.0f} CLP"
            border_color = item["Color"]
            
            # Sin espacios al inicio para evitar que Streamlit lo renderice como bloque de código Markdown
            html_cards += (
f"""<div style="background: white; border-top: 4px solid {border_color}; border-radius: 8px; padding: 18px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-left: 1px solid #f1f5f9; border-right: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;">
<div style="font-size: 13.5px; color: #475569; font-weight: bold; margin-bottom: 10px;">{item["Escenario"]}</div>
<div style="font-size: 12.5px; color: #64748b; margin-bottom: 8px;">{saldo_str}</div>
<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e2e8f0;">
<div style="font-size: 11.5px; color: #94a3b8; text-transform: uppercase; font-weight: 600;">Incremento de Capital para su Pensión</div>
<div style="font-size: 22px; color: {border_color}; font-weight: 800; margin-top: 4px;">{inversion_str}</div>
</div>
</div>"""
            )
        html_cards += "</div>"
        st.markdown(html_cards, unsafe_allow_html=True)

        st.divider()

        chart_b64 = ""
        try:
            import matplotlib.pyplot as plt
            import io
            import base64
            from matplotlib.ticker import FuncFormatter
            
            fig, ax = plt.subplots(figsize=(8, 4))
            escenarios_nombres = [item['Escenario'].split('(')[0].strip() for item in compare_data]
            ahorros = [item['Ahorro'] for item in compare_data]
            colores = [item['Color'] for item in compare_data]
            
            bars = ax.barh(escenarios_nombres, ahorros, color=colores)
            
            ax.set_xlabel('Incremento de Capital para su Pensión (CLP)', fontsize=10, fontweight='bold', color='#334155')
            ax.set_title('Comparación de Beneficio Fiscal por Escenario', fontsize=12, fontweight='bold', color='#0f172a', pad=15)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cbd5e1')
            ax.spines['bottom'].set_color('#cbd5e1')
            ax.invert_yaxis()
            
            def millions_formatter(x, pos):
                if x >= 1e6:
                    return f'${x*1e-6:,.0f}M'
                elif x > 0:
                    return f'${x:,.0f}'
                return '$0'
            ax.xaxis.set_major_formatter(FuncFormatter(millions_formatter))
            
            max_ahorro = max(ahorros) if max(ahorros) > 0 else 1000
            for bar in bars:
                width = bar.get_width()
                label_x_pos = width + (max_ahorro * 0.02)
                ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'${width:,.0f}', va='center', fontsize=9, fontweight='bold', color='#1e293b')
                
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            chart_b64 = "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
        except Exception as e:
            pass

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
            "ganancias_capital": ganancias_capital,
            "rag_response": rag_response,
            "compare_data": compare_data,
            "chart_b64": chart_b64,
            "df_rentas": df_rentas_final.to_dict(orient="records") if df_rentas_final is not None else []
        }
        
        pdf_path = f"reliquidacion_{rut_buscado or 'cliente'}.pdf"
        
        try:
            generate_reliquidacion_pdf(data_pdf, pdf_path)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                
            st.download_button(
                label="📄 Descargar Informe Reliquidación (PDF)",
                data=pdf_bytes,
                file_name=f"Informe_Reliquidacion_{rut_buscado or 'cliente'}.pdf",
                mime="application/pdf",
                width="stretch",
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
        
    if st.button("📊 Generar Reporte Comparativo (PDF)", type="primary", width="stretch"):
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

def render_cuenta2_simulator():
    from src.osint.indicadores import get_uf_info
    from src.utils.simulators.cuenta2_simulator import Cuenta2Simulator, DepositoCuenta2
    
    uf_info = get_uf_info()
    uf_val = uf_info["valor"]
    
    st.markdown("## 📊 Altus AI: Simulador Retiro Cuenta 2 (Optimización Tributaria)")
    st.markdown("Herramienta para calcular la rentabilidad real de fondos en AFP y su impacto en el Impuesto Global Complementario al retirar, con foco en seguros con ahorro.")
    
    fecha_uf = uf_info.get("fecha", "Desconocida")
    estado_uf = "⚠️ Valor de resguardo local" if uf_info.get("is_fallback") else "✅ API en línea"
    st.info(f"**📌 Valores tributarios utilizados:** UF = ${uf_val:,.2f} (Última actualización: {fecha_uf} | {estado_uf})")
    
    sim = Cuenta2Simulator(uf_actual=uf_val)
    
    st.markdown("### 👤 Ficha del Cliente")
    col_c1, col_c2 = st.columns(2)
    rut_buscado = col_c1.text_input("RUT del Cliente", placeholder="Ej: 12345678-9", key="rut_c2")
    
    nombre_cliente = ""
    if rut_buscado:
        from src.database.connection import SessionLocal
        from src.database.models import Prospect
        from sqlalchemy import func
        db = SessionLocal()
        try:
            rut_clean = rut_buscado.replace(".", "").replace("-", "").strip().upper()
            prospect = db.query(Prospect).filter(
                func.replace(func.replace(func.upper(Prospect.rut), '.', ''), '-', '') == rut_clean
            ).first()
            if prospect:
                # `prospect` uses `nombres` and `apellidos` (like in Reliquidacion) or `nombre`? 
                # Let's use what's in reliquidacion_simulator: `prospect.nombres` and `prospect.apellidos`
                if hasattr(prospect, 'nombres') and hasattr(prospect, 'apellidos'):
                    nombre_cliente = f"{prospect.nombres or ''} {prospect.apellidos or ''}".strip()
                elif hasattr(prospect, 'nombre'):
                    nombre_cliente = prospect.nombre
        finally:
            db.close()
            
    nombre_final = col_c2.text_input("Nombre Completo", value=nombre_cliente, placeholder="Nombre del cliente", key=f"nom_c2_{rut_buscado}")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 1. Datos de la Cuenta 2")
        c1_a, c1_b = st.columns(2)
        afp_origen = c1_a.selectbox("AFP", ["Capital", "Cuprum", "Habitat", "Modelo", "PlanVital", "Provida", "Uno"])
        multifondo = c1_b.selectbox("Multifondo", ["A", "B", "C", "D", "E"])
        
        st.markdown("#### Historial de Depósitos")
        st.write("Ingresa la fecha y monto original de los depósitos. El sistema calculará automáticamente la corrección monetaria (UF histórica).")
        
        import datetime
        if "df_depositos" not in st.session_state:
            st.session_state.df_depositos = pd.DataFrame({
                "Fecha": [datetime.date(2019, 1, 1)],
                "Monto CLP": [300000000.0]
            })
            
        edited_df = st.data_editor(
            st.session_state.df_depositos, 
            num_rows="dynamic",
            width="stretch",
            key="editor_depositos",
            column_config={
                "Fecha": st.column_config.DateColumn("Fecha (DD/MM/YYYY)", format="DD/MM/YYYY"),
                "Monto CLP": st.column_config.NumberColumn("Monto CLP", default=0.0, min_value=0.0)
            }
        )
        
        depositos = []
        from src.osint.indicadores import get_uf_historica
        
        for idx, row in edited_df.iterrows():
            m_clp = row.get("Monto CLP")
            if pd.isna(m_clp) or m_clp <= 0:
                continue
                
            if pd.isna(row["Fecha"]):
                fecha_str = "01-01-2020"
            else:
                # Si es un objeto date/datetime, lo formateamos, sino asume que ya es string
                fecha_str = row["Fecha"].strftime('%d-%m-%Y') if hasattr(row["Fecha"], 'strftime') else str(row["Fecha"])
            
            # Fetch UF historical on the fly
            uf_hist = get_uf_historica(fecha_str)
            if uf_hist and uf_hist > 0:
                monto_uf = m_clp / uf_hist
            else:
                monto_uf = 0
                
            depositos.append(DepositoCuenta2(
                fecha=fecha_str,
                monto_clp=m_clp,
                monto_uf=monto_uf
            ))
            
        saldo_actual_clp = st.number_input("Saldo Actual en Cuenta 2 (CLP)", min_value=0, value=600000000, step=1000000, format="%d")
        
        st.markdown("### 2. Parámetros del Retiro")
        monto_a_retirar = st.number_input("Monto a Retirar (CLP)", min_value=0, max_value=int(saldo_actual_clp) if saldo_actual_clp > 0 else 0, value=int(saldo_actual_clp), step=1000000, format="%d")
        
        sugerir_4000 = st.checkbox("Sugerir mantener 4.000 UF exentas de Impuesto a la Herencia en Cuenta 2", value=True)
        
    with c2:
        st.markdown("### 3. Ingresos y Rentas (Año Actual)")
        st.write("Estos datos determinan la tasa del IGC base a la cual se sumará la ganancia del retiro.")
        
        sueldo_anual = st.number_input("Sueldo Bruto Anual / Pensión (CLP)", min_value=0, value=36000000, step=1000000, format="%d")
        honorarios = st.number_input("Honorarios Anuales Brutos (CLP)", min_value=0, value=0, step=1000000, format="%d")
        
        # Estimar impuesto único retenido asumiendo sueldo parejo
        estimated_tax = 0
        if sueldo_anual > 0:
            renta_dict = sim.reliquidador.calcular_renta_tributable(
                sueldo_bruto_mensual=sueldo_anual / 12,
                afp_name="Capital", # asumiendo genérico
                pct_salud=7.0,
                descuento_cesantia=False,
                tipo_afiliado="Pensionado no cotizante"
            )
            base_anual = renta_dict["renta_tributable_mensual"] * 12
            estimated_tax = int(sim.reliquidador.calcular_igc(base_anual))
            
        ret_sueldos = st.number_input("Impuesto Único Retenido (Sueldos)", min_value=0, value=estimated_tax, step=100000, format="%d", help="Autocalculado asumiendo sueldo estable. Ajuste si tiene el dato real.")
        
        from src.utils.finance.tax_constants import get_current_retention_rate
        rate = get_current_retention_rate()
        ret_honorarios = st.number_input(f"Retención Boletas ({rate*100}%)", min_value=0, value=int(honorarios * rate), step=100000, format="%d")
        
    st.divider()
    
    if st.button("📊 Generar Simulación de Retiro", type="primary", width="stretch"):
        with st.spinner("Calculando impacto tributario e IGC..."):
            renta_info = sim.calcular_rentabilidad_real(saldo_actual_clp, depositos)
            estrategia = sim.evaluar_estrategia_retiro(
                saldo_actual_clp, 
                renta_info["rentabilidad_real_clp"], 
                monto_a_retirar, 
                sugerir_4000
            )
            
            impuestos = sim.simular_impuestos(
                sueldo_anual_bruto=sueldo_anual,
                honorarios_anuales=honorarios,
                retencion_sueldos=ret_sueldos,
                retencion_honorarios=ret_honorarios,
                rentabilidad_tributable_retiro=estrategia["rentabilidad_retirada_tributable"]
            )
            
            st.markdown(f"### 📊 Resultados de la Operación en {afp_origen} Fondo {multifondo}")
            
            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric("Rentabilidad Nominal Acumulada", f"${renta_info['rentabilidad_nominal_clp']:,.0f} CLP", f"Aporte base: ${renta_info['aporte_nominal_clp']:,.0f} CLP", delta_color="normal")
            col_res2.metric("Inflación Acumulada", f"${renta_info['inflacion_acumulada_clp']:,.0f} CLP", f"Costo histórico: {renta_info['costo_historico_uf']:,.2f} UF", delta_color="inverse")
            col_res3.metric("Rentabilidad Real Total", f"${renta_info['rentabilidad_real_clp']:,.0f} CLP", "Ganancia sujeta a impuesto", delta_color="normal")
            
            st.divider()
            
            c_ret1, c_ret2 = st.columns(2)
            c_ret1.metric("Rentabilidad Tributable a Retirar", f"${estrategia['rentabilidad_retirada_tributable']:,.0f} CLP", f"Basado en retiro de ${monto_a_retirar:,.0f}")
            
            st.markdown("#### Impacto Tributario IGC (Próxima Operación Renta)")
            df_imp = pd.DataFrame([
                {"Escenario": "1. Sin Retiro de Cuenta 2", "IGC Estimado": f"${impuestos['igc_base']:,.0f}"},
                {"Escenario": f"2. Retirando ${monto_a_retirar:,.0f}", "IGC Estimado": f"${impuestos['igc_con_retiro']:,.0f}"},
            ])
            st.table(df_imp)
            
            st.markdown(f"""
            <div style='background-color:#7f1d1d; padding: 20px; border-radius:10px; border-left: 5px solid #ef4444; margin-bottom: 20px;'>
                <h4 style='color:white; margin:0;'>Sobretasa de Impuesto por Retiro (Extra a pagar)</h4>
                <h2 style='color:#fca5a5; margin:0;'>${impuestos['impuesto_adicional_por_retiro']:,.0f} CLP</h2>
                <p style='color:#fecaca; margin:0;'>Este monto se deberá desembolsar en Abril del próximo año al SII. Tasa marginal: {impuestos['tramo_marginal_con_retiro']:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            if estrategia["recomendacion_herencia"]:
                if "⚠️" in estrategia["recomendacion_herencia"]:
                    st.warning(estrategia["recomendacion_herencia"])
                else:
                    st.success(estrategia["recomendacion_herencia"])
                    
            st.info("💡 **Estrategia Altus:** Retirar de forma escalonada en varios años tributarios permite diluir la ganancia de capital en tramos menores de IGC y optimizar la carga impositiva global.")
            
    st.divider()
    
    st.markdown("### 📈 Proyección y Propuesta de Inversión (Cuenta 2 / Fondos Mutuos)")
    st.write("Genera una propuesta formal proyectando capitalización, exenciones tributarias de 30 UTM y beneficio sucesorio (Art 72).")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    monto_apertura = col_p1.number_input("Monto de Apertura (CLP)", min_value=0, value=10000000, step=1000000)
    aporte_mensual = col_p2.number_input("Aporte Mensual (CLP)", min_value=0, value=200000, step=50000)
    horizonte = col_p3.number_input("Horizonte de Inversión (Años)", min_value=1, max_value=40, value=10)
    
    col_p4, col_p5 = st.columns(2)
    perfil_fondo = col_p4.selectbox("Perfil / Multifondo Sugerido", ["Conservador (Fondo E) - ~4.0%", "Moderado (Fondo C) - ~6.5%", "Agresivo (Fondo A) - ~8.5%"])
    
    tasa_default = 6.5
    if "Agresivo" in perfil_fondo: tasa_default = 8.5
    elif "Conservador" in perfil_fondo: tasa_default = 4.0
    
    tasa_esperada = col_p5.number_input("Tasa Anualizada Esperada (%)", min_value=0.0, value=tasa_default, step=0.5)
    
    # Generate data for PDF directly
    try:
        from src.osint.indicadores import get_utm_today
        utm_val = get_utm_today()
        
        proyeccion = sim.proyectar_inversion(
            monto_apertura_clp=monto_apertura,
            aporte_mensual_clp=aporte_mensual,
            horizonte_anios=horizonte,
            tasa_anual_esperada=tasa_esperada,
            utm_actual=utm_val
        )
        
        data_pdf = {
            "nombre": nombre_final,
            "rut": rut_buscado,
            "horizonte_anios": proyeccion["horizonte_anios"],
            "monto_apertura": monto_apertura,
            "aporte_mensual": aporte_mensual,
            "tasa_anual": proyeccion["tasa_anual_esperada"],
            "total_aportes": proyeccion["total_aportes"],
            "rentabilidad_total": proyeccion["rentabilidad_total"],
            "saldo_final": proyeccion["saldo_final_esperado"],
            "rentabilidad_exenta": proyeccion["rentabilidad_exenta_estimada"],
            "rentabilidad_afecta": proyeccion["rentabilidad_afecta_estimada"],
            "limite_4000_uf_clp": 4000 * uf_val
        }
        
        from src.utils.pdf_generator_cuenta2 import generate_cuenta2_pdf
        pdf_path = f"propuesta_cuenta2_{rut_buscado or 'cliente'}.pdf"
        generate_cuenta2_pdf(data_pdf, pdf_path)
        
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        st.download_button(
            label="📄 Descargar Propuesta Cuenta 2 (PDF)",
            data=pdf_bytes,
            file_name=f"Propuesta_Cuenta2_{rut_buscado or 'cliente'}.pdf",
            mime="application/pdf",
            width="stretch",
            type="primary"
        )
    except Exception as e:
        st.error(f"Error preparando PDF de Cuenta 2: {e}")


def render_dpe_simulator():
    from src.utils.simulators.dpe_simulator import DPESimulator
    from src.utils.pdf_generator_dpe import generate_dpe_pdf
    
    st.markdown("## 💸 Altus AI: Rescate de Excesos AFP (DPE)")
    st.markdown("Analiza automáticamente Certificados de Cotizaciones de AFP para encontrar Pagos en Exceso por múltiples empleadores.")
    
    st.markdown("### 1. Ficha del Prospecto")
    
    modo_demo = st.toggle("Activar Modo Demo (Autocompletar datos ficticios)", key="demo_dpe")
    
    c_rut, c_nom = st.columns(2)
    rut_default = "12345678-9" if modo_demo else ""
    rut_buscado = c_rut.text_input("RUT del Cliente", value=rut_default, placeholder="Ej: 12345678-9", key="dpe_rut_input")
    
    nombre_cliente = "Cliente Demo DPE" if modo_demo else ""
    if rut_buscado and not modo_demo:
        from src.database.connection import SessionLocal
        from src.database.models import Prospect
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
            
    nombre = c_nom.text_input("Nombre Completo", value=nombre_cliente, placeholder="Ej. Dr. Juan Pérez", key=f"dpe_nombre_input_{rut_buscado}")
    
    st.markdown("### 2. Carga de Certificado (PDF o Excel)")
    st.info("Sube el **'Certificado de Cotizaciones Obligatorias'** descargado desde la AFP del prospecto.")
    uploaded_file = st.file_uploader("Certificado Histórico AFP (.pdf, .xlsx, .csv)", type=["pdf", "xlsx", "xls", "csv"], key="dpe_pdf_uploader")
    
    if uploaded_file and nombre:
        if st.button("Analizar con IA (Gemini)", type="primary"):
            with st.spinner("Analizando tabla de cotizaciones con IA... Esto puede tardar unos segundos."):
                simulator = DPESimulator()
                result = simulator.analyze_file(uploaded_file.getvalue(), uploaded_file.name)
                
                if not result.get("success"):
                    st.error(f"Error en el análisis: {result.get('error')}")
                else:
                    st.session_state["dpe_result"] = result
                    st.session_state["dpe_nombre"] = nombre
                    
    if "dpe_result" in st.session_state:
        res = st.session_state["dpe_result"]
        nombre_guardado = st.session_state.get("dpe_nombre", "Cliente")
        
        st.markdown("### 3. Resultados del Análisis")
        if res["total_devolucion_estimada"] > 0:
            st.success(f"¡Se han encontrado {len(res['meses_con_exceso'])} meses con excesos!")
            st.metric("Devolución Estimada (Líquida)", f"${res['total_devolucion_estimada']:,.0f} CLP")
            
            with st.expander("Ver Detalle de Meses con Exceso"):
                import pandas as pd
                df = pd.DataFrame(res["meses_con_exceso"])
                if not df.empty:
                    df = df.rename(columns={
                        "periodo": "Periodo",
                        "cantidad_empleadores": "Empleadores",
                        "renta_total": "Renta Bruta",
                        "exceso_renta": "Exceso Renta",
                        "devolucion_estimada": "Devolución"
                    })
                    
                    df["Renta Bruta"] = df["Renta Bruta"].apply(lambda x: f"${x:,.0f}".replace(",", "."))
                    df["Exceso Renta"] = df["Exceso Renta"].apply(lambda x: f"${x:,.0f}".replace(",", "."))
                    df["Devolución"] = df["Devolución"].apply(lambda x: f"${x:,.0f}".replace(",", "."))
                    
                    st.dataframe(df)
                    
            st.markdown("### 4. Asistente de Reclamo AFP")
            st.info("Utiliza esta herramienta para generar automáticamente el texto exacto que el cliente debe copiar y pegar en la solicitud online de su AFP, junto con el Anexo Técnico de prueba.")
            
            bancos_chile = [
                "Banco de Chile / Edwards", "Banco Santander", "Banco Bci", "Banco Estado",
                "Scotiabank", "Itaú", "Banco Falabella", "Banco Security",
                "Banco Consorcio", "Banco BICE", "Banco Internacional", "Otro"
            ]
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                banco_seleccionado = st.selectbox("Banco de Destino", bancos_chile)
                if banco_seleccionado == "Otro":
                    banco_seleccionado = st.text_input("Especifique el Banco")
            with col_b2:
                tipo_cuenta = st.selectbox("Tipo de Cuenta", ["Cuenta Corriente", "Cuenta Vista / CuentaRUT", "Cuenta de Ahorro"])
            with col_b3:
                num_cuenta = st.text_input("Número de Cuenta", placeholder="Ej: 123456789")
                
            periodos_str = ", ".join([m["periodo"] for m in res["meses_con_exceso"]])
            
            mensaje_reclamo = f"Estimados Señores AFP,\n\nJunto con saludar, me dirijo a ustedes para solicitar formalmente la Devolución de Pagos en Exceso (DPE) por concepto de cotizaciones previsionales obligatorias pagadas por sobre el tope imponible legal.\n\nDe acuerdo a la revisión de mi certificado histórico, existen cotizaciones que exceden el límite legal mensual (establecido en UF para cada año tributario) debido a múltiples empleadores o bonificaciones en los siguientes periodos:\n\nPeriodos detectados: {periodos_str}\n\nAdjunto a esta solicitud el Anexo Técnico con el cálculo matemático exacto y mi Certificado de Cotizaciones Históricas como respaldo.\n\nSolicito que la liquidación de estos fondos sea depositada en la siguiente cuenta bancaria de mi titularidad:\n- Banco: {banco_seleccionado}\n- Tipo de Cuenta: {tipo_cuenta}\n- Número de Cuenta: {num_cuenta}\n\nQuedo atento a la resolución dentro de los plazos normativos vigentes.\n\nAtentamente,\n{nombre_guardado}"
            
            st.markdown("**Texto generado (Cópialo y pégalo en el formulario o WhatsApp de la AFP):**")
            st.code(mensaje_reclamo, language="text")
            
            st.markdown("### 5. Documentos Listos")
            col_pdf1, col_pdf2 = st.columns(2)
            
            pdf_path = f"Reporte_Ejecutivo_DPE_{nombre_guardado.replace(' ', '_')}.pdf"
            pdf_simple_path = f"Anexo_Tecnico_DPE_{nombre_guardado.replace(' ', '_')}.pdf"
            
            data = {
                "nombre": nombre_guardado,
                "total_devolucion": res["total_devolucion_estimada"],
                "meses_con_exceso": res["meses_con_exceso"]
            }
            
            with col_pdf1:
                if generate_dpe_pdf(data, pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    st.download_button(
                        label="📄 Descargar Informe Rescate DPE (PDF)",
                        data=pdf_bytes,
                        file_name=pdf_path,
                        mime="application/pdf",
                        type="primary",
                        key="dpe_download_pdf"
                    )
            
            with col_pdf2:
                # Need to import generate_dpe_pdf_simple or ensure it's imported at the top
                from src.utils.pdf_generator_dpe import generate_dpe_pdf_simple
                if generate_dpe_pdf_simple(data, pdf_simple_path):
                    with open(pdf_simple_path, "rb") as f:
                        pdf_simple_bytes = f.read()
                    st.download_button(
                        label="📎 Descargar Anexo Técnico (Para subir a AFP)",
                        data=pdf_simple_bytes,
                        file_name=pdf_simple_path,
                        mime="application/pdf",
                        type="secondary",
                        key="dpe_download_pdf_simple"
                    )
        else:
            st.warning("No se detectaron excesos por tope imponible para múltiples empleadores en el periodo analizado.")
            
        # Alerta de validación cruzada
        if "cross_validation_warning" in res:
            if res["cross_validation_warning"]:
                st.warning("⚠️ **Validación Cruzada Fallida:** El documento PDF tiene partes complejas y las dos lecturas independientes de la IA arrojaron pequeñas diferencias matemáticas. Para un análisis 100% auditable y libre de dudas, recomendamos **subir el archivo en formato Excel (.xlsx)** que puedes descargar en la misma página de la AFP.")
            elif res["cross_validation_warning"] is False and "pdf" in uploaded_file.name.lower():
                st.success("✅ **Validación Cruzada Exitosa (Doble Motor):** El sistema escaneó el PDF dos veces de forma independiente y los montos cuadran al peso exacto. Sello de Confianza 100%.")

        with st.expander("🛠️ Ver datos crudos (JSON) extraídos por la IA (Modo Auditoría)"):
            st.write("Con esta herramienta puedes auditar lo que la IA leyó directamente del PDF para asegurarte de que no omitió nada.")
            if "raw_json" in res:
                st.code(res["raw_json"], language="json")
