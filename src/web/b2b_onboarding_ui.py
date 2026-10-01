import streamlit as st
import json
from src.database.connection import get_db
from src.database.models import EjecutivoB2B, EmpresaB2B
from src.security.encryption import decrypt_data

def render_b2b_onboarding(token):
    db = next(get_db())
    
    # Desencriptar si el token viene encriptado y así se guardó, pero si lo guardamos crudo o lo pasamos crudo...
    # Verificamos si existe directamente, o si necesitamos desencriptarlo primero
    ejecutivo = db.query(EjecutivoB2B).filter(EjecutivoB2B.token_acceso == token).first()
    
    if not ejecutivo:
        if token and token.startswith("tkn_"):
            # Modo Demo
            class MockEmp:
                def __init__(self):
                    self.razon_social = "Minera Altus Demo SpA"
            class MockExec:
                def __init__(self, t):
                    self.empresa_id = 1
                    self.nombre_completo = "Ejecutivo Demo"
                    self.token_acceso = t
                    self.metadata_json = None
                    self.rut = "11.111.111-1"
                    self.estado_onboarding = "Pendiente"
            ejecutivo = MockExec(token)
            empresa = MockEmp()
        else:
            st.error("El token de acceso es inválido o ha expirado. Por favor, verifique el enlace provisto por su empresa.")
            return
    else:
        empresa = db.query(EmpresaB2B).filter(EmpresaB2B.id == ejecutivo.empresa_id).first()
    
    st.title("Levantamiento Patrimonial 360 - B2B")
    st.markdown(f"Bienvenido **{ejecutivo.nombre_completo}**. Este portal es de uso exclusivo y confidencial para los ejecutivos de **{empresa.razon_social}**.")
    st.info("🔒 **Privacidad Garantizada**: La información ingresada es estrictamente confidencial. Su empleador NO tendrá acceso a estos datos ni a su Reporte 360 final.")
    
    if "b2b_step" not in st.session_state:
        st.session_state.b2b_step = 1
        st.session_state.b2b_data = json.loads(ejecutivo.metadata_json) if ejecutivo.metadata_json else {}
        
    step = st.session_state.b2b_step
    st.progress(step / 3)
    
    if step == 1:
        st.subheader("1. Activos e Inversiones")
        with st.form("b2b_form_1"):
            inmuebles = st.number_input("Valor Comercial de Bienes Raíces (CLP)", value=st.session_state.b2b_data.get("inmuebles", 0))
            inversiones = st.number_input("Inversiones Líquidas, Acciones y Fondos Mutuos (CLP)", value=st.session_state.b2b_data.get("inversiones", 0))
            apv = st.number_input("Saldo Ahorro Previsional Voluntario (APV) (CLP)", value=st.session_state.b2b_data.get("apv", 0))
            
            if st.form_submit_button("Siguiente ->"):
                st.session_state.b2b_data.update({
                    "inmuebles": inmuebles,
                    "inversiones": inversiones,
                    "apv": apv
                })
                st.session_state.b2b_step = 2
                st.rerun()
                
    elif step == 2:
        st.subheader("2. Pasivos y Rentas")
        with st.form("b2b_form_2"):
            deuda_hipotecaria = st.number_input("Saldo Pendiente Deudas Hipotecarias (CLP)", value=st.session_state.b2b_data.get("deuda_hipotecaria", 0))
            deuda_consumo = st.number_input("Deuda de Consumo y Automotriz (CLP)", value=st.session_state.b2b_data.get("deuda_consumo", 0))
            renta_mensual = st.number_input("Renta Líquida Mensual Estimada (CLP)", value=st.session_state.b2b_data.get("renta_mensual", 0))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("<- Volver"):
                    st.session_state.b2b_step = 1
                    st.rerun()
            with col2:
                if st.form_submit_button("Siguiente ->"):
                    st.session_state.b2b_data.update({
                        "deuda_hipotecaria": deuda_hipotecaria,
                        "deuda_consumo": deuda_consumo,
                        "renta_mensual": renta_mensual
                    })
                    st.session_state.b2b_step = 3
                    st.rerun()
                    
    elif step == 3:
        st.subheader("3. Confirmación y Generación de Reporte")
        st.write("Por favor verifique que los datos ingresados reflejan razonablemente su situación actual. Estos valores se utilizarán para proyectar optimizaciones tributarias y patrimoniales en su Reporte 360.")
        
        with st.expander("Ver Resumen de Datos"):
            st.json(st.session_state.b2b_data)
        
        with st.form("b2b_form_3"):
            autorizacion = st.checkbox("Autorizo de forma expresa a Altus AI para procesar estos datos bajo estricta confidencialidad exclusivamente para generar mi Reporte 360.")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("<- Volver"):
                    st.session_state.b2b_step = 2
                    st.rerun()
            with col2:
                if st.form_submit_button("✅ Generar mi Reporte 360 Privado"):
                    if not autorizacion:
                        st.error("Debe autorizar el procesamiento confidencial de datos para continuar.")
                    else:
                        ejecutivo.metadata_json = json.dumps(st.session_state.b2b_data)
                        ejecutivo.estado_onboarding = "Reporte Emitido"
                        if not token.startswith("tkn_"):
                            db.commit()
                        st.session_state.b2b_step = 4
                        st.rerun()
                        
    elif step == 4:
        st.success("¡Levantamiento Patrimonial Completado Exitosamente!")
        st.balloons()
        
        st.markdown("Su información ha sido procesada de manera segura por el motor **Altus Core**.")
        
        try:
            from src.utils.simulators.reliquidacion_simulator import ReliquidacionSimulator
            from src.utils.simulators.dpe_simulator import DPESimulator
            from src.reporting.pdf_engine import generate_audit_pdf
            
            # 1. Obtención de parámetros de entrada
            renta_mensual = st.session_state.b2b_data.get("renta_mensual", 0)
            inmuebles = st.session_state.b2b_data.get("inmuebles", 0)
            inversiones = st.session_state.b2b_data.get("inversiones", 0)
            apv_saldo = st.session_state.b2b_data.get("apv", 0)
            deuda_hip = st.session_state.b2b_data.get("deuda_hipotecaria", 0)
            deuda_cons = st.session_state.b2b_data.get("deuda_consumo", 0)
            
            sueldo_anual = renta_mensual * 12
            
            # 2. Simulación Tributaria (Reliquidación IGC)
            sim_reliq = ReliquidacionSimulator()
            try:
                res_reliq = sim_reliq.simular_operacion_renta(
                    sueldo_anual_bruto=sueldo_anual,
                    afp_name="Habitat",
                    pct_salud=7.0,
                    honorarios_anuales=0.0,
                    retencion_sueldos=0.0,
                    retencion_honorarios=0.0,
                    apv_b_anual=0.0
                )
                igc_estimado = res_reliq.get("igc_original", 0)
                tramo = res_reliq.get("tramo_marginal_efectivo", 0)
            except Exception:
                igc_estimado = 0.0
                tramo = 0.0
                
            # 3. Simulación Depósito Convenido (DPE)
            sim_dpe = DPESimulator()
            try:
                res_dpe = sim_dpe.calcular_beneficio_deposito_convenido(renta_bruta_mensual=renta_mensual)
                ahorro_dpe = res_dpe.get("ahorro_fiscal_dpe", 0.0)
            except Exception:
                ahorro_dpe = 0.0
            
            # 4. Consolidación de Métricas Patrimoniales
            patrimonio_neto = (inmuebles + inversiones + apv_saldo) - (deuda_hip + deuda_cons)
            
            alpha_total = igc_estimado + ahorro_dpe
            
            metrics = {
                "patrimonio": f"$ {patrimonio_neto:,.0f}".replace(",", "."),
                "tac": f"Marginal: {tramo}%",
                "alpha": f"$ {alpha_total:,.0f}".replace(",", ".")
            }
            
            rows_legal = [
                ("🏢 Estructura", "Persona Natural", "Optimización B2B (Recomendado)"),
                ("💰 Carga Tributaria", f"{tramo}%", "Eficiente"),
                ("🛡️ Privacidad", "Pública", "Confidencial"),
                ("📈 Beneficio DPE", "$ 0", f"$ {ahorro_dpe:,.0f}".replace(",", "."))
            ]
            
            pdf_path = generate_audit_pdf(
                client_name=ejecutivo.nombre_completo,
                metrics=metrics,
                rows_legal=rows_legal,
                stats_p=None,
                stats_c=None,
                path_infl=None
            )
            
            st.markdown("### Su Reporte Patrimonial 360 está listo")
            st.write("A continuación puede visualizar y descargar su reporte. Recuerde que este archivo contiene información sensible.")
            
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Descargar Reporte 360 (PDF Confidencial)",
                    data=pdf_file,
                    file_name=f"Reporte_360_Confidencial_{ejecutivo.rut}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error generando el reporte: {str(e)}")
            st.error("Por favor contacte a soporte si el problema persiste.")
