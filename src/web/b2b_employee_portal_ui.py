import streamlit as st
import json
from src.database.connection import get_db
from src.database.models import EjecutivoB2B, EmpresaB2B, Prospect

def get_clean_rut(rut: str) -> str:
    if not rut: return ""
    return rut.replace(".", "").replace("-", "").upper()

def render_b2b_employee_portal(token: str):
    # Asegurar que el estado esté inicializado
    if "b2b_authenticated" not in st.session_state:
        st.session_state.b2b_authenticated = False
    if "b2b_current_view" not in st.session_state:
        st.session_state.b2b_current_view = "hub"
    
    db = next(get_db())
    ejecutivo = db.query(EjecutivoB2B).filter(EjecutivoB2B.token_acceso == token).first()

    # --- MODO DEMO FALLBACK ---
    if not ejecutivo and token.startswith("tkn_"):
        idx_str = token.split("_")[1] if "_" in token else "0"
        try:
            idx = int(idx_str)
        except:
            idx = 0
            
        class MockEmp:
            def __init__(self):
                self.razon_social = "Minera Altus Demo SpA"
        class MockExec:
            def __init__(self, idx):
                self.nombre_completo = f"Ejecutivo Minera {idx}"
                self.rut = f"11.111.111-{idx%9}"
                self.empresa_id = 1
                
        ejecutivo = MockExec(idx)
        empresa = MockEmp()
    elif not ejecutivo:
        st.error("Token de acceso inválido o expirado.")
        return
    else:
        empresa = db.query(EmpresaB2B).filter(EmpresaB2B.id == ejecutivo.empresa_id).first()

    # --- 1. PANTALLA DE LOGIN ---
    if not st.session_state.b2b_authenticated:
        _render_login_screen(ejecutivo, empresa)
        return

    # --- 2. VINCULACIÓN CON CRM PARA HERRAMIENTAS REALES ---
    # Para que las herramientas originales (Reporte 360, Simuladores) funcionen, necesitan un Prospect
    clean_rut = get_clean_rut(ejecutivo.rut)
    prospect = db.query(Prospect).filter(Prospect.rut.like(f"%{clean_rut}%") | (Prospect.rut == ejecutivo.rut)).first()
    
    if not prospect:
        # Si la empresa cargó al ejecutivo pero aún no está en el CRM central, lo creamos dinámicamente
        new_prospect = Prospect(
            rut=ejecutivo.rut,
            nombre=ejecutivo.nombre_completo,
            status_contacto="B2B Auth",
            tipo_negocio="B2B Institucional",
            observaciones=f"Empleado de: {empresa.razon_social}"
        )
        db.add(new_prospect)
        db.commit()
        db.refresh(new_prospect)
        prospect = new_prospect

    # Seteamos el prospecto activo en la sesión para que las herramientas lo lean
    st.session_state.selected_prospect_id = prospect.id

    # --- 3. ENRUTAMIENTO INTERNO DEL PORTAL ---
    if st.session_state.b2b_current_view == "hub":
        _render_hub(ejecutivo, empresa, prospect)
    elif st.session_state.b2b_current_view == "reporte_360":
        _render_tool_header("Reporte Patrimonial 360")
        
        # Inject context for Reporte 360 (Now maps to the full client profile view)
        from src.web.client_management_ui_new import render_client_profile
        st.session_state["current_client_name"] = prospect.nombre
        st.session_state["current_client_rut"] = prospect.rut
            
        render_client_profile(is_b2b=True)
    elif st.session_state.b2b_current_view == "sim_reliquidacion":
        _render_tool_header("Simulador de Reliquidación IGC")
        
        # Inject context for Reliquidacion
        st.session_state["current_client_name"] = prospect.nombre
        st.session_state["current_client_rut"] = prospect.rut
        
        from src.web.simulators_ui import render_reliquidacion_simulator
        render_reliquidacion_simulator()
    elif st.session_state.b2b_current_view == "sim_dpe":
        _render_tool_header("Simulador de Beneficios Tributarios (DPE)")
        
        # Inject context for DPE
        st.session_state["current_client_name"] = prospect.nombre
        st.session_state["current_client_rut"] = prospect.rut
        
        from src.web.simulators_ui import render_dpe_simulator
        render_dpe_simulator()
    elif st.session_state.b2b_current_view == "sim_apv":
        _render_tool_header("Simulador de Ahorro Previsional Voluntario (APV)")
        
        st.session_state["current_client_name"] = prospect.nombre
        st.session_state["current_client_rut"] = prospect.rut
        
        from src.web.simulators_ui import render_apv_simulator
        render_apv_simulator(38000) # Mock UF value
    elif st.session_state.b2b_current_view == "sim_cuenta2":
        _render_tool_header("Simulador Cuenta 2 (AFP)")
        
        st.session_state["current_client_name"] = prospect.nombre
        st.session_state["current_client_rut"] = prospect.rut
        
        from src.web.simulators_ui import render_cuenta2_simulator
        render_cuenta2_simulator()
    elif st.session_state.b2b_current_view == "sim_credito":
        _render_tool_header("Simulador Crédito vs Inversión")
        
        st.session_state["current_client_name"] = prospect.nombre
        st.session_state["current_client_rut"] = prospect.rut
        
        from src.web.simulators_ui import render_credito_vs_inversion_simulator
        render_credito_vs_inversion_simulator()

