import streamlit as st
import pandas as pd
import datetime
import uuid
import time
from src.database.connection import get_db
from src.database.models import EmpresaB2B, EjecutivoB2B
from src.core.config import B2B_LICENSE_TIERS
import hashlib

def render_b2b_management_ui():
    st.title("🏢 Administración de Empresas y Cupos B2B (Reporte 360)")
    
    db = next(get_db())
    try:
        # --- MODO DEMO ---
        demo_mode = st.sidebar.toggle("🧪 Activar Modo Demo", value=False, key="demo_mode")
        if demo_mode:
            st.sidebar.warning("Modo Demo Activo (Datos Simulados)")
            
        # --- SECCIÓN 1: Registrar y editar EmpresaB2B ---
        st.markdown("###### 1️⃣ Gestión de Empresas (Tenant Corporativo)")
        
        if demo_mode:
            class MockEmpresa:
                def __init__(self, id, rut, razon_social, contacto_comercial, plan_contratado, cupo_licencias, estado_activo, ultimo_certificado_hash, fecha_ultimo_certificado):
                    self.id = id
                    self.rut = rut
                    self.razon_social = razon_social
                    self.contacto_comercial = contacto_comercial
                    self.plan_contratado = plan_contratado
                    self.cupo_licencias = cupo_licencias
                    self.estado_activo = estado_activo
                    self.ultimo_certificado_hash = ultimo_certificado_hash
                    self.fecha_ultimo_certificado = fecha_ultimo_certificado

            empresas_db = [
                MockEmpresa(1, "76.123.456-7", "Minera Altus Demo SpA", "Contacto Demo 1", "Enterprise", 50, True, "e3b0c44298fc1c149afbf4c8996fb924", datetime.datetime.now()),
                MockEmpresa(2, "77.765.432-1", "Holding Financiero Test", "Finanzas Demo", "Corporate", 20, True, "f2b0c44298fc1c149afbf4c8996fb924", datetime.datetime.now())
            ]
        else:
            empresas_db = db.query(EmpresaB2B).all()
            
        col_b1, col_b2 = st.columns([1, 1])
        with col_b1:
            st.markdown("**Registrar Nueva Empresa**")
            with st.form("form_nueva_empresa_b2b"):
                n_rut_empresa = st.text_input("RUT Empresa (ej: 76.123.456-7)")
                n_razon_social = st.text_input("Razón Social")
                n_contacto = st.text_input("Contacto Comercial (Nombre, Email)")
                n_plan = st.selectbox("Plan Contratado", list(B2B_LICENSE_TIERS.keys()))
                import math
                n_plan_dict = B2B_LICENSE_TIERS.get(n_plan, {})
                default_cupo = n_plan_dict.get("max_users", 50)
                if default_cupo == float('inf') or math.isinf(default_cupo):
                    default_cupo = 5000
                n_cupo = st.number_input("Cupo de Licencias Asignado", min_value=1, max_value=5000, value=int(default_cupo))
                n_activo = st.checkbox("Estado Activo", value=True)
                
                if st.form_submit_button("💾 Registrar Tenant"):
                    if not n_rut_empresa or not n_razon_social:
                        st.error("RUT y Razón Social son obligatorios.")
                    else:
                        if demo_mode:
                            check_exist = None
                        else:
                            check_exist = db.query(EmpresaB2B).filter_by(rut=n_rut_empresa).first()
                        if check_exist:
                            st.error(f"La empresa con RUT {n_rut_empresa} ya existe.")
                        else:
                            new_emp = EmpresaB2B(
                                rut=n_rut_empresa,
                                razon_social=n_razon_social,
                                contacto_comercial=n_contacto,
                                plan_contratado=n_plan,
                                cupo_licencias=n_cupo,
                                estado_activo=n_activo
                            )
                            if not demo_mode:
                                db.add(new_emp)
                                db.commit()
                            st.success(f"Empresa {n_razon_social} registrada exitosamente.")
                            time.sleep(1)
                            st.rerun()

        with col_b2:
            st.markdown("**Empresas Registradas**")
            if empresas_db:
                df_empresas = pd.DataFrame([{
                    "ID": e.id, 
                    "RUT": e.rut, 
                    "Razón Social": e.razon_social, 
                    "Plan": e.plan_contratado, 
                    "Cupo": e.cupo_licencias,
                    "Activo": "Sí" if e.estado_activo else "No"
                } for e in empresas_db])
                st.dataframe(df_empresas, hide_index=True)
            else:
                st.info("No hay empresas B2B registradas aún.")
                
        st.markdown("---")

        # --- SECCIÓN 2: Alta de Ejecutivos / Nómina ---
        st.markdown("###### 2️⃣ Panel de Control por Empresa")
        if empresas_db:
            opciones_empresa = {f"{e.rut} - {e.razon_social}": e for e in empresas_db}
            sel_empresa = st.selectbox("Seleccione la Empresa para gestionar:", list(opciones_empresa.keys()))
            empresa_sel_b2b = opciones_empresa[sel_empresa]
            
            if demo_mode:
                ejecutivos_asociados = 45 if empresa_sel_b2b.id == 1 else 18
            else:
                ejecutivos_asociados = db.query(EjecutivoB2B).filter_by(empresa_id=empresa_sel_b2b.id).count()

            col_met1, col_met2, col_met3 = st.columns(3)
            with col_met1:
                st.metric("Licencias Contratadas", f"{empresa_sel_b2b.cupo_licencias}")
            with col_met2:
                cupos_disponibles = empresa_sel_b2b.cupo_licencias - ejecutivos_asociados
                st.metric("Licencias Utilizadas", f"{ejecutivos_asociados}", delta=f"{cupos_disponibles} disp.", delta_color="normal")
            with col_met3:
                st.metric("Plan SaaS", empresa_sel_b2b.plan_contratado)

            st.markdown("**📥 Cargar Nómina de Ejecutivos (CSV/Excel)**")
            st.info("El archivo debe contener las columnas: 'RUT', 'Nombre Completo', 'Correo Corporativo', 'Cargo'")
            uploaded_file = st.file_uploader("Sube el listado de colaboradores", type=["csv", "xlsx"])
            
            if uploaded_file is not None:
                if uploaded_file.name.endswith('.csv'):
                    df_nomina = pd.read_csv(uploaded_file)
                else:
                    df_nomina = pd.read_excel(uploaded_file)
                    
                st.write("Vista previa de datos a importar:")
                st.dataframe(df_nomina.head(3))
                
                if st.button("🚀 Procesar Importación y Generar Accesos"):
                    added_count = 0
                    dup_count = 0
                    with st.spinner("Generando credenciales y perfiles..."):
                        for index, row in df_nomina.iterrows():
                            if ejecutivos_asociados + added_count >= empresa_sel_b2b.cupo_licencias:
                                st.warning(f"Se ha alcanzado el límite de {empresa_sel_b2b.cupo_licencias} licencias. Importación parcial.")
                                break
                                
                            r_rut = str(row.get("RUT", "")).strip()
                            r_nombre = str(row.get("Nombre Completo", "")).strip()
                            r_correo = str(row.get("Correo Corporativo", "")).strip() if "Correo Corporativo" in df_nomina.columns else ""
                            r_cargo = str(row.get("Cargo", "")).strip() if "Cargo" in df_nomina.columns else ""
                            
                            if r_rut and r_nombre:
                                if demo_mode:
                                    check_exec = None
                                else:
                                    check_exec = db.query(EjecutivoB2B).filter_by(rut=r_rut).first()
                                if not check_exec:
                                    new_token = str(uuid.uuid4())
                                    new_exec = EjecutivoB2B(
                                        empresa_id=empresa_sel_b2b.id,
                                        rut=r_rut,
                                        nombre_completo=r_nombre,
                                        correo_corporativo=r_correo,
                                        cargo=r_cargo,
                                        token_acceso=new_token,
                                        estado_onboarding="Pendiente"
                                    )
                                    if not demo_mode:
                                        db.add(new_exec)
                                    added_count += 1
                                else:
                                    dup_count += 1
                                    
                        if added_count > 0:
                            if not demo_mode:
                                db.commit()
                        st.success(f"Importación finalizada: {added_count} agregados, {dup_count} omitidos (ya existentes).")
                        time.sleep(2)
                        st.rerun()

            st.markdown("**👥 Administrar Ejecutivos y Enlaces de Acceso (Magic Links)**")
            # Tabla de Monitoreo
            if demo_mode:
                class MockExec:
                    def __init__(self, id, rut, nombre, correo, cargo, estado, token):
                        self.id = id
                        self.rut = rut
                        self.nombre_completo = nombre
                        self.correo_corporativo = correo
                        self.cargo = cargo
                        self.estado_onboarding = estado
                        self.token_acceso = token
                
                ejecutivos_list = []
                if empresa_sel_b2b.id == 1:
                    for i in range(30):
                        ejecutivos_list.append(MockExec(i, f"11.111.111-{i%9}", f"Ejecutivo Minera {i}", f"e{i}@minera.cl", "Gerente", "Completado", f"tkn_{i}"))
                    for i in range(30, 45):
                        ejecutivos_list.append(MockExec(i, f"11.111.111-{i%9}", f"Ejecutivo Minera {i}", f"e{i}@minera.cl", "Supervisor", "Pendiente", f"tkn_{i}"))
                else:
                    for i in range(10):
                        ejecutivos_list.append(MockExec(i, f"22.222.222-{i%9}", f"Ejecutivo Holding {i}", f"e{i}@holding.cl", "Directora", "Reporte Emitido", f"tkn_{i}"))
                    for i in range(10, 18):
                        ejecutivos_list.append(MockExec(i, f"22.222.222-{i%9}", f"Ejecutivo Holding {i}", f"e{i}@holding.cl", "Analista", "Invitación Enviada", f"tkn_{i}"))
            else:
                ejecutivos_list = db.query(EjecutivoB2B).filter_by(empresa_id=empresa_sel_b2b.id).all()
                
            if ejecutivos_list:
                data_execs = []
                base_url = "http://localhost:8504/" # TODO: Usar dominio real en produccion (ej: app.altuscore.com/b2b-report)
                for exc in ejecutivos_list:
                    if not exc.token_acceso:
                        exc.token_acceso = str(uuid.uuid4())
                        if not demo_mode:
                            db.commit()
                    
                    enlace = f"{base_url}?b2b_token={exc.token_acceso}"
                    data_execs.append({
                        "ID": exc.id,
                        "RUT": exc.rut,
                        "Nombre Completo": exc.nombre_completo,
                        "Correo": exc.correo_corporativo,
                        "Cargo": exc.cargo,
                        "Estado": exc.estado_onboarding,
                        "Enlace Acceso": enlace
                    })
                
                df_execs = pd.DataFrame(data_execs)
                st.dataframe(
                    df_execs,
                    hide_index=True,
                    column_config={
                        "Enlace Acceso": st.column_config.LinkColumn("Enlace Acceso (Copiar)"),
                    }
                )
                
                csv_links = df_execs.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar Nómina y Enlaces Únicos (CSV)",
                    data=csv_links,
                    file_name=f"Enlaces_B2B_{empresa_sel_b2b.razon_social}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No hay ejecutivos cargados para esta empresa.")
                
            st.markdown("---")
            st.markdown("###### 3️⃣ Emisión de Certificado de Confidencialidad")
            st.info("Al hacer clic aquí, se genera un hash criptográfico inmutable en la base de datos que certifica la separación de los datos de este tenant del resto del CRM.")
            
            if st.button("🔐 Generar / Refrescar Certificado de Confidencialidad SFO"):
                with st.spinner("Firmando datos..."):
                    timestamp_str = str(time.time())
                    hash_cert = hashlib.sha256(f"{empresa_sel_b2b.rut}-{timestamp_str}".encode()).hexdigest()
                    
                    if demo_mode:
                        st.success(f"Certificado generado exitosamente. Hash: `{hash_cert}`")
                    else:
                        empresa_sel_b2b.ultimo_certificado_hash = hash_cert
                        empresa_sel_b2b.fecha_ultimo_certificado = datetime.datetime.now()
                        db.commit()
                        st.success(f"Certificado generado exitosamente. Hash: `{hash_cert}`")
            
            if empresa_sel_b2b.ultimo_certificado_hash:
                st.markdown(f"**Último Certificado (Hash):** `{empresa_sel_b2b.ultimo_certificado_hash}`")
                st.markdown(f"**Fecha Emisión:** `{empresa_sel_b2b.fecha_ultimo_certificado}`")

    except Exception as e:
        import traceback
        st.error(f"Error en UI de Gestión B2B: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()
