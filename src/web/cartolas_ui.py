import streamlit as st
from src.intelligence.competitor_agent import CompetitorAgent
import os
import tempfile
from datetime import date, datetime
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.database.models import Prospect, ClientProfile, CartolaSummary
from src.ingestion.cartola_reader import CartolaReader
from src.intelligence.proactive_advisor import ProactiveAdvisor

def backup_interaction(rut: str, nombre: str, tipo: str, contenido: str):
    try:
        safe_name = "".join([c if c.isalnum() or c in " _-" else "" for c in nombre]).strip()
        base_dir = os.path.join("data", "clientes", f"{rut}_{safe_name}".replace(" ", "_"))
        os.makedirs(base_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(base_dir, f"{timestamp}_{tipo}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Respaldo: {tipo}\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(contenido)
    except Exception as e:
        print(f"Error guardando respaldo: {e}")

def calcular_edades(fecha_nac: date):
    hoy = date.today()
    edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
    
    # Edad actuarial: edad al cumpleaños más cercano
    try:
        cumple_este_ano = date(hoy.year, fecha_nac.month, fecha_nac.day)
    except ValueError:
        # Febrero 29
        cumple_este_ano = date(hoy.year, 3, 1)
        
    if cumple_este_ano < hoy:
        try:
            proximo_cumple = date(hoy.year + 1, fecha_nac.month, fecha_nac.day)
        except ValueError:
            proximo_cumple = date(hoy.year + 1, 3, 1)
        ultimo_cumple = cumple_este_ano
    else:
        proximo_cumple = cumple_este_ano
        try:
            ultimo_cumple = date(hoy.year - 1, fecha_nac.month, fecha_nac.day)
        except ValueError:
            ultimo_cumple = date(hoy.year - 1, 3, 1)
            
    dias_al_proximo = (proximo_cumple - hoy).days
    dias_desde_ultimo = (hoy - ultimo_cumple).days
    
    if dias_al_proximo <= dias_desde_ultimo:
        edad_actuarial = edad + 1
    else:
        edad_actuarial = edad
        
    return edad, edad_actuarial


def render_cartolas_ui():
    st.markdown("""
    <div style='background: radial-gradient(circle at top right, #3a3a3a 0%, #050505 80%); padding: 30px; border-radius: 15px; border: 1px solid #D4AF37; margin-bottom: 30px;'>
        <h1 style='margin:0; font-size: 2.2rem; color: #D4AF37;'>🏦 Altus AI <span style='color: white;'>- Motor Cuantitativo</span></h1>
        <p style='margin:10px 0 0 0; opacity: 0.9; font-size: 1.1rem; color: #ffffff;'>Plataforma de inteligencia artificial operada por FV Asesorías e Inversiones.</p>
    </div>
    """, unsafe_allow_html=True)

    db: Session = SessionLocal()
    
    try:
        prospects = db.query(Prospect).all()
        
        # UI para Añadir Nuevo Prospecto
        with st.expander("➕ Ingresar Nuevo Cliente por RUT / Buscar Existente", expanded=not bool(prospects)):
            with st.form("nuevo_prospecto_form"):
                nuevo_rut = st.text_input("Ingresa el RUT del Cliente (ej: 12345678-9)")
                if st.form_submit_button("Buscar Datos"):
                    from src.ingestion.cleaner import clean_rut_chileno
                    from src.enrichment.run_enrichment import get_active_provider, enrich_prospect_apollo, enrich_prospect_transunion
                    
                    rut_limpio = clean_rut_chileno(nuevo_rut)
                    if not rut_limpio:
                        st.error("RUT inválido. Por favor verifica el formato.")
                    else:
                        # Verificar si existe
                        existente = db.query(Prospect).filter(Prospect.rut == rut_limpio).first()
                        if existente:
                            st.session_state.selected_rut = rut_limpio
                            st.rerun()
                        else:
                            nombre_encontrado = "Cliente Desconocido"
                            with st.spinner("Buscando antecedentes e Inteligencia (OSINT)..."):
                                provider = get_active_provider()
                                if provider == "apollo":
                                    res = enrich_prospect_apollo(rut_limpio)
                                    if res.get("success"): nombre_encontrado = res.get("nombre", nombre_encontrado)
                                elif provider == "transunion":
                                    res = enrich_prospect_transunion(rut_limpio)
                                    if res.get("success"): nombre_encontrado = res.get("nombre", nombre_encontrado)
                                    
                            nuevo_p = Prospect(rut=rut_limpio, nombre=nombre_encontrado, status_contacto="Nuevo")
                            db.add(nuevo_p)
                            db.commit()
                            st.session_state.selected_rut = rut_limpio
                            st.rerun()

        # Recargar prospects por si hubo inserción
        prospects = db.query(Prospect).all()
        if not prospects:
            st.warning("No hay prospectos. Usa la herramienta de arriba para ingresar uno.")
            return

        prospect_options = {f"{p.rut} - {p.nombre}": p.id for p in prospects}
        
        # Determinar índice por defecto basado en búsqueda
        default_index = 0
        if "selected_rut" in st.session_state:
            keys_list = list(prospect_options.keys())
            for i, k in enumerate(keys_list):
                if k.startswith(st.session_state.selected_rut):
                    default_index = i
                    break

        selected_prospect_name = st.selectbox("👤 Seleccionar Cliente/Prospecto Existente", list(prospect_options.keys()), index=default_index)
        prospect_id = prospect_options[selected_prospect_name]
        prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()

        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["📊 Análisis y Estrategia", "⚔️ Benchmarking Competencia", "🧠 Analista de Consultas"])
        with tab1:
            col1, col2 = st.columns([1, 2])
        
            with col1:
                st.subheader("📈 1. Ingesta de Inversiones (Portafolio)")
                
                inv_files = st.file_uploader("Sube Cartola de Inversiones (Bolsa, FFMM, APV)", type=["pdf", "png", "jpg", "xlsx", "xls"], accept_multiple_files=True)
                
                if inv_files and len(inv_files) > 0:
                    excel_files = [f for f in inv_files if f.name.endswith('.xlsx') or f.name.endswith('.xls')]
                    pdf_files = [f for f in inv_files if not (f.name.endswith('.xlsx') or f.name.endswith('.xls'))]
                    
                    if excel_files:
                        st.info("📊 Archivo Excel detectado. Vamos a procesarlo dinámicamente.")
                        for excel_file in excel_files:
                            try:
                                import pandas as pd
                                df_temp = pd.read_excel(excel_file)
                                # Buscar RUTs en la columna RUT (si existe) o asumir general si no existe
                                ruts_encontrados = []
                                if 'RUT' in df_temp.columns:
                                    ruts_encontrados = df_temp['RUT'].dropna().unique().tolist()
                                    
                                if not ruts_encontrados:
                                    st.warning(f"No se detectó una columna 'RUT' en {excel_file.name}. Se asumirá un único RUT para todo el archivo.")
                                    ruts_encontrados = [prospect.rut]
                                
                                st.write("**Clasificación de Entidades:**")
                                st.write("Para generar el reporte correctamente, clasifica cada RUT detectado en el archivo:")
                                
                                with st.form(f"form_clasif_{excel_file.name}"):
                                    rut_mapping = {}
                                    for r in ruts_encontrados:
                                        # Intentar pre-clasificar por largo del RUT o guión (heurística muy básica, mejor preguntar)
                                        tipo_defecto = "Empresa" if str(r).startswith("7") and len(str(r)) > 8 else "Persona Natural"
                                        rut_mapping[r] = st.selectbox(f"RUT {r}", ["Persona Natural", "Empresa"], index=0 if tipo_defecto == "Persona Natural" else 1)
                                        
                                    if st.form_submit_button("Procesar Excel y Guardar Portafolio"):
                                        from sura_excel_parser import parse_sura_excel
                                        import tempfile
                                        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                                            tmp.write(excel_file.getvalue())
                                            tmp_path = tmp.name
                                            
                                        # Llamamos al parser dinámico
                                        carteras_parseadas = parse_sura_excel(tmp_path, rut_mapping=rut_mapping)
                                        
                                        if carteras_parseadas:
                                            st.session_state.carteras = carteras_parseadas
                                            st.success("✅ Portafolio procesado y agrupado correctamente. ¡Ve a 'Valuación de Portafolios' para continuar!")
                                        else:
                                            st.error("Error al procesar el Excel. Verifica que tenga las columnas correctas (PRODUCTO, TOTAL ACTUALIZADO, etc).")
                                            
                                if 'carteras' in st.session_state:
                                    def nav_to_valuation():
                                        st.session_state.sub_nav_auditoria = "Valuación de Portafolios"
                                        
                                    st.button("➡️ Ir a Valuación de Portafolios", on_click=nav_to_valuation, type="primary", use_container_width=True)
                                    
                            except Exception as e:
                                st.error(f"No se pudo leer el Excel: {e}")
                                
                    if pdf_files and st.button("Extraer Portafolio de PDFs a BD", type="primary", use_container_width=True):
                        with st.status("⏳ Extrayendo activos de inversión...", expanded=True) as status:
                            try:
                                from src.database.models import ClientPortfolio
                                import google.generativeai as genai
                                import json
                                import tempfile
                                
                                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                                model = genai.GenerativeModel('gemini-2.5-pro')
                                
                                for idx, inv_file in enumerate(inv_files):
                                    st.write(f"Procesando portafolio {inv_file.name}...")
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf" if inv_file.name.lower().endswith(".pdf") else ".png") as tmp:
                                        tmp.write(inv_file.getvalue())
                                        tmp_path = tmp.name
                                        
                                    file_uri = genai.upload_file(tmp_path)
                                    
                                    prompt = """Eres un experto financiero. Lee este estado de cuenta de inversiones y extrae todos los activos financieros del cliente en formato JSON.
                                    Debes retornar SOLO un arreglo de objetos JSON con esta estructura exacta, sin markdown ni comillas extras:
                                    [
                                      {"institucion": "Nombre de la corredora/banco", "activo": "Nombre del fondo o acción", "tipo_activo": "Renta Variable/Renta Fija/APV/Liquidez", "monto_clp": 1500000}
                                    ]
                                    Asegúrate de convertir los montos a pesos chilenos (CLP) como enteros, sin puntos ni símbolos. Si está en dólares o UF, haz una conversión aproximada.
                                    """
                                    response = model.generate_content([file_uri, prompt])
                                    raw_json = response.text.strip()
                                    if raw_json.startswith("```json"):
                                        raw_json = raw_json[7:-3]
                                    elif raw_json.startswith("```"):
                                        raw_json = raw_json[3:-3]
                                        
                                    activos = json.loads(raw_json)
                                    
                                    for a in activos:
                                        inst_new = a.get('institucion', 'Desconocido')
                                        act_new = a.get('activo', 'Activo N/A')
                                        tipo_new = a.get('tipo_activo', 'Otro')
                                        monto_new = float(a.get('monto_clp', 0.0))
                                        
                                        # Buscar activo existente por coincidencia parcial de nombre o mismo tipo/institución
                                        existentes = db.query(ClientPortfolio).filter(
                                            ClientPortfolio.prospect_id == prospect.id,
                                            ClientPortfolio.institucion == inst_new
                                        ).all()
                                        
                                        for ex in existentes:
                                            # Si el activo tiene el mismo nombre base o el mismo tipo y monto similar, eliminar duplicado viejo
                                            clean_ex = ex.activo.replace(" - ", " ").replace("-", " ").strip().lower()
                                            clean_new = act_new.replace(" - ", " ").replace("-", " ").strip().lower()
                                            if clean_ex in clean_new or clean_new in clean_ex or (ex.tipo_activo == tipo_new and abs((ex.monto_original or ex.monto_clp or 0) - monto_new) < 1000):
                                                db.delete(ex)
                                        
                                        nuevo_activo = ClientPortfolio(
                                            prospect_id=prospect.id,
                                            institucion=inst_new,
                                            activo=act_new,
                                            tipo_activo=tipo_new,
                                            monto_original=monto_new if a.get('moneda_original', 'CLP') == 'CLP' else float(a.get('monto_original', 0.0)),
                                            moneda_original=a.get('moneda_original', 'CLP'),
                                            monto_clp=monto_new
                                        )
                                        db.add(nuevo_activo)
                                        
                                    os.remove(tmp_path)
                                
                                db.commit()
                                status.update(label="✅ Portafolio extraído y guardado con éxito", state="complete")
                                st.rerun()
                            except Exception as e:
                                status.update(label=f"Error procesando inversiones: {str(e)}", state="error")
                            
                st.markdown("---")
                st.subheader("📄 2. Ingesta de Flujos Bancarios")
                uploaded_files = st.file_uploader("Sube uno o más PDFs de Cartolas Bancarias", type=["pdf"], accept_multiple_files=True)
                extract_detail = st.checkbox("Extracción Profunda (Transacciones Individuales)", value=False)
            
                if uploaded_files and len(uploaded_files) > 0 and st.button("Procesar Cartola(s) con IA", help="Ejecuta la extracción de datos usando Google Gemini Multimodal sobre los PDFs subidos.", use_container_width=True):
                    with st.status("⏳ Analizando documentos con IA...", expanded=True) as status:
                        try:
                            reader = CartolaReader()
                            for idx, uploaded_file in enumerate(uploaded_files):
                                st.write(f"Procesando {uploaded_file.name} ({idx+1}/{len(uploaded_files)})...")
                                # Guardar temporalmente
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                    tmp.write(uploaded_file.getvalue())
                                    tmp_path = tmp.name
                                
                                summary_schema = reader.analyze_pdf(tmp_path, extract_detail)
                            
                                # Verificar si ya existe para evitar duplicados
                                existente = db.query(CartolaSummary).filter(
                                    CartolaSummary.prospect_id == prospect.id,
                                    CartolaSummary.mes == summary_schema.mes,
                                    CartolaSummary.institucion_bancaria == summary_schema.institucion_bancaria
                                ).first()

                                if existente:
                                    db.delete(existente)
                                    db.commit()

                                # Guardar en BD
                                cartola_db = CartolaSummary(
                                    prospect_id=prospect.id,
                                    mes=summary_schema.mes,
                                    institucion_bancaria=summary_schema.institucion_bancaria,
                                    saldo_inicial=summary_schema.saldo_inicial,
                                    saldo_final=summary_schema.saldo_final,
                                    total_ingresos=summary_schema.total_ingresos,
                                    total_egresos=summary_schema.total_egresos,
                                    gasto_supermercado=summary_schema.gasto_supermercado,
                                    gasto_seguros=summary_schema.gasto_seguros,
                                    gasto_creditos=summary_schema.gasto_creditos,
                                    gasto_ocio=summary_schema.gasto_ocio,
                                    capacidad_ahorro_estimada=summary_schema.capacidad_ahorro_estimada,
                                    analisis_ia=summary_schema.analisis_cualitativo
                                )
                                db.add(cartola_db)
                                os.remove(tmp_path)
                            
                            db.commit()
                            status.update(label="✅ Cartolas procesadas con éxito", state="complete")
                            st.rerun()
                        except Exception as e:
                            status.update(label=f"Error procesando cartolas: {str(e)}", state="error")

                            status.update(label=f"Error procesando cartolas: {str(e)}", state="error")
                            
                # Botón del SFO
                st.markdown("---")
                st.subheader("🚨 Motor SFO (Synthetic Family Office)")
                shock_event = st.text_input("Ingresa un Shock de Mercado (Ej: 'SQM cayó un 15%')", placeholder="El Banco Central bajó las tasas 100 bps...")
                if st.button("Ejecutar Test de Estrés (SFO)", use_container_width=True):
                    if not shock_event:
                        st.warning("Debes ingresar un evento de shock.")
                    else:
                        with st.spinner("SFO calculando impacto patrimonial..."):
                            from src.database.models import ClientPortfolio
                            from src.agents.sfo_engine import SFOEngine
                            
                            portfolios = db.query(ClientPortfolio).filter(ClientPortfolio.prospect_id == prospect.id).all()
                            if not portfolios:
                                st.error("No hay un portafolio de inversiones guardado para este cliente.")
                            else:
                                port_data = "\n".join([f"- {p.activo} ({p.institucion}): ${p.monto_clp:,.0f} CLP [{p.tipo_activo}]" for p in portfolios])
                                
                                # Preparar info del prospect
                                profile = db.query(ClientProfile).filter(ClientProfile.prospect_id == prospect.id).first()
                                prospect_info = f"Nombre: {prospect.nombre}\n"
                                if profile:
                                    prospect_info += f"Edad: {profile.edad}\nPerfil de Riesgo: {profile.nivel_riesgo}\nSegmento: {profile.segmento_cliente}\nPatrimonio Inmobiliario: ${profile.patrimonio_inmobiliario:,.0f}"
                                    
                                engine = SFOEngine()
                                alert_msg = engine.run_stress_test(prospect_info, port_data, shock_event)
                                st.session_state[f"sfo_alert_{prospect.id}"] = alert_msg
                                
                if f"sfo_alert_{prospect.id}" in st.session_state:
                    st.error("ALERTA SFO GENERADA")
                    st.markdown(st.session_state[f"sfo_alert_{prospect.id}"])

            with col2:
                st.subheader("🧠 2. Asesor Patrimonial Autónomo")
                profile = db.query(ClientProfile).filter(ClientProfile.prospect_id == prospect.id).first()
                cartolas = db.query(CartolaSummary).filter(CartolaSummary.prospect_id == prospect.id).all()
            
                # Formulario de Perfil (Si no existe)
                if not profile:
                    st.info("Falta el perfil patrimonial del cliente. Completa estos datos para que el Agente pueda hacer su trabajo.")
                    with st.form("profile_form"):
                        fecha_nac = st.date_input("Fecha de Nacimiento", value=date(1980, 1, 1), min_value=date(1900, 1, 1))
                        est_civil = st.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado", "Viudo"])
                        herederos = st.number_input("Cantidad Herederos", min_value=0, max_value=20, value=0)
                    
                        st.markdown("**Perfilamiento Estratégico**")
                        seg_cliente = st.selectbox("Segmento", ["Mass Affluent", "Banca Privada", "Alto Patrimonio", "Ultra Alto Patrimonio"])
                        niv_riesgo = st.selectbox("Perfil de Riesgo", ["Conservador", "Moderado", "Agresivo"])
                        exp_inv = st.selectbox("Experiencia Inversiones", ["Baja", "Media", "Alta", "Experto"])
                    
                        pat_liq = st.number_input("Patrimonio Líquido (MM$)", value=50) * 1000000
                        pat_inm = st.number_input("Patrimonio Inmobiliario (MM$)", value=100) * 1000000
                        
                        st.markdown("**Flujos de Caja (Opcional)**")
                        ing_mens = st.number_input("Ingresos Mensuales Estimados ($)", value=0, step=500000)
                        egr_mens = st.number_input("Egresos Mensuales Estimados ($)", value=0, step=500000)
                    
                        if st.form_submit_button("Guardar Perfil y Calcular Edad"):
                            edad_cron, edad_act = calcular_edades(fecha_nac)
                            new_profile = ClientProfile(
                                prospect_id=prospect.id,
                                fecha_nacimiento=fecha_nac,
                                edad=edad_cron,
                                edad_actuarial=edad_act,
                                estado_civil=est_civil,
                                cantidad_herederos=herederos,
                                segmento_cliente=seg_cliente,
                                nivel_riesgo=niv_riesgo,
                                experiencia_inversiones=exp_inv,
                                patrimonio_liquido=pat_liq,
                                patrimonio_inmobiliario=pat_inm,
                                ingresos_mensuales=ing_mens,
                                egresos_mensuales=egr_mens
                            )
                            db.add(new_profile)
                            db.commit()
                            st.success("Perfil Guardado Exitosamente")
                            st.rerun()
                else:
                    st.write(f"**Fecha de Nac:** {profile.fecha_nacimiento} | **Edad Cronológica:** {profile.edad} años | **Edad Actuarial:** {profile.edad_actuarial} años")
                    st.write(f"**Estado Civil:** {profile.estado_civil} | **Herederos:** {profile.cantidad_herederos}")
                    st.write(f"**Segmento:** {profile.segmento_cliente} | **Riesgo:** {profile.nivel_riesgo} | **Exp:** {profile.experiencia_inversiones}")
                    st.write(f"**Patrimonio Total:** ${(profile.patrimonio_liquido + profile.patrimonio_inmobiliario):,.0f} | **Flujo Mensual Neto:** ${(profile.ingresos_mensuales or 0) - (profile.egresos_mensuales or 0):,.0f}")
                    
                    with st.expander("✏️ Editar Perfil Patrimonial"):
                        with st.form("edit_profile_form"):
                            col1_e, col2_e = st.columns(2)
                            with col1_e:
                                e_fecha_nac = st.date_input("Fecha de Nacimiento", value=profile.fecha_nacimiento)
                                e_est_civil = st.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado", "Viudo"], index=["Soltero", "Casado", "Divorciado", "Viudo"].index(profile.estado_civil) if profile.estado_civil in ["Soltero", "Casado", "Divorciado", "Viudo"] else 1)
                                e_herederos = st.number_input("Cantidad Herederos", min_value=0, max_value=20, value=profile.cantidad_herederos)
                                e_pat_liq = st.number_input("Patrimonio Líquido (MM$)", value=int(profile.patrimonio_liquido/1000000)) * 1000000
                                e_pat_inm = st.number_input("Patrimonio Inmobiliario (MM$)", value=int(profile.patrimonio_inmobiliario/1000000)) * 1000000
                            with col2_e:
                                e_seg_cliente = st.selectbox("Segmento", ["Mass Affluent", "Banca Privada", "Alto Patrimonio", "Ultra Alto Patrimonio"], index=["Mass Affluent", "Banca Privada", "Alto Patrimonio", "Ultra Alto Patrimonio"].index(profile.segmento_cliente) if profile.segmento_cliente in ["Mass Affluent", "Banca Privada", "Alto Patrimonio", "Ultra Alto Patrimonio"] else 1)
                                e_niv_riesgo = st.selectbox("Perfil de Riesgo", ["Conservador", "Moderado", "Agresivo"], index=["Conservador", "Moderado", "Agresivo"].index(profile.nivel_riesgo) if profile.nivel_riesgo in ["Conservador", "Moderado", "Agresivo"] else 1)
                                e_exp_inv = st.selectbox("Experiencia Inversiones", ["Baja", "Media", "Alta", "Experto"], index=["Baja", "Media", "Alta", "Experto"].index(profile.experiencia_inversiones) if profile.experiencia_inversiones in ["Baja", "Media", "Alta", "Experto"] else 1)
                                e_ing_mens = st.number_input("Ingresos Mensuales Estimados ($)", value=int(profile.ingresos_mensuales or 0), step=500000)
                                e_egr_mens = st.number_input("Egresos Mensuales Estimados ($)", value=int(profile.egresos_mensuales or 0), step=500000)
                            
                            if st.form_submit_button("Actualizar Perfil"):
                                edad_cron_e, edad_act_e = calcular_edades(e_fecha_nac)
                                profile.fecha_nacimiento = e_fecha_nac
                                profile.edad = edad_cron_e
                                profile.edad_actuarial = edad_act_e
                                profile.estado_civil = e_est_civil
                                profile.cantidad_herederos = e_herederos
                                profile.segmento_cliente = e_seg_cliente
                                profile.nivel_riesgo = e_niv_riesgo
                                profile.experiencia_inversiones = e_exp_inv
                                profile.patrimonio_liquido = e_pat_liq
                                profile.patrimonio_inmobiliario = e_pat_inm
                                profile.ingresos_mensuales = e_ing_mens
                                profile.egresos_mensuales = e_egr_mens
                                db.commit()
                                st.success("Perfil actualizado correctamente.")
                                st.rerun()
                                
                    from src.database.models import ClientPortfolio
                    portafolios = db.query(ClientPortfolio).filter(ClientPortfolio.prospect_id == prospect.id).all()
                    
                    st.markdown("### 💼 Portafolio de Inversiones Consolidado (AUM)")
                    if portafolios:
                        total_aum = sum([p.monto_clp for p in portafolios])
                        st.metric("Total Assets Under Management (AUM)", f"${total_aum:,.0f} CLP")
                        
                        import pandas as pd
                        df_port = pd.DataFrame([{
                            "Institución": p.institucion,
                            "Activo": p.activo,
                            "Tipo": p.tipo_activo,
                            "Monto (CLP)": p.monto_clp
                        } for p in portafolios])
                        st.dataframe(df_port, use_container_width=True, hide_index=True)
                    else:
                        st.info("No hay inversiones registradas. Sube una Cartola de Inversiones en el panel izquierdo.")
                
                    st.markdown("### 📊 Flujos y Cartolas Bancarias Registradas")
                    if cartolas:
                        for c in cartolas:
                            st.caption(f"📅 {c.mes} | {c.institucion_bancaria}")
                            if c.analisis_ia:
                                cleaned_ia = str(c.analisis_ia).replace("\\n", "\n").replace("$", r"\$")
                                st.info(f"🧠 **Lectura IA:**\n\n{cleaned_ia}")
                    else:
                        st.caption("No hay cartolas registradas. Sube una en el panel izquierdo.")

                    st.markdown("### 🎤 Notas de Audio (Inteligencia Multimodal)")
                    st.info("Graba o sube un audio de tu reunión. La IA extraerá el perfil psicológico y oportunidades ocultas.")
                    
                    audio_metodo = st.radio("Método de Ingreso de Audio", ["Grabar ahora", "Subir archivo"], horizontal=True)
                    audio_val = None
                    if audio_metodo == "Grabar ahora":
                        audio_val = st.audio_input("Grabar Nota")
                    else:
                        audio_val = st.file_uploader("Sube tu archivo de audio desde el celular", type=["mp3", "wav", "m4a", "ogg", "mp4"])
                        
                    if audio_val:
                        if st.button("Procesar Audio con Gemini", use_container_width=True):
                            with st.spinner("Analizando voz y extrayendo insights..."):
                                from src.intelligence.audio_processor import process_client_audio
                                try:
                                    insights = process_client_audio(audio_val.getvalue())
                                
                                    # Guardar en BD
                                    if profile.observaciones_estrategicas:
                                        profile.observaciones_estrategicas += "\n\n---\n\n" + insights
                                    else:
                                        profile.observaciones_estrategicas = insights
                                    db.commit()
                                    backup_interaction(prospect.rut, prospect.nombre, "Insights_Audio", insights)
                                    st.success("Nota procesada y guardada. Respaldo generado en la carpeta del cliente.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error procesando audio: {str(e)}")
                
                    if profile.observaciones_estrategicas:
                        st.markdown("### 🕒 Historial de Interacciones (Timeline)")
                        interacciones = profile.observaciones_estrategicas.split("\n\n---\n\n")
                        for idx, interaccion in enumerate(reversed(interacciones)):
                            with st.expander(f"Interacción #{len(interacciones) - idx}"):
                                st.markdown(interaccion)

                    st.markdown("### 🎥 Analista de Reuniones en Video (Teams/Zoom)")
                    st.info("Sube la grabación de tu reunión (MP4). La IA multimodal extraerá el acta, los próximos pasos y evaluará el perfil psicológico y objeciones basándose en el video y audio.")
                    video_val = st.file_uploader("Subir grabación de video", type=["mp4", "mov", "avi"])
                    
                    if video_val:
                        if st.button("🧠 Generar Minuta de Reunión (Video IA)", use_container_width=True):
                            with st.spinner("Subiendo video al procesador de Google (puede tomar varios minutos)..."):
                                from src.intelligence.meeting_analyzer import MeetingAnalyst
                                import tempfile
                                
                                # Guardar temporalmente para subir a Google API
                                temp_path = os.path.join(tempfile.gettempdir(), video_val.name)
                                with open(temp_path, "wb") as f:
                                    f.write(video_val.getvalue())
                                
                                try:
                                    analyst = MeetingAnalyst()
                                    minuta = analyst.analyze_meeting(temp_path, prospect.nombre)
                                    
                                    # Guardar en BD
                                    if profile.observaciones_estrategicas:
                                        profile.observaciones_estrategicas += f"\n\n---\n\n{minuta}"
                                    else:
                                        profile.observaciones_estrategicas = minuta
                                    db.commit()
                                    
                                    # Respaldo físico
                                    backup_interaction(prospect.rut, prospect.nombre, "Minuta_Video", minuta)
                                    st.success("Minuta generada y guardada en el Historial del Cliente.")
                                    st.markdown("### Acta de Reunión")
                                    st.markdown(minuta)
                                    
                                    # Generar botón de Email si existe la sección
                                    import urllib.parse
                                    if "📧 Borrador de Correo para el Cliente" in minuta:
                                        partes = minuta.split("📧 Borrador de Correo para el Cliente")
                                        if len(partes) > 1:
                                            borrador = partes[1].strip()
                                            
                                            # Intentar extraer asunto
                                            asunto = "Resumen de nuestra reunión - FV Inversiones"
                                            if "Asunto:" in borrador:
                                                lineas = borrador.split("\n")
                                                for l in lineas:
                                                    if "Asunto:" in l:
                                                        asunto = l.replace("Asunto:", "").replace("*", "").strip()
                                                        borrador = borrador.replace(l, "").strip()
                                                        break
                                                        
                                            mailto_url = f"mailto:?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(borrador)}"
                                            
                                            st.markdown("---")
                                            st.markdown(f'''
                                                <a href="{mailto_url}" target="_blank">
                                                    <button style="background-color:#0078D4; color:white; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
                                                        📧 Abrir Borrador en tu Gestor de Correo (Outlook/Gmail)
                                                    </button>
                                                </a>
                                            ''', unsafe_allow_html=True)
                                            st.info("Revisa y ajusta el correo en tu aplicación antes de enviarlo.")
                                            
                                    os.remove(temp_path)
                                except Exception as e:
                                    st.error(f"Error procesando el video: {str(e)}")
                                    if os.path.exists(temp_path):
                                        os.remove(temp_path)

                    if st.button("🤖 Generar Estrategia Proactiva (IA)", help="Analiza el perfil completo del cliente y sus cartolas para sugerir optimizaciones patrimoniales y tributarias.", type="primary"):
                        with st.spinner("El Agente está cruzando el perfil, cartolas y leyes (RAG)..."):
                            try:
                                advisor = ProactiveAdvisor()
                                estrategia = advisor.generate_strategy(prospect, profile, cartolas)
                                st.session_state[f"estrategia_{prospect.id}"] = estrategia
                                backup_interaction(prospect.rut, prospect.nombre, "Estrategia_Proactiva", estrategia)
                            except Exception as e:
                                st.error(f"Error al generar estrategia: {str(e)}")
                
                    # Mostrar la estrategia si existe en la sesión para que no se borre al recargar la página
                    if f"estrategia_{prospect.id}" in st.session_state:
                        st.markdown("### 📜 Estrategia Patrimonial Propuesta")
                        est_text = str(st.session_state[f"estrategia_{prospect.id}"])
                        est_cleaned = est_text.replace("\\n", "\n").replace("$", r"\$")
                        st.markdown(est_cleaned)

                    st.markdown("---")
                    st.markdown("### 🚀 Ejecución Autónoma (Agente de Salida)")
                    col_exec1, col_exec2 = st.columns(2)
                    
                    with col_exec1:
                        if st.button("📄 Exportar a PDF", use_container_width=True):
                            from src.intelligence.execution_agent import ExecutionAgent
                            with st.spinner("Generando documento institucional..."):
                                exec_agent = ExecutionAgent()
                                tmp_pdf_path = os.path.join(tempfile.gettempdir(), f"Estrategia_{prospect.id}.pdf")
                                try:
                                    exec_agent.generate_pdf_report(st.session_state[f"estrategia_{prospect.id}"], tmp_pdf_path)
                                    with open(tmp_pdf_path, "rb") as f_pdf:
                                        st.download_button("⬇️ Descargar PDF Oficial", f_pdf, file_name=f"FV_Estrategia_{prospect.rut}.pdf", mime="application/pdf", use_container_width=True, type="primary")
                                except Exception as e:
                                    st.error(f"Error al generar PDF: {str(e)}")

                    with col_exec2:
                        if st.button("✉️ Redactar Email al Cliente", use_container_width=True):
                            from src.intelligence.execution_agent import ExecutionAgent
                            with st.spinner("Redactando correo..."):
                                exec_agent = ExecutionAgent()
                                try:
                                    email_data = exec_agent.generate_email_draft(prospect.nombre, st.session_state[f"estrategia_{prospect.id}"])
                                    st.session_state[f"email_{prospect.id}"] = email_data
                                except Exception as e:
                                    st.error(f"Error al redactar correo: {str(e)}")
                                
                    if f"email_{prospect.id}" in st.session_state:
                        st.success("Borrador generado con éxito.")
                        email_data = st.session_state[f"email_{prospect.id}"]
                        st.markdown(f"**Asunto:** {email_data['subject']}")
                        st.text_area("Cuerpo del Correo", email_data['body'], height=150)
                        st.markdown(f"""<a href="{email_data['mailto_link']}" target="_blank">
                                    <button style='background-color:#1e3a8a;color:white;padding:10px;border:none;border-radius:5px;cursor:pointer;width:100%;font-weight:bold;'>
                                    🚀 Abrir directamente en Outlook / Mail</button></a>""", unsafe_allow_html=True)
                        

        with tab2:
            st.subheader("⚔️ Benchmarking vs Competencia")
            st.info("Sube un folleto, PDF o imagen de un producto de la competencia (ej. Fondo Mutuo, APV) para generar un contra-argumento instantáneo.")
            
            comp_file = st.file_uploader("Subir Propuesta de Competencia (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"], key="comp_uploader")
            
            if comp_file and st.button("Analizar Competencia y Generar Objeciones", type="primary"):
                with st.spinner("Leyendo letras chicas y comparando con FV Asesorías..."):
                    try:
                        file_bytes = comp_file.getvalue()
                        mime_type = comp_file.type
                        agent = CompetitorAgent()
                        resultado_bench = agent.generate_counter_proposal(file_bytes, mime_type, prospect.nombre)
                        st.session_state[f"bench_{prospect.id}"] = resultado_bench
                    except Exception as e:
                        st.error(f"Error al analizar competencia: {str(e)}")
            
            if f"bench_{prospect.id}" in st.session_state:
                st.markdown(st.session_state[f"bench_{prospect.id}"])

        with tab3:
            st.subheader("🧠 Analista Multimodal de Consultas y Portafolios")
            st.info("Ingresa cualquier consulta del cliente (texto, imagen de WhatsApp, correo en PDF, nota de voz). El agente investigará en la web citando fuentes y dará una recomendación técnica.")
            
            q_text = st.text_area("Consulta en texto (opcional)", height=100, placeholder="Escribe o pega aquí la duda del cliente...")
            
            q_method = st.radio("¿Quieres adjuntar algún archivo?", ["Subir Archivo", "Grabar Audio", "Sin Adjunto"], horizontal=True, index=0)
            
            q_file = None
            if q_method == "Subir Archivo":
                q_file = st.file_uploader("Adjuntar documento o imagen", type=["pdf", "png", "jpg", "jpeg", "txt", "eml", "csv", "xlsx", "xls", "mp3", "wav"], accept_multiple_files=True)
                dolar_historico = st.text_input("Tipo de Cambio Histórico (Opcional)", value="", placeholder="Ej: 800", help="Si lo dejas en blanco, la IA buscará un valor referencial.")
                if dolar_historico.strip():
                    q_text = f"{q_text}\n\n[CONTEXTO INTERNO]: El dólar de compra histórico fue de ${dolar_historico} CLP. Usa este valor para los cálculos de rentabilidad en pesos y rentabilidad real."
                
                try:
                    import requests
                    resp = requests.get("https://mindicador.cl/api/dolar", timeout=3).json()
                    dolar_hoy = resp["serie"][0]["valor"]
                    q_text = f"{q_text}\n\n[DATO ESTRICTO]: El Dólar Observado de HOY (Banco Central) es exactamente {dolar_hoy} CLP. UTILIZA EXCLUSIVAMENTE este valor como Dólar Actual para todos tus cálculos de conversión y tributarios, sin importar lo que diga Yahoo Finance o DuckDuckGo."
                except Exception as e:
                    pass
            elif q_method == "Grabar Audio":
                q_file = [st.audio_input("Grabar consulta de voz")]
            
            if st.button("Analizar Consulta e Investigar Mercado", type="primary", use_container_width=True):
                if not q_text and (not q_file or q_file[0] is None):
                    st.warning("Debes ingresar texto o subir un archivo.")
                else:
                    from src.intelligence.query_analyst import MultimodalQueryAnalyst
                    analyst = MultimodalQueryAnalyst()
                    
                    respuesta = ""
                    with st.status("🧠 Analizando la consulta e investigando en la web...", expanded=True) as status:
                        st.write("📥 Procesando documentos adjuntos...")
                        
                        file_bytes_list = []
                        filenames = []
                        if q_file:
                            st.write("📄 Extrayendo contexto multimodal...")
                            for f in q_file:
                                if f:
                                    file_bytes_list.append(f.read())
                                    filenames.append(getattr(f, 'name', 'adjunto'))
                                
                        st.write("🌐 Conectando con Agente Investigador (OSINT)...")
                        st.write("⏳ Realizando cálculos y buscando precios objetivo (esto toma 1-2 minutos)...")
                        
                        try:
                            prospect_context = f"Nombre: {prospect.nombre}."
                            if profile:
                                prospect_context += f" Perfil de Riesgo: {profile.nivel_riesgo}. Segmento: {profile.segmento_cliente}. Patrimonio Total: ${(profile.patrimonio_liquido + profile.patrimonio_inmobiliario):,.0f} CLP."
                                
                            respuesta = analyst.analyze_query(
                                text_input=q_text,
                                file_bytes_list=file_bytes_list if file_bytes_list else None,
                                filenames=filenames if filenames else None,
                                prospect_info=prospect_context
                            )
                            status.update(label="✅ Análisis completado con éxito", state="complete", expanded=False)
                            st.session_state[f"query_{prospect.id}"] = respuesta
                            backup_interaction(prospect.rut, prospect.nombre, "Analista_Multimodal", respuesta)
                        except Exception as e:
                            status.update(label=f"❌ Error durante el análisis: {str(e)}", state="error", expanded=True)
                            st.error(f"Error procesando la consulta: {str(e)}")
            
            if f"query_{prospect.id}" in st.session_state:
                st.markdown("---")
                st.markdown("### 📝 Respuesta del Analista (Modificable)")
                st.info("💡 **Consejo:** Puedes modificar el texto aquí mismo antes de generar el reporte PDF para tu cliente.")
                st.caption("⚠️ **IMPORTANTE:** Si modificas el texto, debes **hacer clic fuera del cuadro de texto** (o presionar Cmd+Enter/Ctrl+Enter) para registrar los cambios antes de presionar el botón de descargar.")
                
                # Área de texto editable
                edited_query = st.text_area(
                    "Contenido del Reporte (Markdown)", 
                    value=st.session_state[f"query_{prospect.id}"], 
                    height=400,
                    key=f"edit_query_{prospect.id}"
                )
                
                # Guardamos los cambios temporalmente en la sesión
                if edited_query != st.session_state[f"query_{prospect.id}"]:
                    st.session_state[f"query_{prospect.id}"] = edited_query
                
                st.markdown("<br>", unsafe_allow_html=True)
                try:
                    import sys
                    import importlib
                    from pathlib import Path
                    sys.path.append(str(Path(__file__).parent.parent.parent))
                    import generador_informes
                    importlib.reload(generador_informes)
                    from generador_informes import generar_pdf_bytes
                    pdf_bytes = generar_pdf_bytes(f"Reporte Analítico: {prospect.nombre}", edited_query)
                    st.download_button(
                        label="📄 Descargar Reporte en PDF (Altus AI)",
                        data=pdf_bytes,
                        file_name=f"Reporte_AltusAI_{prospect.rut}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"No se pudo preparar el PDF: {e}")
    finally:
        db.close()