def _render_tool_header(title: str):
    st.markdown(f"## {title}")
    if st.button("⬅️ Volver al Inicio (Mi Portal)"):
        st.session_state.b2b_current_view = "hub"
        st.rerun()
    st.markdown("---")

def _render_login_screen(ejecutivo, empresa):
    st.markdown(f"""
    <div style='text-align: center; margin-top: 50px; margin-bottom: 30px;'>
        <h1 style='color: #1e293b;'>Portal Corporativo <b>{empresa.razon_social}</b></h1>
        <p style='color: #64748b; font-size: 1.1em;'>Motorizado por Altus Core</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("b2b_login_form"):
            st.markdown("### Acceso Seguro")
            rut_input = st.text_input("RUT", placeholder="Ej: 11.111.111-0")
            clave_input = st.text_input("Clave de Acceso", type="password", help="Para esta demostración, puede usar cualquier clave.")
            submit = st.form_submit_button("Ingresar a mi Perfil", type="primary", use_container_width=True)
            
            if submit:
                # Validación simple de RUT (en un caso real, validar con hash de BD)
                clean_rut_input = get_clean_rut(rut_input)
                clean_ejec_rut = get_clean_rut(ejecutivo.rut)
                
                if clean_rut_input == clean_ejec_rut:
                    st.session_state.b2b_authenticated = True
                    st.rerun()
                else:
                    st.error(f"El RUT ingresado no coincide con el asignado a este enlace. (Hint: Usa {ejecutivo.rut})")

def _render_hub(ejecutivo, empresa, prospect):
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 30px; border-radius: 12px; border: 1px solid #3b82f6; margin-bottom: 30px; color: white;'>
        <h1 style='margin:0; font-size: 2.2rem;'>Mi Panel Integral</h1>
        <p style='margin: 5px 0 0 0; color: #94a3b8; font-size: 1.1rem;'>Bienvenido, <b>{ejecutivo.nombre_completo}</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Mis Datos Personales (Sincronizados por el Empleador)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**RUT:** {prospect.rut}")
        st.markdown(f"**Nombre:** {prospect.nombre}")
    with col2:
        st.markdown(f"**Empresa:** {empresa.razon_social}")
        st.markdown(f"**Cargo/Rol:** Ejecutivo Corporativo")
    with col3:
        st.markdown(f"**Email:** {prospect.email if prospect.email else 'No registrado'}")
        st.markdown(f"**Teléfono:** {prospect.telefono if prospect.telefono else 'No registrado'}")
        
    st.markdown("---")
    st.markdown("### 🛠️ Mis Herramientas Financieras")
    st.markdown("Seleccione una herramienta para interactuar en tiempo real con sus datos.")
    
    # ROW 1
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div style='border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; height: 100%;'>
            <h3 style='margin-top:0;'>📑 Reporte 360</h3>
            <p style='color: #64748b; font-size: 0.9em;'>Genere su Análisis Patrimonial Consolidado y proyecciones dinámicas.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Reporte 360", use_container_width=True, key="btn_rep360"):
            st.session_state.b2b_current_view = "reporte_360"
            st.rerun()

    with c2:
        st.markdown("""
        <div style='border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; height: 100%;'>
            <h3 style='margin-top:0;'>⚖️ Reliquidación IGC</h3>
            <p style='color: #64748b; font-size: 0.9em;'>Simulador tributario de Global Complementario para optimizar sus declaraciones.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Simulador IGC", use_container_width=True, key="btn_igc"):
            st.session_state.b2b_current_view = "sim_reliquidacion"
            st.rerun()

    with c3:
        st.markdown("""
        <div style='border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; height: 100%;'>
            <h3 style='margin-top:0;'>🛡️ Ahorro DPE</h3>
            <p style='color: #64748b; font-size: 0.9em;'>Calculadora de beneficios fiscales mediante Depósito Convenido Institucional.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Simulador DPE", use_container_width=True, key="btn_dpe"):
            st.session_state.b2b_current_view = "sim_dpe"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ROW 2
    c4, c5, c6 = st.columns(3)
    
    with c4:
        st.markdown("""
        <div style='border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; height: 100%;'>
            <h3 style='margin-top:0;'>📈 Simulador APV</h3>
            <p style='color: #64748b; font-size: 0.9em;'>Proyecte sus beneficios fiscales a través del Ahorro Previsional Voluntario (Letra A y B).</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Simulador APV", use_container_width=True, key="btn_apv"):
            st.session_state.b2b_current_view = "sim_apv"
            st.rerun()

    with c5:
        st.markdown("""
        <div style='border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; height: 100%;'>
            <h3 style='margin-top:0;'>💰 Cuenta 2 (AFP)</h3>
            <p style='color: #64748b; font-size: 0.9em;'>Optimización de liquidez usando régimen tributario especial de Cuenta 2.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Simulador Cuenta 2", use_container_width=True, key="btn_cta2"):
            st.session_state.b2b_current_view = "sim_cuenta2"
            st.rerun()

    with c6:
        st.markdown("""
        <div style='border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; height: 100%;'>
            <h3 style='margin-top:0;'>🏦 Inversión vs Deuda</h3>
            <p style='color: #64748b; font-size: 0.9em;'>Análisis matemático: ¿Conviene prepagar su crédito o invertir ese capital?</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Comparador", use_container_width=True, key="btn_credito"):
            st.session_state.b2b_current_view = "sim_credito"
            st.rerun()
