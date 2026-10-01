import re
import datetime

with open('src/web/company_management_ui.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Insert demo toggle and mock empresas
mock_empresas = '''        # --- MODO DEMO ---
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
            empresas_db = db.query(EmpresaB2B).all()'''

old_section_1 = '''        # --- SECCIÓN 1: Registrar y editar EmpresaB2B ---
        st.markdown("###### 1️⃣ Gestión de Empresas (Tenant Corporativo)")
        
        empresas_db = db.query(EmpresaB2B).all()'''
code = code.replace(old_section_1, mock_empresas)

# 2. Db add and commit inside submit_new_emp
old_db_add = '''                            db.add(new_emp)
                            db.commit()'''
new_db_add = '''                            if not demo_mode:
                                db.add(new_emp)
                                db.commit()'''
code = code.replace(old_db_add, new_db_add)

# 3. ejecutivos_asociados count
old_ejec = '''                    ejecutivos_asociados = db.query(EjecutivoB2B).filter_by(empresa_id=empresa_sel_b2b.id).count()'''
new_ejec = '''                    if demo_mode:
                        ejecutivos_asociados = 45 if empresa_sel_b2b.id == 1 else 18
                    else:
                        ejecutivos_asociados = db.query(EjecutivoB2B).filter_by(empresa_id=empresa_sel_b2b.id).count()'''
code = code.replace(old_ejec, new_ejec)

# 4. Tabla de monitoreo 
old_list = '''            # Tabla de Monitoreo
            ejecutivos_list = db.query(EjecutivoB2B).filter_by(empresa_id=empresa_sel_b2b.id).all()
            if ejecutivos_list:'''
new_list = '''            # Tabla de Monitoreo
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
                
            if ejecutivos_list:'''
code = code.replace(old_list, new_list)

# 5. Token commit
old_tok = '''                    if not exc.token_acceso:
                        exc.token_acceso = str(uuid.uuid4())
                        db.commit()'''
new_tok = '''                    if not exc.token_acceso:
                        exc.token_acceso = str(uuid.uuid4())
                        if not demo_mode:
                            db.commit()'''
code = code.replace(old_tok, new_tok)

# 6. Auditing hash check
old_aud = '''                    # Buscar en la base de datos
                    empresa_verificada = db.query(EmpresaB2B).filter(EmpresaB2B.ultimo_certificado_hash == hash_to_verify).first()'''
new_aud = '''                    # Buscar en la base de datos
                    if demo_mode:
                        empresa_verificada = empresas_db[0] if "e3b" in hash_to_verify or "f2b" in hash_to_verify else None
                    else:
                        empresa_verificada = db.query(EmpresaB2B).filter(EmpresaB2B.ultimo_certificado_hash == hash_to_verify).first()'''
code = code.replace(old_aud, new_aud)

# 7. Check exist rut
old_chk = '''                        check_exist = db.query(EmpresaB2B).filter_by(rut=n_rut_empresa).first()'''
new_chk = '''                        if demo_mode:
                            check_exist = None
                        else:
                            check_exist = db.query(EmpresaB2B).filter_by(rut=n_rut_empresa).first()'''
code = code.replace(old_chk, new_chk)

# 8. Certificate generation
old_cert = '''                        # 2. Persistir en la BD (huella de auditoría)
                        empresa_sel_b2b.ultimo_certificado_hash = hash_cert
                        empresa_sel_b2b.fecha_ultimo_certificado = datetime.datetime.now()
                        db.commit()'''
new_cert = '''                        # 2. Persistir en la BD (huella de auditoría)
                        empresa_sel_b2b.ultimo_certificado_hash = hash_cert
                        empresa_sel_b2b.fecha_ultimo_certificado = datetime.datetime.now()
                        if not demo_mode:
                            db.commit()'''
code = code.replace(old_cert, new_cert)

old_cert2 = '''                        # 2. Persistir en la BD (huella de auditoría)
                        empresa_sel_b2b.ultimo_certificado_hash = hash_cert
                        empresa_sel_b2b.fecha_ultimo_certificado = datetime.now()
                        db.commit()'''
new_cert2 = '''                        # 2. Persistir en la BD (huella de auditoría)
                        empresa_sel_b2b.ultimo_certificado_hash = hash_cert
                        empresa_sel_b2b.fecha_ultimo_certificado = datetime.now()
                        if not demo_mode:
                            db.commit()'''
code = code.replace(old_cert2, new_cert2)

# 9. Extra commits on invite dispatch
old_dispatch = '''                            db.commit()
                            try:
                                from src.utils.gcs_sync import safe_upload_with_streamlit_ui'''
new_dispatch = '''                            if not demo_mode:
                                db.commit()
                            try:
                                from src.utils.gcs_sync import safe_upload_with_streamlit_ui'''
code = code.replace(old_dispatch, new_dispatch)


old_imp_commit = '''                            if added_count > 0:
                                db.commit()'''
new_imp_commit = '''                            if added_count > 0:
                                if not demo_mode:
                                    db.commit()'''
code = code.replace(old_imp_commit, new_imp_commit)

with open('src/web/company_management_ui.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Done!')
