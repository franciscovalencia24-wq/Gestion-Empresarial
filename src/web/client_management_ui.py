import streamlit as st
import pandas as pd
from src.database.connection import SessionLocal, engine
from sqlalchemy import text
import io
import datetime
import plotly.express as px
import plotly.graph_objects as go
from src.osint.parser_inversiones import parse_investment_files
import plotly.express as px
import plotly.graph_objects as go
from src.osint.parser_inversiones import parse_investment_files
import os
import json
from src.database.models import Prospect, ClientProfile, ClientHeir, ClientProperty, ClientInsurance, ClientDebt, ClientCompany, ClientPortfolio, CompanyShareholder, CompanyRepresentative
from src.osint.herencia import calculate_inheritance_chile

def render_client_management_ui():
    main_container = st.container()
    
    def render_manual_button(file_name, label):
        path = os.path.join("assets", "manuales", file_name)
        if os.path.exists(path):
            with open(path, "rb") as f:
                st.download_button(label=label, data=f, file_name=file_name, mime="application/pdf", use_container_width=True)
        else:
            st.download_button(label=label, data=b"", file_name=file_name, mime="application/pdf", disabled=True, help="Manual no disponible", use_container_width=True)

    with main_container:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 15px; margin-bottom: 25px; color: white;'>
                <h1 style='color: white; margin: 0; font-size: 2.5em; font-weight: 900;'>👥 Gestión de Clientes</h1>
                <p style='color: #94a3b8; margin: 10px 0 0 0; font-size: 1.2em;'>Punto de partida: Selecciona tu prospecto o cliente y enriquece su perfil detallado.</p>
            </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔍 Seleccionar Cliente", "📝 Enriquecimiento de Perfil Avanzado"])

    with tab1:
        st.subheader("Búsqueda en Base de Datos")
        with engine.connect() as con:
            df = pd.read_sql("SELECT rut, nombre, es_cliente FROM prospects", con=con)
        
        if df.empty:
            st.warning("No hay registros en la base de datos.")
            return

        c_search1, c_search2 = st.columns(2)
        with c_search1:
            rut_manual = st.text_input("🔍 Escribir RUT Exacto (opcional):", placeholder="Ej: 12345678-9")
        
        opciones = df.apply(lambda row: f"{row['rut']} - {row['nombre']} {'(Cliente)' if row['es_cliente'] else '(Prospecto)'}", axis=1).tolist()
        
        with c_search2:
            cliente_seleccionado_texto = st.selectbox("O buscar en lista desplegable:", ["Seleccione..."] + opciones)

        rut_seleccionado = None
        nombre_seleccionado = None

        if rut_manual:
            match = df[df['rut'].str.contains(rut_manual, na=False, case=False)]
            if not match.empty:
                rut_seleccionado = match.iloc[0]['rut']
                nombre_seleccionado = match.iloc[0]['nombre']
            else:
                st.warning("⚠️ RUT no encontrado en la base de datos.")
                with st.expander("➕ Registrar como Nuevo Prospecto", expanded=True):
                    nuevo_nombre = st.text_input("Nombre (Persona o Empresa):")
                    if st.button("Registrar y Seleccionar", type="primary"):
                        if nuevo_nombre.strip():
                            try:
                                with engine.begin() as con:
                                    con.execute(text("INSERT INTO prospects (rut, nombre, es_cliente) VALUES (:r, :n, 0)"), {"r": rut_manual, "n": nuevo_nombre})
                                st.success("Prospecto creado exitosamente.")
                                st.session_state.current_client_rut = rut_manual
                                st.session_state.current_client_name = nuevo_nombre
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al guardar en base de datos: {e}")
                        else:
                            st.error("Por favor, ingresa un nombre para registrar el prospecto.")
        elif cliente_seleccionado_texto != "Seleccione...":
            rut_seleccionado = cliente_seleccionado_texto.split(" - ")[0]
            nombre_seleccionado = cliente_seleccionado_texto.split(" - ")[1].split(" (")[0]

        if rut_seleccionado and nombre_seleccionado:
            st.session_state.current_client_rut = rut_seleccionado
            st.session_state.current_client_name = nombre_seleccionado
            st.success(f"✅ Cliente Seleccionado: {st.session_state.current_client_name} ({rut_seleccionado})")
            st.info("Este cliente se utilizará como base para los análisis posteriores en la plataforma.")
        else:
            if "current_client_rut" in st.session_state:
                st.info(f"Cliente activo actualmente: {st.session_state.current_client_name} ({st.session_state.current_client_rut})")



    with tab2:
        if "current_client_rut" not in st.session_state:
            st.warning("Primero selecciona un cliente en la pestaña de Búsqueda.")
        else:

            rut = st.session_state.current_client_rut
            st.subheader(f"Perfil: {st.session_state.current_client_name}")
        
            # Uso de variables planas en session_state para evitar problemas de referencia en st.data_editor
            k_hered = f"df_herederos_{rut}"
            k_prop = f"df_propiedades_{rut}"
            k_poliza = f"df_polizas_{rut}"
            k_debt = f"df_deudas_{rut}"
            k_comp = f"df_sociedades_{rut}"
            k_na = f"na_herederos_{rut}"
            k_test = f"test_{rut}"
            k_nota = f"nota_{rut}"
            k_alerta = f"alerta_{rut}"
            k_tipo_persona = f"tipo_persona_{rut}"
            k_socios = f"df_socios_{rut}"
            k_repres = f"df_repres_{rut}"
            k_inv = f"df_inversiones_{rut}"
            k_inv = f"df_inversiones_{rut}"
            k_fecha_const = f"fecha_const_{rut}"
            k_notaria = f"notaria_{rut}"
            k_repertorio = f"repertorio_{rut}"
            k_fecha_vig = f"fecha_vig_{rut}"
            k_doc_legal = f"doc_legal_{rut}"

            col_title, col_btn, col_btn_pdf = st.columns([0.5, 0.25, 0.25])
            col_title.markdown(f"## 👤 {rut} - Perfil Integral del Cliente")
            if col_btn.button("🔄 Refrescar Datos", help="Recarga la información desde la Base de Datos", use_container_width=True):
                for key in [k_hered, k_prop, k_poliza, k_na, k_test, k_nota, k_alerta, k_debt, k_comp, k_tipo_persona, k_socios, k_repres, k_fecha_const, k_notaria, k_repertorio, k_fecha_vig, k_doc_legal]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

            from src.utils.pdf_generator import generate_succession_report_pdf
            try:
                # Buscar id prospect para PDF
                db_top = SessionLocal()
                clean_rut_top = rut.replace(".", "").replace("-", "").strip()
                p_top = db_top.query(Prospect).filter(Prospect.rut.contains(clean_rut_top) | (Prospect.rut == rut)).first()
                pdf_top_bytes = generate_succession_report_pdf(p_top.id) if p_top else None
                db_top.close()
            except:
                pdf_top_bytes = None

            if pdf_top_bytes:
                col_btn_pdf.download_button(
                    label="📜 Descargar Reporte Total 360° (PDF)",
                    data=pdf_top_bytes,
                    file_name=f"Reporte_Consolidado_360_{rut}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    key=f"dl_top_pdf_{rut}"
                )

            if k_hered not in st.session_state:
                db = SessionLocal()
                clean_rut_search = rut.replace(".", "").replace("-", "").strip()
                prospect = db.query(Prospect).filter(Prospect.rut.contains(clean_rut_search) | (Prospect.rut == rut)).first()
            
                df_hered = pd.DataFrame(columns=["RUT", "Relación", "Nombre", "Fecha de Nacimiento", "% Asignación"])
                df_prop = pd.DataFrame(columns=["Nombre/Alias", "Comuna", "ROL", "Dirección", "Destino", "Fojas", "Número", "Año", "% de Derecho", "Avalúo Fiscal (CLP)", "Valor Com. (UF)", "Deuda Hipotecaria", "Institución Hipoteca", "Monto Inicial (UF)", "Saldo Actual (UF)", "Monto Asegurado (UF)", "Tasación (UF)", "Tasa Interés (%)", "Tipo Tasa", "Fecha Escritura", "Dividendo", "Cuota Actual", "Total Cuotas", "Arrendada", "Monto Arriendo", "Moneda Arriendo", "Fecha Contrato Arriendo", "Meses Reajuste Arriendo", "Contribuciones Trim.", "Gastos Comunes Mensuales", "Mantención Anual (CLP)", "Plusvalía Esperada (%)", "__fecha_act_cuota"])
                df_poliza = pd.DataFrame(columns=["Aseguradora", "Tipo", "Monto (UF)", "Prima", "Coberturas", "Análisis IA", "Beneficiarios"])
                df_debt = pd.DataFrame(columns=["Institucion", "Tipo_Credito", "Monto Original", "Monto Actual", "Carga Financiera", "Otorgamiento", "Vencimiento", "Mora", "Observaciones"])
                df_comp = pd.DataFrame(columns=["RUT Empresa", "Razón Social", "Incorporación", "% Capital", "% Utilidades"])
                df_socios = pd.DataFrame(columns=["RUT", "Nombre", "% Participación", "Capital Aportado"])
                df_repres = pd.DataFrame(columns=["RUT", "Nombre", "Poderes y Restricciones"])
                df_inv = pd.DataFrame(columns=["Institucion", "Activo", "Tipo", "Monto", "Moneda", "Monto CLP"])
                na_val = False
                nota_val = ""
                tipo_persona_val = "PN"
                fecha_const_val = None
                notaria_val = ""
                repertorio_val = ""
                fecha_vig_val = None
                doc_legal_val = ""
                nombre_val = ""
                telefono_val = ""
                email_val = ""
                perfil_val = "Moderado"
                objetivo_val = "Otro"

            
                if prospect:
                    heirs = db.query(ClientHeir).filter(ClientHeir.prospect_id == prospect.id).all()
                    if heirs:
                        df_hered = pd.DataFrame([{
                            "RUT": h.rut, "Relación": h.relacion, "Nombre": h.nombre,
                            "Fecha de Nacimiento": h.fecha_nacimiento, "% Asignación": h.porcentaje_asignacion,
                            "¿Estudiante (18-24 años)?": bool(h.es_estudiante)
                        } for h in heirs])
                    
                    props = db.query(ClientProperty).filter(ClientProperty.prospect_id == prospect.id).all()
                    if props:
                        import datetime as dt_module
                        now = dt_module.datetime.now()
                        current_month_str = now.strftime("%Y-%m")
                        updated_any = False
                    
                        for p in props:
                            if p.deuda_hipotecaria > 0 and p.hipoteca_cuota_actual < p.hipoteca_total_cuotas:
                                if now.day >= 15 and p.hipoteca_fecha_ultima_actualizacion != current_month_str:
                                    p.hipoteca_cuota_actual += 1
                                    p.hipoteca_fecha_ultima_actualizacion = current_month_str
                                    updated_any = True
                                
                        if updated_any:
                            db.commit()

                        df_prop = pd.DataFrame([{
                            "Nombre/Alias": p.observaciones, "Comuna": p.comuna, "ROL": p.rol, "Dirección": p.direccion,
                            "Destino": p.destino, "Fojas": p.fojas, "Número": p.numero, "Año": p.ano,
                            "% de Derecho": p.porcentaje_derecho, "Avalúo Fiscal (CLP)": p.avaluo_fiscal,
                            "Valor Com. (UF)": p.valor_comercial_estimado, "Deuda Hipotecaria": bool(p.deuda_hipotecaria > 0),
                            "Institución Hipoteca": p.hipoteca_institucion,
                            "Monto Inicial (UF)": p.hipoteca_monto_inicial,
                            "Saldo Actual (UF)": p.hipoteca_saldo_actual,
                            "Monto Asegurado (UF)": p.hipoteca_monto_asegurado,
                            "Tasación (UF)": p.hipoteca_valor_tasacion,
                            "Tasa Interés (%)": p.hipoteca_tasa_interes,
                            "Tipo Tasa": p.hipoteca_tipo_tasa,
                            "Fecha Escritura": p.hipoteca_fecha_escritura,
                            "Dividendo": p.dividendo_mensual, "Cuota Actual": p.hipoteca_cuota_actual, "Total Cuotas": p.hipoteca_total_cuotas, "Arrendada": p.arriendo_mensual > 0,
                            "Monto Arriendo": p.arriendo_mensual,
                            "Moneda Arriendo": p.arriendo_moneda or "CLP",
                            "Fecha Contrato Arriendo": p.arriendo_fecha_contrato,
                            "Meses Reajuste Arriendo": p.arriendo_periodo_reajuste,
                            "Contribuciones Trim.": p.contribuciones_anuales / 4 if p.contribuciones_anuales else 0.0,
                            "Gastos Comunes Mensuales": p.gastos_comunes,
                            "Mantención Anual (CLP)": p.gastos_mantencion_anual,
                            "Plusvalía Esperada (%)": p.plusvalia_esperada_anual,
                            "__fecha_act_cuota": p.hipoteca_fecha_ultima_actualizacion
                        } for p in props])
                    
                    df_poliza = pd.DataFrame([{
                        "Aseguradora": p.compania,
                        "Asegurado": p.asegurado,
                        "Contratante": p.contratante,
                        "Tipo": p.tipo_seguro,
                        "N° Póliza": p.numero_poliza,
                        "Colectivo / Individual": p.colectivo_individual,
                        "Alias / Patente": p.alias_patente,
                        "Monto (UF)": p.capital_asegurado,
                        "Prima": p.prima_mensual,
                        "Medio de Pago": p.medio_pago,
                        "Fecha Contratación": getattr(p, "fecha_contratacion", "") or "",
                        "¿APV Póliza?": bool(getattr(p, "es_apv_poliza", False)),
                        "Coberturas": p.coberturas,
                        "Análisis IA": p.analisis_ia
                    } for p in prospect.insurances])
                    if df_poliza.empty:
                        df_poliza = pd.DataFrame(columns=["Aseguradora", "Asegurado", "Contratante", "Tipo", "N° Póliza", "Colectivo / Individual", "Alias / Patente", "Monto (UF)", "Prima", "Medio de Pago", "Fecha Contratación", "¿APV Póliza?", "Coberturas", "Análisis IA"])
                    
                    df_debt = pd.DataFrame([{
                        "Institucion": d.institucion,
                        "Tipo_Credito": d.tipo_credito,
                        "Monto Original": d.monto_original,
                        "Monto Actual": d.monto_actual,
                        "Carga Financiera": d.carga_financiera,
                        "Otorgamiento": d.fecha_otorgamiento,
                        "Vencimiento": d.fecha_vencimiento,
                        "Mora": d.monto_mora,
                        "Observaciones": getattr(d, "observaciones", "")
                    } for d in prospect.debts if d.institucion and str(d.institucion).strip() not in ["", "None", "nan"]])
                    if df_debt.empty:
                        df_debt = pd.DataFrame(columns=["Institucion", "Tipo_Credito", "Monto Original", "Monto Actual", "Carga Financiera", "Otorgamiento", "Vencimiento", "Mora", "Observaciones"])
                    else:
                        mask_valid = df_debt["Institucion"].notna() & (~df_debt["Institucion"].astype(str).str.strip().isin(["", "None", "nan"]))
                        df_debt = df_debt[mask_valid].reset_index(drop=True)
                
                    # INICIO EXTRAER SOCIEDADES (Directas + Relacionadas)
                    comp_list = []
                    for c in prospect.companies:
                        comp_list.append({
                            "RUT Empresa": c.rut_empresa,
                            "Razón Social": c.razon_social,
                            "Incorporación": c.fecha_incorporacion,
                            "% Capital": c.porcentaje_capital,
                            "% Utilidades": c.porcentaje_utilidades,
                            "Última Actualización": "",
                            "Observaciones": ""
                        })
                
                    my_clean = prospect.rut.replace(".", "").upper() if prospect.rut else ""
                    if my_clean:
                        from src.database.models import CompanyShareholder, Prospect as ProspectModel
                        socios_inversos = db.query(CompanyShareholder).all()
                        for socio in socios_inversos:
                            if socio.rut and socio.rut.replace(".", "").upper() == my_clean:
                                empresa = db.query(ProspectModel).filter_by(id=socio.prospect_id).first()
                                if empresa:
                                    if not any(x["RUT Empresa"] == empresa.rut for x in comp_list):
                                        comp_list.append({
                                            "RUT Empresa": empresa.rut,
                                            "Razón Social": empresa.nombre,
                                            "Incorporación": "[Falta Fecha]",
                                            "% Capital": socio.porcentaje_participacion,
                                            "% Utilidades": socio.porcentaje_participacion,
                                            "Última Actualización": "Cruce CRM",
                                            "Observaciones": "Extraído desde socios de la empresa."
                                        })
                                    
                    df_comp = pd.DataFrame(comp_list)
                    if df_comp.empty:
                        df_comp = pd.DataFrame(columns=["RUT Empresa", "Razón Social", "Incorporación", "% Capital", "% Utilidades", "Última Actualización", "Observaciones"])
                    
                    df_inv = pd.DataFrame([{
                        "Institucion": i.institucion,
                        "Activo": i.activo,
                        "Tipo": i.tipo_activo,
                        "Monto": i.monto_original,
                        "Moneda": i.moneda_original,
                        "Monto CLP": i.monto_clp
                    } for i in prospect.portfolios])
                    if df_inv.empty:
                        df_inv = pd.DataFrame(columns=["Institucion", "Activo", "Tipo", "Monto", "Moneda", "Monto CLP"])

                    if prospect.company_shareholders:
                        df_socios = pd.DataFrame([{
                            "RUT": s.rut, "Nombre": s.nombre,
                            "% Participación": s.porcentaje_participacion, "Capital Aportado": s.capital_aportado
                        } for s in prospect.company_shareholders])
                    
                    if prospect.company_representatives:
                        df_repres = pd.DataFrame([{
                            "RUT": r.rut, "Nombre": r.nombre,
                            "Poderes y Restricciones": r.poderes_restricciones
                        } for r in prospect.company_representatives])

                    if prospect.profile:
                        nota_val = prospect.profile.notas_neuroventas or ""
                        alerta_val = prospect.profile.alertas_sistema or ""
                        tipo_persona_val = getattr(prospect.profile, 'tipo_persona', 'PN') or 'PN'
                        fecha_const_val = getattr(prospect.profile, 'fecha_constitucion', None)
                        notaria_val = getattr(prospect.profile, 'notaria_constitucion', "") or ""
                        repertorio_val = getattr(prospect.profile, 'repertorio_constitucion', "") or ""
                        fecha_vig_val = getattr(prospect.profile, 'fecha_ultima_vigencia', None)
                        doc_legal_val = getattr(prospect.profile, 'documentos_legales_path', "") or ""
                        perfil_val = getattr(prospect.profile, 'nivel_riesgo', "Moderado") or "Moderado"
                        objetivo_val = getattr(prospect.profile, 'objetivo_inversion', "Otro") or "Otro"
                        f_seguros_val = getattr(prospect.profile, 'fecha_ultima_act_seguros', None)
                        f_deudas_val = getattr(prospect.profile, 'fecha_ultima_act_deudas', None)
                        
                        secciones_omit = []
                        if getattr(prospect.profile, 'secciones_omitidas', None):
                            try:
                                secciones_omit = json.loads(prospect.profile.secciones_omitidas)
                            except:
                                pass
                    
                        if not heirs and prospect.profile.cantidad_herederos == 0:
                            na_val = True
                            
                    nombre_val = prospect.nombre or ""
                    telefono_val = prospect.telefono or ""
                    email_val = prospect.email or ""

                db.close()

                df_hered["Fecha de Nacimiento"] = pd.to_datetime(df_hered["Fecha de Nacimiento"], errors='coerce')
                df_hered["% Asignación"] = pd.to_numeric(df_hered["% Asignación"], errors='coerce')
                df_prop["Fecha Escritura"] = pd.to_datetime(df_prop["Fecha Escritura"], errors='coerce')
            
                st.session_state[k_hered] = df_hered
                st.session_state[k_prop] = df_prop
                st.session_state[k_poliza] = df_poliza
                st.session_state[k_debt] = df_debt
                st.session_state[k_comp] = df_comp
                st.session_state[k_na] = na_val
                st.session_state[k_test] = False
                st.session_state[k_nota] = nota_val
                st.session_state[k_alerta] = alerta_val if 'alerta_val' in locals() else ""
                st.session_state[k_tipo_persona] = tipo_persona_val
                st.session_state[k_socios] = df_socios
                st.session_state[k_repres] = df_repres
                st.session_state[k_inv] = df_inv
                st.session_state[k_fecha_const] = fecha_const_val
                st.session_state[k_notaria] = notaria_val
                st.session_state[k_repertorio] = repertorio_val
                st.session_state[k_fecha_vig] = fecha_vig_val
                st.session_state[k_doc_legal] = doc_legal_val
                st.session_state[f"{rut}_nombre"] = nombre_val
                st.session_state[f"{rut}_telefono"] = telefono_val
                st.session_state[f"{rut}_email"] = email_val
                st.session_state[f"{rut}_perfil"] = perfil_val
                st.session_state[f"{rut}_objetivo"] = objetivo_val
                
                if 'f_seguros_val' in locals():
                    st.session_state[f"{rut}_f_seguros"] = f_seguros_val
                    st.session_state[f"{rut}_f_deudas"] = f_deudas_val
                else:
                    st.session_state[f"{rut}_f_seguros"] = None
                    st.session_state[f"{rut}_f_deudas"] = None
                
                if 'secciones_omit' not in locals():
                    secciones_omit = []
                st.session_state[f"omit_{rut}_sii"] = "sii" in secciones_omit
                st.session_state[f"omit_{rut}_inmobiliaria"] = "inmobiliaria" in secciones_omit
                st.session_state[f"omit_{rut}_seguros"] = "seguros" in secciones_omit
                st.session_state[f"omit_{rut}_deudas"] = "deudas" in secciones_omit
                st.session_state[f"omit_{rut}_inversiones"] = "inversiones" in secciones_omit

            if not st.session_state[k_prop].empty:
                if not pd.api.types.is_datetime64_any_dtype(st.session_state[k_prop]["Fecha Escritura"]):
                    st.session_state[k_prop]["Fecha Escritura"] = pd.to_datetime(st.session_state[k_prop]["Fecha Escritura"], errors='coerce')
                if "Fecha Contrato Arriendo" in st.session_state[k_prop].columns and not pd.api.types.is_datetime64_any_dtype(st.session_state[k_prop]["Fecha Contrato Arriendo"]):
                    st.session_state[k_prop]["Fecha Contrato Arriendo"] = pd.to_datetime(st.session_state[k_prop]["Fecha Contrato Arriendo"], errors='coerce')

            # Migración columnas propiedades SII
            expected_cols = ["Nombre/Alias", "Comuna", "ROL", "Dirección", "Destino", "Fojas", "Número", "Año", "% de Derecho", "Avalúo Fiscal (CLP)", "Valor Com. (UF)", "Deuda Hipotecaria", "Institución Hipoteca", "Monto Inicial (UF)", "Saldo Actual (UF)", "Monto Asegurado (UF)", "Tasación (UF)", "Tasa Interés (%)", "Tipo Tasa", "Fecha Escritura", "Dividendo", "Cuota Actual", "Total Cuotas", "Arrendada", "Monto Arriendo", "Moneda Arriendo", "Fecha Contrato Arriendo", "Meses Reajuste Arriendo", "Contribuciones Trim.", "Gastos Comunes Mensuales", "Mantención Anual (CLP)", "Plusvalía Esperada (%)", "__fecha_act_cuota"]
            for col in expected_cols:
                if col not in st.session_state[k_prop].columns:
                    st.session_state[k_prop][col] = None
        
            # Eliminar la antigua Avalúo (CLP) si existe
            if "Avalúo (CLP)" in st.session_state[k_prop].columns and "Avalúo Fiscal (CLP)" in st.session_state[k_prop].columns:
                st.session_state[k_prop] = st.session_state[k_prop].drop(columns=["Avalúo (CLP)"])

            # UI Toggle para Persona Natural o Jurídica
            col_t1, col_t2 = st.columns([1, 3])
            with col_t1:
                st.session_state[k_tipo_persona] = st.radio("Tipo de Entidad", ["PN", "PJ"], index=0 if st.session_state.get(k_tipo_persona, "PN") == "PN" else 1, horizontal=True)
        
            missing_herederos = st.session_state[k_hered].empty and not st.session_state[k_na] and st.session_state[k_tipo_persona] == "PN"
            missing_propiedades = st.session_state[k_prop].empty
            missing_polizas = st.session_state[k_poliza].empty

            st.markdown("---")
        
            # --- TABLAS DINÁMICAS ---
            if st.session_state.get(k_tipo_persona, "PN") == "PN":
                with st.expander("👨‍👩‍👧‍👦 (1) Datos Personales y Sucesión"):
                    st.info("ℹ️ Permite registrar o actualizar a un cliente/prospecto, su perfil de inversionista y calcular asignaciones legales.")
                    
                    st.markdown("#### Datos Personales")
                    col_dp1, col_dp2, col_dp3 = st.columns(3)
                    with col_dp1:
                        st.session_state[f"{rut}_nombre"] = st.text_input("Nombre Completo", value=st.session_state[f"{rut}_nombre"])
                    with col_dp2:
                        st.session_state[f"{rut}_telefono"] = st.text_input("Teléfono", value=st.session_state[f"{rut}_telefono"])
                    with col_dp3:
                        st.session_state[f"{rut}_email"] = st.text_input("Email", value=st.session_state[f"{rut}_email"])
                    
                    col_dp4, col_dp5 = st.columns(2)
                    
                    opciones_perfil = [
                        "Muy conservador (0% Renta variable)",
                        "Conservador (10% Máxima exposición Renta variable)",
                        "Cauteloso (25% Máxima exposición Renta variable)",
                        "Moderado (50% Máxima exposición Renta variable)",
                        "Decidido (75% Máxima exposición Renta variable)",
                        "Agresivo (100% Máxima exposición Renta variable)"
                    ]
                    
                    # Normalizar valor anterior
                    perfil_actual = st.session_state[f"{rut}_perfil"]
                    perfil_index = 3
                    for i, opc in enumerate(opciones_perfil):
                        if perfil_actual.lower() in opc.lower():
                            perfil_index = i
                            break
                    
                    with col_dp4:
                        st.session_state[f"{rut}_perfil"] = st.selectbox("Perfil de Inversionista", opciones_perfil, index=perfil_index)
                    
                    opciones_obj = ["Jubilación", "Compra de vivienda", "Fondo de emergencia", "Educación de los Hijos", "Preservación de Capital", "Crecimiento a Largo Plazo", "Otro"]
                    obj_actual = st.session_state[f"{rut}_objetivo"]
                    if obj_actual not in opciones_obj:
                        obj_actual = "Otro"
                        
                    with col_dp5:
                        st.session_state[f"{rut}_objetivo"] = st.selectbox("Principales Objetivos de Inversión", opciones_obj, index=opciones_obj.index(obj_actual))
                    
                    st.markdown("---")
                    st.markdown("#### 🏥 Estado Previsional y Régimen de Jubilación")
                    col_prev1, col_prev2 = st.columns(2)
                    with col_prev1:
                        prev_options = ["Cotizante Activo / Sueldo Empresarial", "Pensionado Retiro Programado (AFP)", "Pensionado Renta Vitalicia Simple", "Pensionado Renta Vitalicia Garantizada"]
                        curr_prev = st.session_state.get(f"{rut}_estado_prev", "Cotizante Activo / Sueldo Empresarial")
                        if curr_prev not in prev_options: curr_prev = "Cotizante Activo / Sueldo Empresarial"
                        st.session_state[f"{rut}_estado_prev"] = st.selectbox("Estado Previsional del Cliente", prev_options, index=prev_options.index(curr_prev))
                    with col_prev2:
                        if st.session_state[f"{rut}_estado_prev"] == "Pensionado Renta Vitalicia Garantizada":
                            st.session_state[f"{rut}_rv_anios"] = st.number_input("Período Garantizado Renta Vitalicia (Años)", min_value=1, max_value=30, value=int(st.session_state.get(f"{rut}_rv_anios", 15) or 15))
                        else:
                            st.session_state[f"{rut}_rv_anios"] = 0
                    st.markdown("#### Audio y Notas de Psicología (Neuroventas)")
                    st.info("ℹ️ Apuntes cualitativos, miedos, intereses y análisis de audio del cliente para preparar la próxima reunión.")
                    st.session_state[k_nota] = st.text_area("Agrega comentarios clave para la próxima reunión (intereses, miedos, familia):", value=st.session_state.get(k_nota, ""), height=150)
                    # Reproducir audio guardado si existe
                    db_temp = SessionLocal()
                    prospect_temp = db_temp.query(Prospect).filter(Prospect.rut == rut).first()
                    saved_audio_path = prospect_temp.profile.audio_path if prospect_temp and prospect_temp.profile else None
                    if saved_audio_path:
                        st.markdown("**🎙️ Audio guardado anteriormente:**")
                        if os.path.exists(saved_audio_path):
                            st.audio(saved_audio_path)
                        else:
                            st.warning("El archivo de audio físico no se encontró en el servidor.")
                    
                    c_audio1, c_audio2 = st.columns(2)
                    with c_audio1:
                        uploaded_audio_dp = st.file_uploader("Adjuntar nota de audio (opcional):", type=["mp3", "wav", "mp4", "m4a", "ogg", "aac"], key=f"audio_up_{rut}_1")
                    with c_audio2:
                        recorded_audio_dp = st.audio_input("🎙️ Grabar nota de voz desde tu PC:", key=f"audio_rec_{rut}_1")
                    db_temp.close()
                    
                    audio_to_process_bytes = None
                    if recorded_audio_dp:
                        audio_to_process_bytes = recorded_audio_dp.getvalue()
                    elif uploaded_audio_dp:
                        audio_to_process_bytes = uploaded_audio_dp.getvalue()
                    elif saved_audio_path and os.path.exists(saved_audio_path):
                        with open(saved_audio_path, "rb") as f:
                            audio_to_process_bytes = f.read()
                    
                    if audio_to_process_bytes:
                        if st.button("🧠 Procesar Audio con IA (Neurociencia)"):
                            with st.spinner("Escuchando y analizando..."):
                                from src.intelligence.audio_processor import process_client_audio
                                resultado_ia = process_client_audio(audio_to_process_bytes)
                                st.session_state[k_nota] = (st.session_state.get(k_nota, "") + "\n\n=== ANÁLISIS IA ===\n" + resultado_ia).strip()
                                st.rerun()
                    
                    st.markdown("---")
                    st.markdown("#### Sucesión Familiar")
                    col_fam1, col_fam2, col_fam3 = st.columns(3)
                    with col_fam1:
                        st.session_state[k_na] = st.checkbox("No aplica (Sin herederos / Soltero sin hijos)", value=st.session_state[k_na])
                    with col_fam2:
                        st.session_state[k_test] = st.checkbox("Existe Testamento Vigente", value=st.session_state[k_test], help="Si hay testamento, los cálculos legales asumen que solo se debe garantizar la Mitad Legitimaria (50%) a los herederos forzosos.")
                    with col_fam3:
                        st.session_state[f"{rut}_patrimonio"] = st.number_input("Patrimonio Neto a Repartir (UF)", value=st.session_state.get(f"{rut}_patrimonio", 0.0), min_value=0.0, step=1000.0, format="%.2f", help="Ingresa un estimado para calcular el impuesto a la herencia y liquidez por heredero.")
                
                    edited_herederos = st.session_state[k_hered]
            
                    if not st.session_state[k_na]:
                        # Renderear data_editor usando la base de datos en session_state y una llave única
                        # Guardamos el resultado en edited_herederos en lugar de sobrescribir el origen inmediatamente
                        
                        # Add new columns to the dataframe if they don't exist yet for visualization
                        for col in ["Monto Herencia (UF)", "Impuesto Estimado (UF)", "Líquido a Recibir (UF)"]:
                            if col not in st.session_state[k_hered].columns:
                                st.session_state[k_hered][col] = 0.0
                                
                        edited_herederos = st.data_editor(
                            st.session_state[k_hered], 
                            num_rows="dynamic", 
                            use_container_width=True, 
                            key=f"editor_herederos_{rut}",
                            column_config={
                                "Relación": st.column_config.SelectboxColumn(
                                    "Relación",
                                    options=["Cónyuge", "Hijo/a", "Nieto/a", "Padre/Madre", "Hermano/a", "Sobrino/a", "Conviviente Civil", "Otro"]
                                ),
                                "Fecha de Nacimiento": st.column_config.DateColumn(
                                    "Fecha de Nacimiento",
                                    format="DD/MM/YYYY",
                                    min_value=datetime.date(1900, 1, 1),
                                    max_value=datetime.date.today(),
                                ),
                                "% Asignación": st.column_config.NumberColumn(
                                    "% Asignación",
                                    min_value=0.0,
                                    max_value=100.0,
                                    step=1.0,
                                    format="%.2f%%"
                                ),
                                "¿Estudiante (18-24 años)?": st.column_config.CheckboxColumn(
                                    "¿Estudiante (18-24 años)?",
                                    help="Pensión de Sobrevivencia para hijos estudiantes regulares entre 18 y 24 años (DL 3500 Art. 5 y 58)"
                                ),
                                "Monto Herencia (UF)": st.column_config.NumberColumn("Monto (UF)", format="%.2f", disabled=True),
                                "Impuesto Estimado (UF)": st.column_config.NumberColumn("Impuesto (UF)", format="%.2f", disabled=True),
                                "Líquido a Recibir (UF)": st.column_config.NumberColumn("Líquido (UF)", format="%.2f", disabled=True),
                            }
                        )

                        if st.button("⚖️ Calcular Asignación Legal (Ley Chilena)"):
                            # Calculamos sobre la versión editada para capturar las nuevas filas
                            new_df = calculate_inheritance_chile(edited_herederos, st.session_state[k_test], st.session_state[f"{rut}_patrimonio"])
                            # Actualizamos la base de datos
                            st.session_state[k_hered] = new_df
                            # Limpiamos el estado del widget para forzar que tome la nueva base
                            if f"editor_herederos_{rut}" in st.session_state:
                                del st.session_state[f"editor_herederos_{rut}"]
                            st.rerun()
                    
                        if st.session_state[k_test]:
                            st.info("💡 **Modo Testamento:** Se ha calculado el mínimo legal garantizado (Mitad Legitimaria, equivalente al 50% del patrimonio). El 50% restante corresponde a la Cuarta de Mejoras y Cuarta de Libre Disposición.")
                            st.markdown("""
                            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #0056b3; margin-top: 10px;'>
                            <b>📌 Ley de Herencias en Chile (con Testamento):</b><br>
                            - <b>Mitad Legitimaria (50%):</b> Para los herederos forzosos (cónyuge e hijos). Es intocable.<br>
                            - <b>Cuarta de Mejoras (25%):</b> Se puede usar para "mejorar" la cuota de cónyuge, descendientes o ascendientes exclusivamente.<br>
                            - <b>Cuarta de Libre Disposición (25%):</b> Se puede dejar a <b>cualquier persona</b> o institución (no requiere ser familiar).
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #0056b3; margin-top: 10px;'>
                            <b>📌 Ley de Herencias en Chile (sin Testamento / Intestada):</b><br>
                            - El patrimonio se divide según los "Órdenes de Sucesión" que dicta la ley.<br>
                            - Si hay cónyuge e hijos (Primer Orden): El cónyuge recibe el doble que cada hijo, asegurando al menos el 25% del total.<br>
                            - Todo el patrimonio se reparte bajo esta regla; no hay porcentajes de libre disposición.
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown("---")
                        # Botón para descargar Reporte Sucesorio Completo PDF
                        from src.utils.pdf_generator import generate_succession_report_pdf
                        try:
                            pdf_suc_bytes = generate_succession_report_pdf(prospect.id) if prospect else None
                        except:
                            pdf_suc_bytes = None

                        if pdf_suc_bytes:
                            st.download_button(
                                label="📜 Descargar Informe Executive Sucesorio y Análisis Legal (PDF)",
                                data=pdf_suc_bytes,
                                file_name=f"Informe_Sucesorio_Legal_{rut}.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                                key=f"dl_suc_pdf_{rut}"
                            )
            else:
                with st.expander("🏛️ (1) Datos de la Sociedad y Representación"):
                    st.info("ℹ️ Permite procesar informes legales para extraer datos societarios y de representación legal.")
            
                    st.info("Sube el Informe Legal o Documentos de Constitución (PDF) para extraer los datos con IA.")
                    doc_legal = st.file_uploader("Subir Informe Legal (PDF)", type=["pdf"], key=f"legal_{rut}", accept_multiple_files=True)
                    if doc_legal:
                        if st.button("Procesar Informe con IA", type="primary"):
                            with st.spinner("Analizando documento con IA (esto tomará unos segundos)..."):
                                try:
                                    import sys
                                    import importlib
                                    import src.osint.parser_informe_legal
                                    importlib.reload(src.osint.parser_informe_legal)
                                    from src.osint.parser_informe_legal import LegalReportParser
                                    parser = LegalReportParser()
                                    datos = parser.parse_pdfs([doc.getvalue() for doc in doc_legal])
                            
                                    st.session_state[k_fecha_const] = pd.to_datetime(datos.get("fecha_constitucion"), errors='coerce').date() if datos.get("fecha_constitucion") else None
                                    st.session_state[k_notaria] = datos.get("notaria_constitucion", "") or ""
                                    st.session_state[k_repertorio] = datos.get("repertorio_constitucion", "") or ""
                                    st.session_state[k_fecha_vig] = pd.to_datetime(datos.get("fecha_ultima_vigencia"), errors='coerce').date() if datos.get("fecha_ultima_vigencia") else None
                            
                                    if datos.get("socios"):
                                        df_s = pd.DataFrame(datos["socios"])
                                        df_s = df_s.rename(columns={"rut": "RUT", "nombre": "Nombre", "porcentaje_participacion": "% Participación", "capital_aportado": "Capital Aportado"})
                                        st.session_state[k_socios] = df_s
                            
                                    if datos.get("representantes"):
                                        df_r = pd.DataFrame(datos["representantes"])
                                        df_r = df_r.rename(columns={"rut": "RUT", "nombre": "Nombre", "poderes_restricciones": "Poderes y Restricciones"})
                                        st.session_state[k_repres] = df_r
                                
                                    st.success("¡Datos extraídos correctamente! Por favor, verifica la información abajo y presiona 'Guardar y Actualizar Perfil Integral'.")
                                except Exception as e:
                                    st.error(f"Error procesando el PDF con IA: {e}")

                    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
                    with col_c1:
                        st.session_state[k_fecha_const] = st.date_input("Fecha Constitución", value=st.session_state[k_fecha_const] if isinstance(st.session_state[k_fecha_const], datetime.date) else None)
                    with col_c2:
                        st.session_state[k_notaria] = st.text_input("Notaría", value=st.session_state[k_notaria])
                    with col_c3:
                        st.session_state[k_repertorio] = st.text_input("Repertorio", value=st.session_state[k_repertorio])
                    with col_c4:
                        st.session_state[k_fecha_vig] = st.date_input("Última Vigencia", value=st.session_state[k_fecha_vig] if isinstance(st.session_state[k_fecha_vig], datetime.date) else None)

                    st.markdown("##### Accionistas / Socios")
                    edited_socios = st.data_editor(st.session_state[k_socios], num_rows="dynamic", use_container_width=True, key=f"ed_socios_{rut}")

                    st.markdown("##### Representantes Legales / Apoderados")
                    edited_repres = st.data_editor(st.session_state[k_repres], num_rows="dynamic", use_container_width=True, key=f"ed_repres_{rut}")


            with st.expander("🏢 (2) Perfil Tributario y Sociedades (SII)"):
                st.session_state[f"omit_{rut}_sii"] = st.checkbox("Omitir sección", value=st.session_state.get(f"omit_{rut}_sii", False), key=f"cb_omit_{rut}_sii")
                if st.session_state[f"omit_{rut}_sii"]:
                    st.info("⚠️ La sección de Perfil Tributario fue omitida intencionalmente.")
                    if st.button("Restaurar Sección", key=f"rest_{rut}_sii"):
                        st.session_state[f"omit_{rut}_sii"] = False
                        st.rerun()
                else:
                    st.info("ℹ️ Información sobre las empresas en las que el cliente tiene participación y sus propiedades.")
                    with st.expander("📥 Importar desde Carpeta Tributaria (SII)", expanded=False):
                        st.info("Sube el PDF de la Carpeta Tributaria para extraer participaciones societarias.")
                        render_manual_button("manual_sii_carpeta.pdf", "📄 Descargar Manual SII (Carpeta Tributaria)")
                        sii_pdf_file = st.file_uploader("Subir PDF Carpeta Tributaria", type=["pdf"], key=f"sii_pdf_{rut}")
                        if sii_pdf_file:
                            if st.button("Procesar Sociedades", type="primary"):
                                with st.spinner("Extrayendo..."):
                                    import sys
                                    import importlib
                                    import src.osint.parser_sii
                                    importlib.reload(src.osint.parser_sii)
                                    from src.osint.parser_sii import parse_sii_carpeta_pdf
                                    df_sociedades, renta, df_propiedades = parse_sii_carpeta_pdf(sii_pdf_file.getvalue())
                        
                                    if not df_sociedades.empty:
                                        import datetime as dt_lib
                                        now_str = dt_lib.datetime.now().strftime("%Y-%m-%d %H:%M")
                            
                                        current_df = st.session_state[k_comp].copy()
                                        if "Última Actualización" not in current_df.columns:
                                            current_df["Última Actualización"] = ""
                                        if "Observaciones" not in current_df.columns:
                                            current_df["Observaciones"] = ""
                                
                                        for idx, new_row in df_sociedades.iterrows():
                                            rut_nueva = new_row.get("RUT Empresa", "")
                                            match_idx = current_df[current_df["RUT Empresa"] == rut_nueva].index
                                
                                            if len(match_idx) > 0:
                                                # Ya existe, actualizar y anotar diferencias
                                                idx_to_update = match_idx[0]
                                                old_cap = current_df.at[idx_to_update, "% Capital"]
                                                new_cap = new_row.get("% Capital", "")
                                                obs = "Actualizado vía PDF."
                                                if str(old_cap) != str(new_cap) and str(old_cap) != "nan" and old_cap:
                                                    obs += f" Capital previo: {old_cap}%."
                                    
                                                current_df.at[idx_to_update, "Incorporación"] = new_row.get("Incorporación", current_df.at[idx_to_update, "Incorporación"])
                                                current_df.at[idx_to_update, "% Capital"] = new_cap
                                                current_df.at[idx_to_update, "% Utilidades"] = new_row.get("% Utilidades", "")
                                                current_df.at[idx_to_update, "Última Actualización"] = now_str
                                                current_df.at[idx_to_update, "Observaciones"] = obs
                                            else:
                                                # Es nueva
                                                new_row_dict = new_row.to_dict()
                                                new_row_dict["Última Actualización"] = now_str
                                                new_row_dict["Observaciones"] = "Importado desde PDF SII."
                                                current_df = pd.concat([current_df, pd.DataFrame([new_row_dict])], ignore_index=True)
                                    
                                        st.session_state[k_comp] = current_df
                                        st.success(f"Se procesaron {len(df_sociedades)} sociedades del PDF (actualizadas o añadidas).")
                                        if f"editor_sociedades_{rut}" in st.session_state:
                                            del st.session_state[f"editor_sociedades_{rut}"]
                                    else:
                                        st.warning("No se encontraron sociedades en este documento.")
                            
                                    if not df_propiedades.empty:
                                        existing_rols = [str(r).strip() for r in st.session_state[k_prop]["ROL"].tolist() if str(r).strip() not in ["", "nan", "None"]] if "ROL" in st.session_state[k_prop].columns else []
                                        df_propiedades["_clean_rol"] = df_propiedades["ROL"].astype(str).str.strip()
                                        new_props = df_propiedades[~df_propiedades["_clean_rol"].isin(existing_rols)].drop(columns=["_clean_rol"])
                                
                                        if not new_props.empty:
                                            st.session_state[k_prop] = pd.concat([st.session_state[k_prop], new_props], ignore_index=True)
                                            st.success(f"{len(new_props)} propiedades nuevas importadas desde Carpeta Tributaria.")
                                        else:
                                            st.info("Las propiedades de la Carpeta Tributaria ya estaban registradas (sin duplicados).")
                                    
                                        if f"editor_propiedades_{rut}" in st.session_state:
                                            del st.session_state[f"editor_propiedades_{rut}"]
                        
                                    # Guardar renta en base de datos temporalmente
                                    if renta > 0:
                                        db = SessionLocal()
                                        prospect = db.query(Prospect).filter(Prospect.rut == rut).first()
                                        if prospect and prospect.profile:
                                            prospect.profile.renta_anual_declarada = renta
                                            db.commit()
                                        db.close()
                                        st.success(f"Renta anual declarada capturada: ${renta:,.0f} CLP")
                            
                                st.rerun()

                    # Validación visual para campos vacíos (Missing Info)
                    current_df = st.session_state[k_comp]
                    if not current_df.empty:
                        if current_df['Incorporación'].astype(str).str.contains(r'Falta Fecha|None', regex=True, case=False).any() or current_df['Incorporación'].isnull().any():
                            st.warning("⚠️ **Información Incompleta:** Algunas sociedades cruzadas desde el CRM no tienen fecha de incorporación. Por favor, edita la celda correspondiente para completarla o sube una carpeta tributaria.")

                    edited_sociedades = st.data_editor(
                        current_df,
                        num_rows="dynamic",
                        use_container_width=True,
                        key=f"editor_sociedades_{rut}"
                    )

            with st.expander("🏠 (3) Cartera Inmobiliaria"):
                st.session_state[f"omit_{rut}_inmobiliaria"] = st.checkbox("Omitir sección", value=st.session_state.get(f"omit_{rut}_inmobiliaria", False), key=f"cb_omit_{rut}_inmobiliaria")
                if st.session_state[f"omit_{rut}_inmobiliaria"]:
                    st.info(" La seccin de Cartera Inmobiliaria fue omitida intencionalmente.")
                else:
                    st.info("ℹ️ Detalle de bienes raíces, avalúos, créditos hipotecarios y cálculos de rentabilidad inmobiliaria.")
        
                    # BOTÓN DE AUDITORÍA Y BÚSQUEDA AUTOMÁTICA POR RUT / CATASTRO NACIONAL (dequienes.cl / SII)
                    if st.button("🏢 Auditar / Consultar Propiedades por RUT (Catastro Nacional)", key=f"btn_lookup_prop_{rut}", use_container_width=True):
                        try:
                            from src.osint.property_lookup_engine import PropertyLookupEngine
                            engine_prop = PropertyLookupEngine()
                            df_p = st.session_state[k_prop].copy()
                            
                            # 1. Eliminar filas ficticias de prueba previo (ROL 1420-0012, 1420-0055 o alias Catastro)
                            if not df_p.empty and "ROL" in df_p.columns:
                                df_p = df_p[~df_p["ROL"].astype(str).str.strip().isin(["1420-0012", "1420-0055"])]
                            if not df_p.empty and "Nombre/Alias" in df_p.columns:
                                df_p = df_p[~df_p["Nombre/Alias"].astype(str).str.contains("Catastro", case=False, na=False)]
                            
                            # 2. Recalcular Factor AI y Valor Sugerido AI (UF), preservando tasaciones reales ingresadas por el cliente
                            updated_count = 0
                            if not df_p.empty:
                                for idx, row in df_p.iterrows():
                                    avaluo = float(row.get("Avalúo Fiscal (CLP)", 0.0) or 0.0)
                                    comuna = str(row.get("Comuna", "")).strip()
                                    destino = str(row.get("Destino", "HABITACIONAL")).strip()
                                    
                                    val_sugerido_uf, factor_total = engine_prop.estimate_commercial_value_uf(avaluo, comuna, destino)
                                    df_p.at[idx, "Factor Estimación"] = f"{factor_total:.2f}x"
                                    df_p.at[idx, "Valor Sugerido AI (UF)"] = val_sugerido_uf
                                    
                                    # Verificar si el cliente ingresó una tasación personalizada (ej: 10.000 UF / 5.500 UF)
                                    val_actual_uf = float(row.get("Valor Com. (UF)", 0.0) or 0.0)
                                    origen_prev = str(row.get("Origen Tasación", "")).strip()
                                    
                                    if origen_prev == "Tasación Real / Cliente" or (val_actual_uf > 0 and abs(val_actual_uf - val_sugerido_uf) > 1.0):
                                        # PRESERVAR VALORACIÓN PROPIA DEL CLIENTE
                                        df_p.at[idx, "Origen Tasación"] = "Tasación Real / Cliente"
                                    else:
                                        # Asignar sugerido por AI por defecto
                                        df_p.at[idx, "Valor Com. (UF)"] = val_sugerido_uf
                                        df_p.at[idx, "Origen Tasación"] = "Sugerida por AI"
                                        
                                    updated_count += 1
                                        
                            st.session_state[k_prop] = df_p
                            if f"editor_propiedades_{rut}" in st.session_state:
                                del st.session_state[f"editor_propiedades_{rut}"]
                                
                            st.success(f"✅ Auditoría completada: Se actualizaron los factores de estimación AI para {updated_count} propiedades y se preservaron tus tasaciones reales del cliente.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error consultando catastro inmobiliario: {e}")
        
                    with st.expander("📥 Importar desde Excel de Bienes Raíces (SII)", expanded=False):
                        st.info("Sube el archivo Excel descargado desde la página del SII ('Consultar mis bienes raíces').")
                        render_manual_button("manual_sii_bienes_raices.pdf", "📄 Descargar Manual SII (Bienes Raíces)")
                        sii_file = st.file_uploader("Subir Excel SII", type=["xlsx", "xls"], key=f"sii_file_{rut}")
                        if sii_file:
                            if st.button("Procesar Excel SII"):
                                try:
                                    df_sii = pd.read_excel(sii_file)
                                    nuevas_propiedades = []
                                    existing_rols = [str(r).strip() for r in st.session_state[k_prop]["ROL"].tolist() if str(r).strip() not in ["", "nan", "None"]] if "ROL" in st.session_state[k_prop].columns else []
                            
                                    for _, row in df_sii.iterrows():
                                        rol_val = str(row.get("ROL", "")).strip()
                                        if rol_val in existing_rols and rol_val != "":
                                            continue  # Evitar duplicados
                                    
                                        val_avaluo = str(row.get("Avalúo Fiscal", "0")).replace("$", "").replace(".", "").strip()
                                        try:
                                            val_avaluo = float(val_avaluo)
                                        except:
                                            val_avaluo = 0.0
                            
                                        porcentaje = str(row.get("% de Derecho de la propiedad", "100")).replace("%", "").strip()
                                        try:
                                            porcentaje = float(porcentaje)
                                        except:
                                            porcentaje = 100.0

                                        nueva_prop = {
                                            "Nombre/Alias": "Propiedad SII",
                                            "Comuna": str(row.get("Comuna", "")),
                                            "ROL": str(row.get("ROL", "")),
                                            "Dirección": str(row.get("Dirección", "")),
                                            "Destino": str(row.get("Destino", "")),
                                            "Fojas": str(row.get("Fojas", "")),
                                            "Número": str(row.get("Número", "")),
                                            "Año": str(row.get("Año", "")),
                                            "% de Derecho": porcentaje,
                                            "Avalúo Fiscal (CLP)": val_avaluo,
                                            "Valor Com. (UF)": 0.0,
                                            "Deuda Hipotecaria": False,
                                            "Institución Hipoteca": "",
                                            "Monto Inicial (UF)": 0.0,
                                            "Saldo Actual (UF)": 0.0,
                                            "Monto Asegurado (UF)": 0.0,
                                            "Tasación (UF)": 0.0,
                                            "Tasa Interés (%)": 0.0,
                                            "Tipo Tasa": "",
                                            "Fecha Escritura": "",
                                            "Dividendo": 0.0,
                                            "Cuota Actual": 0,
                                            "Total Cuotas": 0,
                                            "Arrendada": False,
                                            "Monto Arriendo": 0.0,
                                            "Moneda Arriendo": "CLP",
                                            "Fecha Contrato Arriendo": "",
                                            "Meses Reajuste Arriendo": 12,
                                            "Contribuciones Trim.": 0.0,
                                            "Gastos Comunes Mensuales": 0.0,
                                            "Mantención Anual (CLP)": 0.0,
                                            "Plusvalía Esperada (%)": 0.0,
                                            "__fecha_act_cuota": None
                                        }
                                        nuevas_propiedades.append(nueva_prop)
                        
                                    if nuevas_propiedades:
                                        st.session_state[k_prop] = pd.concat([st.session_state[k_prop], pd.DataFrame(nuevas_propiedades)], ignore_index=True)
                                        if f"editor_propiedades_{rut}" in st.session_state:
                                            del st.session_state[f"editor_propiedades_{rut}"]
                                        st.success(f"{len(nuevas_propiedades)} propiedades importadas exitosamente.")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error procesando Excel: {e}")

                    # Asegurar columnas de auditoría AI y tasación cliente
                    df_props_curr = st.session_state[k_prop].copy()
                    if not df_props_curr.empty:
                        from src.osint.property_lookup_engine import PropertyLookupEngine
                        engine_prop = PropertyLookupEngine()
                        changed_cols = False
                        if "Factor Estimación" not in df_props_curr.columns:
                            df_props_curr["Factor Estimación"] = "1.85x"
                            changed_cols = True
                        if "Valor Sugerido AI (UF)" not in df_props_curr.columns:
                            df_props_curr["Valor Sugerido AI (UF)"] = 0.0
                            changed_cols = True
                        if "Origen Tasación" not in df_props_curr.columns:
                            df_props_curr["Origen Tasación"] = "Sugerida por AI"
                            changed_cols = True
                        
                        for idx, row in df_props_curr.iterrows():
                            avaluo = float(row.get("Avalúo Fiscal (CLP)", 0.0) or 0.0)
                            comuna = str(row.get("Comuna", "")).strip()
                            destino = str(row.get("Destino", "HABITACIONAL")).strip()
                            val_sug_uf, factor_tot = engine_prop.estimate_commercial_value_uf(avaluo, comuna, destino)
                            
                            df_props_curr.at[idx, "Factor Estimación"] = f"{factor_tot:.2f}x"
                            df_props_curr.at[idx, "Valor Sugerido AI (UF)"] = val_sug_uf
                            
                            val_com_actual = float(row.get("Valor Com. (UF)", 0.0) or 0.0)
                            if val_com_actual == 0.0:
                                df_props_curr.at[idx, "Valor Com. (UF)"] = val_sug_uf
                                
                        st.session_state[k_prop] = df_props_curr

                    cols = st.session_state[k_prop].columns.tolist()
                    if "Dividendo (CLP)" in cols and "Dividendo" in cols:
                        cols.remove("Dividendo (CLP)")
                        idx = cols.index("Dividendo")
                        cols.insert(idx + 1, "Dividendo (CLP)")
                        st.session_state[k_prop] = st.session_state[k_prop][cols]

                    edited_propiedades = st.data_editor(
                        st.session_state[k_prop], 
                        num_rows="dynamic", 
                        use_container_width=True, 
                        key=f"editor_propiedades_{rut}",
                        column_config={
                            "Deuda Hipotecaria": st.column_config.CheckboxColumn("¿Tiene Deuda?", default=False),
                            "Arrendada": st.column_config.CheckboxColumn("¿Arrendada?", default=False),
                            "Monto Arriendo": st.column_config.NumberColumn(format="$ %,d", min_value=0.0),
                            "Moneda Arriendo": None,
                            "Fecha Contrato Arriendo": st.column_config.DateColumn("Fecha Contrato", format="DD/MM/YYYY", min_value=datetime.date(1950, 1, 1), max_value=datetime.date.today()),
                            "Meses Reajuste Arriendo": st.column_config.NumberColumn("Meses Reajuste", min_value=1, max_value=60, step=1),
                            "Cuota Actual": st.column_config.NumberColumn(min_value=0, step=1),
                            "Total Cuotas": st.column_config.NumberColumn(min_value=0, step=1),
                            "Avalúo Fiscal (CLP)": st.column_config.NumberColumn(format="$ %,d"),
                            "Factor Estimación": st.column_config.TextColumn("Factor AI", help="Multiplicador asignado por Comuna y Destino"),
                            "Valor Sugerido AI (UF)": st.column_config.NumberColumn("Sugerido AI (UF)", format="%.2f UF", help="Estimación calculada por la IA según Avalúo Fiscal"),
                            "Valor Com. (UF)": st.column_config.NumberColumn("Valor Comercial / Tasación (UF)", format="%.2f UF", help="Valor usado para el Informe 360°. Puedes sobreescribirlo con tu tasación real (ej: 10.000 UF)"),
                            "Origen Tasación": st.column_config.SelectboxColumn("Origen Valor", options=["Sugerida por AI", "Tasación Real / Cliente"]),
                            "Monto Inicial (UF)": st.column_config.NumberColumn(format="%.2f UF"),
                            "Saldo Actual (UF)": st.column_config.NumberColumn(format="%.2f UF"),
                            "Monto Asegurado (UF)": st.column_config.NumberColumn(format="%.2f UF"),
                            "Tasación (UF)": st.column_config.NumberColumn(format="%.2f UF"),
                            "Tasa Interés (%)": st.column_config.NumberColumn(format="%.2f%%"),
                            "Tipo Tasa": st.column_config.SelectboxColumn("Tipo Tasa", options=["Fija", "Variable", "Mixta"]),
                            "Fecha Escritura": st.column_config.DateColumn("Fecha Escritura", format="DD/MM/YYYY", min_value=datetime.date(1950, 1, 1), max_value=datetime.date.today()),
                            "Dividendo": st.column_config.NumberColumn("Dividendo (UF)", format="%.2f UF"),
                            "Año": st.column_config.NumberColumn("Año", format="%d", step=1),
                            "Contribuciones Trim.": st.column_config.NumberColumn(format="$ %,d"),
                            "Gastos Comunes Mensuales": st.column_config.NumberColumn(format="$ %,d"),
                            "Mantención Anual (CLP)": st.column_config.NumberColumn(format="$ %,d"),
                            "Plusvalía Esperada (%)": st.column_config.NumberColumn(format="%.2f%%", min_value=0.0, max_value=100.0),
                            "% de Derecho": st.column_config.NumberColumn(format="%.2f%%", min_value=0.0, max_value=100.0),
                            "Rentabilidad S/Deuda (Cap Rate %)": st.column_config.NumberColumn("Cap Rate (%)", format="%.2f%%", disabled=True, help="Rentabilidad de la propiedad asumiendo compra al contado.\n\nFórmula: (Ingreso Operativo Anual / Valor Comercial) * 100\nObjetivo: Evaluar el rendimiento puro del activo inmobiliario sin considerar el apalancamiento bancario."),
                            "Retorno C/Deuda (ROE %)": st.column_config.NumberColumn("ROE (%)", format="%.2f%%", disabled=True, help="Retorno sobre el Patrimonio (Return on Equity).\n\nFórmula: (Flujo de Caja Anual / Patrimonio Inmovilizado) * 100\nObjetivo: Medir la rentabilidad real de la porción que ya has pagado, maximizando el uso del apalancamiento."),
                            "Flujo Caja Anual (CLP)": st.column_config.NumberColumn("Flujo Caja Anual", format="$ %,d", disabled=True, help="Dinero real (liquidez) que produce la propiedad anualmente.\n\nFórmula: Ingresos por Arriendo - (Gastos Operativos + Dividendos Hipotecarios)\nObjetivo: Conocer cuánto dinero líquido te deja (o te cuesta) mantener la propiedad al año."),
                            "Retorno Total (%)": st.column_config.NumberColumn("Retorno Total", format="%.2f%%", disabled=True, help="Ganancia consolidada de la propiedad.\n\nFórmula: ROE (o Cap Rate si no hay deuda) + Plusvalía Esperada Anual\nObjetivo: Visión completa de la creación de riqueza de la propiedad a través del tiempo."),
                            "Dividendo (CLP)": st.column_config.NumberColumn("Dividendo (CLP)", format="$ %,d", disabled=True),
                            "__fecha_act_cuota": None  # Ocultar columna interna
                        }
                    )
        
                    # --- CÁLCULO DE MÉTRICAS INMOBILIARIAS EN VIVO ---
                    from src.osint.indicadores import get_uf_today
                    uf_hoy = get_uf_today()
        
                    def recalc_metrics(df):
                        df = df.copy()
                        for col in ["Rentabilidad S/Deuda (Cap Rate %)", "Retorno C/Deuda (ROE %)", "Flujo Caja Anual (CLP)", "Retorno Total (%)", "Dividendo (CLP)"]:
                            if col not in df.columns:
                                df[col] = 0.0
                    
                        for idx, row in df.iterrows():
                            try:
                                vc_clp = float(row.get('Valor Com. (UF)', 0) or 0) * uf_hoy
                                arr = float(row.get('Monto Arriendo', 0) or 0)
                                con = float(row.get('Contribuciones Trim.', 0) or 0) * 4
                                gas = float(row.get('Gastos Comunes Mensuales', 0) or 0) * 12
                                man = float(row.get('Mantención Anual (CLP)', 0) or 0)
                                div_uf = float(row.get('Dividendo', 0) or 0)
                                div_clp = div_uf * uf_hoy
                                deu_uf = float(row.get('Saldo Actual (UF)', 0) or 0)
                                deu_clp = deu_uf * uf_hoy
                                plu = float(row.get('Plusvalía Esperada (%)', 0) or 0)
                    
                                ingreso_anual = (arr * 12) - con - gas - man
                                cap_rate = (ingreso_anual / vc_clp * 100) if vc_clp > 0 else 0.0
                    
                                patrimonio = vc_clp - deu_clp
                                roe = ((ingreso_anual - (div_clp * 12)) / patrimonio * 100) if patrimonio > 0 else 0.0
                    
                                flujo = ingreso_anual - (div_clp * 12)
                                retorno_total = (roe if row.get('Deuda Hipotecaria', False) and deu_clp > 0 else cap_rate) + plu
                    
                                df.at[idx, 'Dividendo (CLP)'] = div_clp
                                df.at[idx, 'Rentabilidad S/Deuda (Cap Rate %)'] = cap_rate
                                df.at[idx, 'Retorno C/Deuda (ROE %)'] = roe
                                df.at[idx, 'Flujo Caja Anual (CLP)'] = flujo
                                df.at[idx, 'Retorno Total (%)'] = retorno_total
                            except Exception as e:
                                pass
                        return df
            
                    edited_propiedades = recalc_metrics(edited_propiedades)
        
                    # Si las métricas calculadas difieren de session_state, actualizar para reflejarlas en la UI
                    # Solo comparamos las columnas de métricas para evitar reruns infinitos
                    metric_cols = ["Rentabilidad S/Deuda (Cap Rate %)", "Retorno C/Deuda (ROE %)", "Flujo Caja Anual (CLP)", "Retorno Total (%)", "Dividendo (CLP)"]
                    for col in metric_cols:
                        if col not in st.session_state[k_prop].columns:
                            st.session_state[k_prop][col] = 0.0
                
                    needs_rerun = False
                    for col in metric_cols:
                        if not edited_propiedades[col].equals(st.session_state[k_prop][col]):
                            needs_rerun = True
                            break
                
                    if needs_rerun:
                        st.session_state[k_prop] = edited_propiedades
                        st.rerun()

            with st.expander("🛡️ (4) Pólizas y Seguros"):
                st.session_state[f"omit_{rut}_seguros"] = st.checkbox("Omitir sección", value=st.session_state.get(f"omit_{rut}_seguros", False), key=f"cb_omit_{rut}_seguros")
                if st.session_state[f"omit_{rut}_seguros"]:
                    st.info("⚠️ La sección de Seguros fue omitida intencionalmente.")
                else:
                    st.info("ℹ️ Seguros contratados, análisis de coberturas con IA y detalles de beneficiarios.")
        
                    with st.expander("📥 Importar desde Certificado CMF", expanded=False):
                        st.info("Sube el certificado de la CMF ('Conoce Tu Seguro') para importar automáticamente las pólizas.")
                        render_manual_button("manual_cmf_seguros.pdf", "📄 Descargar Manual CMF (Seguros)")
                        cmf_file = st.file_uploader("Subir PDF CMF", type=["pdf"], key=f"cmf_file_{rut}")
                        if cmf_file:
                            if st.button("Procesar Pólizas CMF", type="primary"):
                                with st.spinner("Extrayendo pólizas vigentes..."):
                                    from src.osint.parser_cmf_pdf import parse_cmf_insurance_pdf
                                    df_cmf, no_responden = parse_cmf_insurance_pdf(cmf_file.getvalue())
                                    if not df_cmf.empty:
                                        nuevas_polizas = []
                                        existing_polizas = st.session_state[k_poliza]['N° Póliza'].tolist() if 'N° Póliza' in st.session_state[k_poliza].columns else []
                                        for _, row in df_cmf.iterrows():
                                            if str(row['numero_poliza']) not in existing_polizas:
                                                nuevas_polizas.append({
                                                    "Aseguradora": row['compania'],
                                                    "Asegurado": row['asegurado'],
                                                    "Contratante": row['contratante'],
                                                    "Tipo": row['tipo_seguro'],
                                                    "N° Póliza": row['numero_poliza'],
                                                    "Colectivo / Individual": row['colectivo_individual'],
                                                    "Alias / Patente": "",
                                                    "Monto (UF)": 0,
                                                    "Prima": 0.0,
                                                    "Medio de Pago": "",
                                                    "Coberturas": row.get('coberturas', ''),
                                                    "Análisis IA": ""
                                                })
                            
                                        if nuevas_polizas:
                                            st.session_state[k_poliza] = pd.concat([st.session_state[k_poliza], pd.DataFrame(nuevas_polizas)], ignore_index=True)
                                            if f"editor_polizas_{rut}" in st.session_state:
                                                del st.session_state[f"editor_polizas_{rut}"]
                                            
                                            st.session_state[f"{rut}_f_seguros"] = datetime.date.today()
                                
                                        if no_responden:
                                            import datetime as dt_module
                                            alerta = f"\n🚨 CMF Alerta ({(dt_module.datetime.now()).strftime('%d-%m-%Y')}): Las siguientes compañías NO respondieron la consulta, verificar con el cliente: {', '.join(no_responden)}."
                                            if "CMF Alerta" not in st.session_state[k_nota]:
                                                st.session_state[k_nota] = (st.session_state[k_nota] + alerta).strip()
                                    
                                        st.success(f"{len(nuevas_polizas)} pólizas importadas exitosamente. Revisa la tabla y presiona 'Guardar' para confirmar.")
                                        st.rerun()
                                    else:
                                        st.warning("No se encontraron pólizas vigentes en el documento.")

                    # Botón para Análisis IA Múltiple
                    if not st.session_state[k_poliza].empty:
                        if st.button("🤖 Generar Análisis Comercial IA (Todas las pólizas)", type="primary"):
                            with st.spinner("Analizando cláusulas técnicas con IA (esto tomará unos segundos)..."):
                                from src.intelligence.insurance_analyzer import InsurancePolicyAnalyst
                                analyst = InsurancePolicyAnalyst()
                                df_copy = st.session_state[k_poliza].copy()
                    
                                for idx, row in df_copy.iterrows():
                                    cob = str(row.get("Coberturas", ""))
                                    if cob and len(cob) > 10 and not str(row.get("Análisis IA", "")).startswith("- **"):
                                        res = analyst.analyze_cmf_coberturas(str(row.get("Tipo", "")), cob)
                                        df_copy.at[idx, "Análisis IA"] = res
                    
                                st.session_state[k_poliza] = df_copy
                                st.success("¡Análisis IA completado! Revisa la columna de 'Análisis IA' para el diagnóstico.")
                                st.rerun()

                    edited_polizas = st.data_editor(
                        st.session_state[k_poliza], 
                        num_rows="dynamic", 
                        use_container_width=True, 
                        key=f"editor_polizas_{rut}",
                        column_config={
                            "Aseguradora": st.column_config.TextColumn("Aseguradora"),
                            "Asegurado": st.column_config.TextColumn("Asegurado"),
                            "Contratante": st.column_config.TextColumn("Contratante"),
                            "Tipo": st.column_config.TextColumn("Bien Asegurado (Tipo)"),
                            "N° Póliza": st.column_config.TextColumn("N° Póliza / Código"),
                            "Colectivo / Individual": st.column_config.TextColumn("Colectivo / Individual"),
                            "Alias / Patente": st.column_config.TextColumn("Alias / Patente"),
                            "Monto (UF)": st.column_config.NumberColumn(format="%d UF"),
                            "Prima": st.column_config.NumberColumn(),
                            "Medio de Pago": st.column_config.TextColumn("Medio de Pago"),
                            "Fecha Contratación": st.column_config.TextColumn("Fecha Contratación (DD/MM/YYYY)", help="Pólizas Post-04/02/2022 están afectas a impuesto a la herencia según Ley 21.420 y Circular 20 SII"),
                            "¿APV Póliza?": st.column_config.CheckboxColumn("¿APV Póliza?", help="Pólizas de APV acogidas al Art. 42 LIR (exentas de impuesto a la herencia)"),
                            "Coberturas": st.column_config.TextColumn("Coberturas (Letra Chica)", width="large"),
                            "Análisis IA": st.column_config.TextColumn("💡 Análisis IA Comercial", width="large")
                        }
                    )
        
                    st.info("💡 **Sugerencia:** Para obtener mayores detalles sobre el medio de pago, beneficiarios designados o el mandato exacto, te recomendamos visitar la 'Sucursal Virtual' de la aseguradora correspondiente.")

            with st.expander("💳 (5) Mapa de Deudas (CMF)"):
                st.session_state[f"omit_{rut}_deudas"] = st.checkbox("Omitir sección", value=st.session_state.get(f"omit_{rut}_deudas", False), key=f"cb_omit_{rut}_deudas")
                if st.session_state[f"omit_{rut}_deudas"]:
                    st.info(" La seccin de Deudas fue omitida intencionalmente.")
                else:
                    st.info("ℹ️ Consolidación de deudas del sistema financiero, cargas financieras y morosidades.")
                    with st.expander("📥 Importar Informe de Deudas CMF (CSV / Excel)", expanded=False):
                        st.info("Sube el archivo CSV o Excel del Informe de Deudas de la CMF ('Conoce tu deuda').")
                        render_manual_button("manual_cmf_deudas.pdf", "📄 Descargar Manual CMF (Deudas)")
                        cmf_csv_file = st.file_uploader("Subir Informe Deudas CMF (CSV/Excel)", type=["csv", "xls", "xlsx"], key=f"cmf_deuda_{rut}")
                        if cmf_csv_file:
                            if st.button("Procesar Deudas", type="primary"):
                                with st.spinner("Procesando deudas..."):
                                    import sys
                                    import importlib
                                    import src.osint.parser_cmf_deudas
                                    importlib.reload(src.osint.parser_cmf_deudas)
                                    from src.osint.parser_cmf_deudas import parse_cmf_deudas_csv
                                    df_deudas = parse_cmf_deudas_csv(cmf_csv_file.getvalue(), filename=cmf_csv_file.name)
                        
                                    if not df_deudas.empty:
                                        # Asegurar columnas base en k_debt si estaba vacío
                                        expected_cols = ["Institucion", "Tipo_Credito", "Monto Original", "Monto Actual", "Carga Financiera", "Otorgamiento", "Vencimiento", "Mora", "Observaciones"]
                                        if st.session_state[k_debt].empty:
                                            st.session_state[k_debt] = pd.DataFrame(columns=expected_cols)

                                        st.session_state[k_debt] = pd.concat([st.session_state[k_debt], df_deudas], ignore_index=True)
                                        # Forzar columnas correctas y limpiar basura residual
                                        valid_cols = [c for c in expected_cols if c in st.session_state[k_debt].columns]
                                        st.session_state[k_debt] = st.session_state[k_debt][valid_cols]
                                        # Eliminar filas vacías o con Institucion vacía
                                        mask = st.session_state[k_debt]["Institucion"].notna() & (st.session_state[k_debt]["Institucion"] != "") & (st.session_state[k_debt]["Institucion"] != "None")
                                        st.session_state[k_debt] = st.session_state[k_debt][mask]
                                        # Conservar observaciones previas para las deudas actualizadas
                                        subset_cols = ["Institucion", "Tipo_Credito", "Monto Original", "Otorgamiento"]
                                        st.session_state[k_debt]["Observaciones"] = st.session_state[k_debt].groupby(subset_cols)["Observaciones"].ffill()
                                        # Eliminar duplicados para evitar duplicación futura al reimportar
                                        st.session_state[k_debt].drop_duplicates(subset=subset_cols, keep='last', inplace=True)
                                        st.session_state[k_debt].reset_index(drop=True, inplace=True)
                                        st.success(f"{len(df_deudas)} deudas procesadas exitosamente.")
                                        if f"editor_deudas_{rut}" in st.session_state:
                                            del st.session_state[f"editor_deudas_{rut}"]
                                        st.session_state[f"{rut}_f_deudas"] = datetime.date.today()
                                        st.rerun()
                                    else:
                                        st.warning("No se encontraron deudas en el archivo subido.")

                    edited_deudas = st.data_editor(
                        st.session_state[k_debt],
                        num_rows="dynamic",
                        use_container_width=True,
                        key=f"editor_deudas_{rut}",
                        column_config={
                            "Institucion": st.column_config.TextColumn("Institución"),
                            "Tipo_Credito": st.column_config.TextColumn("Tipo Crédito"),
                            "Monto Original": st.column_config.NumberColumn(format="$ %,d"),
                            "Monto Actual": st.column_config.NumberColumn(format="$ %,d"),
                            "Carga Financiera": st.column_config.NumberColumn(format="$ %,d"),
                            "Mora": st.column_config.NumberColumn(format="$ %,d"),
                            "Observaciones": st.column_config.TextColumn("Observaciones / Propiedad", width="large")
                        }
                    )

            with st.expander("📈 (6) Inversiones Consolidadas"):
                st.session_state[f"omit_{rut}_inversiones"] = st.checkbox("Omitir sección", value=st.session_state.get(f"omit_{rut}_inversiones", False), key=f"cb_omit_{rut}_inversiones")
                if st.session_state[f"omit_{rut}_inversiones"]:
                    st.info("⚠️ La sección de Inversiones fue omitida intencionalmente.")
                else:
                    st.info("ℹ️ Consolidación de portafolios de inversión, AFP y otros activos.")
                    
                    with st.expander("📥 Importar Cartolas de Inversión y AFP", expanded=False):
                        st.info("Sube múltiples cartolas de AFP, Fondos Mutuos o Inversiones.")
                        inv_files = st.file_uploader("Subir archivos (PDF/Excel)", type=["pdf", "xlsx", "xls", "csv"], accept_multiple_files=True, key=f"inv_files_{rut}")
                        if inv_files:
                            if st.button("Procesar Cartolas con IA", type="primary"):
                                with st.spinner("Analizando cartolas con Inteligencia Artificial (Gemini)..."):
                                    file_bytes_list = [f.read() for f in inv_files]
                                    file_names = [f.name for f in inv_files]
                                    try:
                                        import importlib
                                        import src.osint.parser_inversiones
                                        importlib.reload(src.osint.parser_inversiones)
                                        from src.osint.parser_inversiones import parse_investment_files
                                        
                                        df_extracted = parse_investment_files(file_bytes_list, file_names)
                                        if not df_extracted.empty:
                                            st.session_state[k_inv] = pd.concat([st.session_state[k_inv], df_extracted], ignore_index=True)
                                            st.success(f"✅ Se extrajeron {len(df_extracted)} posiciones correctamente.")
                                        else:
                                            st.error("No se encontraron posiciones o hubo un error en la extracción.")
                                    except Exception as e:
                                        st.error(f"Error procesando cartolas: {e}")
                    
                    st.markdown("##### Portafolio de Inversiones")
                    edited_inv = st.data_editor(
                        st.session_state[k_inv],
                        num_rows="dynamic",
                        use_container_width=True,
                        key=f"editor_inversiones_{rut}",
                        column_config={
                            "Institucion": st.column_config.TextColumn("Institución", width="medium"),
                            "Activo": st.column_config.TextColumn(width="large"),
                            "Tipo": st.column_config.SelectboxColumn(
                                "Tipo",
                                options=["Cotización Obligatoria", "APV-A", "APV-B", "Depósito Convenido (DC-R)", "Depósito Convenido (DC-L)", "Cuenta 2", "Fondo Mutuo", "Acciones", "Depósito a Plazo", "Otro"]
                            ),
                            "Monto": st.column_config.NumberColumn("Monto Original", format="$ %,d"),
                            "Moneda": st.column_config.TextColumn(width="small"),
                            "Monto CLP": st.column_config.NumberColumn("Monto (CLP)", format="$ %,d")
                        }
                    )
                    
                    if not edited_inv.empty:
                        st.markdown("##### 📊 Distribución del Portafolio")
                        df_plot = edited_inv.copy()
                        df_plot["Monto CLP"] = pd.to_numeric(df_plot["Monto CLP"], errors='coerce').fillna(0)
                        df_plot = df_plot[df_plot["Monto CLP"] > 0]
                        
                        if not df_plot.empty:
                            col1, col2 = st.columns(2)
                            with col1:
                                fig1 = px.pie(df_plot, values="Monto CLP", names="Institucion", title="Por Institución", hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
                                fig1.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig1, use_container_width=True)
                            with col2:
                                fig2 = px.pie(df_plot, values="Monto CLP", names="Tipo", title="Por Tipo de Activo", hole=0.4, color_discrete_sequence=px.colors.sequential.Burg)
                                fig2.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig2, use_container_width=True)
                        else:
                            st.info("Ingresa montos válidos en CLP para visualizar la distribución.")
                    

            with st.expander("🚨 (7) Alertas y Pendientes"):
                st.info("ℹ️ Resumen de notificaciones importantes, fechas de reajuste de arriendo y observaciones de compliance.")
                
                # Check for omitted sections
                if st.session_state.get(f"omit_{rut}_sii"):
                    st.warning("⚠️ La sección de Perfil Tributario (SII) fue omitida intencionalmente.")
                if st.session_state.get(f"omit_{rut}_inmobiliaria"):
                    st.warning("⚠️ La sección de Cartera Inmobiliaria fue omitida intencionalmente.")
                if st.session_state.get(f"omit_{rut}_seguros"):
                    st.warning("⚠️ La sección de Pólizas y Seguros fue omitida intencionalmente.")
                if st.session_state.get(f"omit_{rut}_deudas"):
                    st.warning("⚠️ La sección Mapa de Deudas (CMF) fue omitida intencionalmente.")
                if st.session_state.get(f"omit_{rut}_inversiones"):
                    st.warning("⚠️ La sección de Inversiones Consolidadas fue omitida intencionalmente.")
                
                # Alertas de información faltante
                if missing_herederos:
                    st.warning("⚠️ **Falta información de Herederos:** Sin este dato, no se puede generar el informe detallado de *Sucesión Patrimonial*.")
                if missing_propiedades and not st.session_state.get(f"omit_{rut}_inmobiliaria"):
                    st.warning("⚠️ **Falta información de Propiedades:** No se puede ejecutar la valorización patrimonial ni el *Análisis Inmobiliario / Bienes Raíces*.")
                if missing_polizas and not st.session_state.get(f"omit_{rut}_seguros"):
                    st.info("💡 **Información de Pólizas:** Agregar las pólizas de vida habilitará el análisis de *Estrategia Tributaria Avanzada e Inembargabilidad*.")
                
                if not missing_herederos and not missing_propiedades and not missing_polizas:
                    st.success("✅ **Perfil Completo:** Tienes toda la información necesaria para los análisis avanzados.")

                f_seguros = st.session_state.get(f"{rut}_f_seguros")
                if f_seguros and not st.session_state.get(f"omit_{rut}_seguros"):
                    diff = (datetime.date.today() - f_seguros).days
                    if diff > 180:
                        st.warning("⚠️ **Información de Seguros desactualizada:** Hace más de 6 meses que no se actualizan las pólizas.")

                f_deudas = st.session_state.get(f"{rut}_f_deudas")
                if f_deudas and not st.session_state.get(f"omit_{rut}_deudas"):
                    diff = (datetime.date.today() - f_deudas).days
                    if diff > 90:
                        st.warning("⚠️ **Información de Deudas desactualizada:** Hace más de 3 meses que no se actualiza el mapa de deudas (CMF).")

                st.markdown("##### 🔔 Alertas y Reajustes de Arriendo")
                from src.osint.indicadores import get_uf_today, get_ipc_accumulated
        
                arriendos_activos = edited_propiedades[edited_propiedades["Arrendada"] == True]
                if arriendos_activos.empty:
                    st.info("No hay propiedades marcadas como arrendadas para mostrar alertas.")
                else:
                    uf_hoy = get_uf_today()
                    alertas = []
            
                    for idx, row in arriendos_activos.iterrows():
                        direccion = row.get("Dirección", "") or f"Propiedad {idx+1}"
                        monto = row.get("Monto Arriendo", 0.0)
                        moneda = row.get("Moneda Arriendo", "CLP")
                        fecha_contrato = row.get("Fecha Contrato Arriendo")
                        meses_reajuste = row.get("Meses Reajuste Arriendo", 12)
                
                        if pd.isna(monto) or pd.isna(fecha_contrato) or pd.isna(meses_reajuste):
                            continue
                    
                        fecha_dt = pd.to_datetime(fecha_contrato, errors='coerce')
                        if pd.isna(fecha_dt):
                            continue
                    
                        # Calcular fechas de reajuste
                        now = pd.Timestamp.now()
                        proximo_reajuste = fecha_dt
                        while proximo_reajuste <= now:
                            proximo_reajuste += pd.DateOffset(months=int(meses_reajuste))
                
                        ultimo_reajuste = proximo_reajuste - pd.DateOffset(months=int(meses_reajuste))
                        if ultimo_reajuste < fecha_dt:
                            ultimo_reajuste = fecha_dt
                
                        if moneda == "UF":
                            monto_clp = monto * uf_hoy
                            alertas.append(f"**{direccion}**: Contrato en UF. Valor actual: **${monto_clp:,.0f} CLP** ({monto} UF).")
                        elif moneda == "CLP":
                            # Calcular IPC desde ultimo reajuste
                            ipc_var = get_ipc_accumulated(ultimo_reajuste.strftime('%Y-%m-%d'))
                            nuevo_monto = monto * (1 + (ipc_var/100.0))
                    
                            if (proximo_reajuste - now).days <= 45:
                                st.warning(f"⚠️ **Atención:** {direccion} tiene fecha de reajuste el **{proximo_reajuste.strftime('%d-%m-%Y')}**.")
                                st.write(f"➤ *Información referencial:* La variación del IPC acumulada estrictamente **a la fecha de hoy** (desde {ultimo_reajuste.strftime('%d-%m-%Y')}) es de **{ipc_var:.1f}%**.")
                                st.write("*(Recuerda que el monto exacto a cobrar dependerá de la inflación oficial publicada al cierre del mes anterior a la fecha de cobro).*")
                                st.markdown("---")
                            else:
                                alertas.append(f"**{direccion}**: Próximo reajuste programado para el **{proximo_reajuste.strftime('%d-%m-%Y')}**.")
            
                    for a in alertas:
                        st.write(f"👉 {a}")

                st.markdown("##### 🚨 Panel de Alertas y Observaciones del Sistema")
                st.session_state[k_alerta] = st.text_area("Agrega advertencias, falta de información, o asuntos de compliance:", value=st.session_state[k_alerta], height=100)

            # 🔗 INFO DINÁMICA DE ENTIDADES RELACIONADAS (NUEVO)
            if prospect_temp:
                db_temp = SessionLocal()
                p_full = db_temp.query(Prospect).filter_by(id=prospect_temp.id).first()
                if p_full:
                    related_prospects = p_full.get_related_prospects(db_temp)
                    if related_prospects:
                        st.markdown("---")
                        with st.expander("🔗 (8) Información de Entidades Relacionadas"):
                            st.info("ℹ️ Permite escuchar los audios y leer las notas de los familiares o socios comerciales sin tener que salir de la página del cliente actual, dando una vista panorámica del grupo familiar o económico.")
                            st.caption("Los siguientes datos provienen de empresas o socios vinculados a este perfil.")
                            for rp in related_prospects:
                                if rp.profile:
                                    has_notes = bool(rp.profile.notas_neuroventas)
                                    has_audio = bool(rp.profile.audio_path and os.path.exists(rp.profile.audio_path))
                            
                                    if has_notes or has_audio:
                                        with st.expander(f"📌 {rp.nombre} (RUT: {rp.rut})"):
                                            if has_notes:
                                                st.markdown(f"**Notas:** {rp.profile.notas_neuroventas}")
                                            if has_audio:
                                                st.markdown("**Audio:**")
                                                st.audio(rp.profile.audio_path)
                    db_temp.close()
            
            with st.expander("📄 (9) Generación e Ingesta de Informes 360° y Formularios KYC", expanded=True):
                st.info("ℹ️ Creación automatizada de Informes Ejecutivo 360°, Planificación Sucesoria y Manuales KYC para el cliente.")
                
                # 1. Informe Ejecutivo Total 360°
                st.markdown("#### 📜 Informe Ejecutivo Consolidated 360° & Planificación Sucesoria")
                st.caption("Contiene el mapa integral de activos (propiedades, inversiones, seguros, deudas CMF), cálculo de herencia, exenciones (Cuenta 2 Art. 72, Ley 21.420), extinción por desgravamen y matriz legal por artículo.")
                
                if pdf_top_bytes:
                    st.download_button(
                        label="📜 Descargar Informe Executive Total 360° (PDF)",
                        data=pdf_top_bytes,
                        file_name=f"Reporte_Consolidado_360_{rut}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                        key=f"dl_sec9_pdf_{rut}"
                    )
                else:
                    st.warning("⚠️ No se pudo generar el informe PDF para este cliente.")

                st.markdown("---")
                st.markdown("#### 📋 Manual de Recopilación y Formularios KYC")
                st.markdown("Envíale un formulario estructurado al cliente solicitando la información faltante específica.")
        
                c_form1, c_form2 = st.columns(2)
                with c_form1:
                    from src.utils.pdf_generator import generate_kyc_manual
                    current_name = st.session_state.get("current_client_name", str(rut))
                    try:
                        pdf_bytes = generate_kyc_manual(current_name)
                    except Exception as e:
                        pdf_bytes = None

                    if pdf_bytes:
                        st.download_button(
                            label="📥 Descargar Manual de Recopilación (PDF)",
                            data=pdf_bytes,
                            file_name=f"Manual_KYC_{rut}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"dl_kyc_pdf_{rut}"
                        )
                    else:
                        st.button("📥 Manual no disponible", disabled=True, use_container_width=True)
            
                    # Generar Excel solo con lo que falta
                    req_fields = []
                    req_reasons = []
                    if missing_herederos:
                        req_fields.append("Detalle de Herederos (Parentesco, Nombre, Fecha de Nacimiento)")
                        req_reasons.append("Requerido para la planificación de sucesión y distribución legal eficiente.")
                    if missing_propiedades:
                        req_fields.append("Detalle de Propiedades (ROL, Valor, Deuda Hipotecaria vigente)")
                        req_reasons.append("Necesario para calcular patrimonio neto consolidado y planificar liquidez sucesoria.")
                    if missing_polizas:
                        req_fields.append("Pólizas de Vida o APV (Aseguradora, Montos)")
                        req_reasons.append("Para auditar estructuras inembargables y maximizar beneficios tributarios (Art. 57 LIR, etc).")
                
                    if not req_fields:
                        st.info("El perfil está completo. No se requiere solicitar más datos por ahora.")
                    else:
                        df_req = pd.DataFrame({
                            "Dato Requerido por Altus AI": req_fields,
                            "¿Por qué lo necesitamos?": req_reasons,
                            "Respuesta del Cliente": [""] * len(req_fields)
                        })
                
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_req.to_excel(writer, index=False, sheet_name='Formulario_KYC')
                        val = output.getvalue()
                
                        st.download_button(
                            label="💾 Descargar Excel KYC para Cliente",
                            data=val,
                            file_name=f"Altus_KYC_{st.session_state.current_client_name.replace(' ', '_')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                with c_form2:
                    uploaded_form = st.file_uploader("📤 Subir Excel/PDF completado por el cliente", type=["xlsx", "xls", "pdf"])
                    if uploaded_form:
                        if st.button("Procesar Archivo y Actualizar Base de Datos", use_container_width=True):
                            with st.spinner("El Agente IA está extrayendo los datos de las tablas del documento..."):
                                # Simulación de extracción estructurada
                                if missing_herederos:
                                    st.session_state[k_hered] = pd.DataFrame([{"Relación": "Hijo/a", "Nombre": "Extraído por IA", "Fecha de Nacimiento": datetime.date(1995, 1, 1), "% Asignación": 50}])
                                if missing_propiedades:
                                    st.session_state[k_prop] = pd.DataFrame([{"Nombre/Alias": "Casa Extraída", "ROL": "123-4", "Dirección": "Las Condes", "Avalúo (CLP)": 150000000, "Valor Com. (UF)": 10000, "Deuda Hipotecaria": True, "Dividendo": 40, "Cuota Actual": 12, "Total Cuotas": 240, "Arrendada": False}])
                        
            st.markdown("---")
            col_save1, col_save2 = st.columns([0.5, 0.5])
            with col_save2:
                if pdf_top_bytes:
                    st.download_button(
                        label="📜 Descargar Reporte Executive Total 360° (PDF)",
                        data=pdf_top_bytes,
                        file_name=f"Reporte_Consolidado_360_{rut}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"dl_foot_pdf_{rut}"
                    )
            
            with col_save1:
                btn_guardar_click = st.button("💾 Guardar y Actualizar Perfil Integral", type="primary", use_container_width=True)

            if btn_guardar_click:
                # Sincronizamos la base de datos con las ediciones finales
                if "edited_herederos" in locals():
                    st.session_state[k_hered] = edited_herederos
                if "edited_propiedades" in locals():
                    st.session_state[k_prop] = edited_propiedades
                if "edited_polizas" in locals():
                    st.session_state[k_poliza] = edited_polizas
                if "edited_socios" in locals():
                    st.session_state[k_socios] = edited_socios
                if "edited_repres" in locals():
                    st.session_state[k_repres] = edited_repres
                if "edited_inv" in locals():
                    st.session_state[k_inv] = edited_inv
                if "edited_deudas" in locals():
                    st.session_state[k_debt] = edited_deudas
            
                # Obtener el documento legal actual si existe en el uploader
                uploaded_doc_legal = st.session_state.get(f"legal_{rut}")
            
                # --- PERSISTENCIA EN BASE DE DATOS REAL ---
                try:
                    db = SessionLocal()
                    clean_rut_save = rut.replace(".", "").replace("-", "").strip()
                    prospect = db.query(Prospect).filter(Prospect.rut.contains(clean_rut_save) | (Prospect.rut == rut)).first()
                
                    if prospect:
                        # 1. Perfil Base y Datos Personales
                        if not prospect.profile:
                            nuevo_perfil = ClientProfile(prospect_id=prospect.id)
                            db.add(nuevo_perfil)
                            db.flush()
                            prospect.profile = nuevo_perfil
                            
                        # Actualizar datos de Prospect
                        prospect.nombre = st.session_state.get(f"{rut}_nombre", prospect.nombre)
                        prospect.telefono = st.session_state.get(f"{rut}_telefono", prospect.telefono)
                        prospect.email = st.session_state.get(f"{rut}_email", prospect.email)
                        
                        prospect.profile.cantidad_herederos = len(st.session_state[k_hered]) if k_hered in st.session_state and not st.session_state.get(k_na) else 0
                        prospect.profile.notas_neuroventas = st.session_state.get(k_nota)
                        prospect.profile.alertas_sistema = st.session_state.get(k_alerta)
                        prospect.profile.tipo_persona = st.session_state.get(k_tipo_persona)
                        prospect.profile.nivel_riesgo = st.session_state.get(f"{rut}_perfil", prospect.profile.nivel_riesgo)
                        prospect.profile.objetivo_inversion = st.session_state.get(f"{rut}_objetivo", prospect.profile.objetivo_inversion)
                        prospect.estado_previsional = st.session_state.get(f"{rut}_estado_prev", getattr(prospect, "estado_previsional", ""))
                        prospect.periodo_garantizado_rv_meses = int(st.session_state.get(f"{rut}_rv_anios", 0) or 0) * 12
                        
                        omit_list = []
                        if st.session_state.get(f"omit_{rut}_sii"): omit_list.append("sii")
                        if st.session_state.get(f"omit_{rut}_inmobiliaria"): omit_list.append("inmobiliaria")
                        if st.session_state.get(f"omit_{rut}_seguros"): omit_list.append("seguros")
                        if st.session_state.get(f"omit_{rut}_deudas"): omit_list.append("deudas")
                        if st.session_state.get(f"omit_{rut}_inversiones"): omit_list.append("inversiones")
                        prospect.profile.secciones_omitidas = json.dumps(omit_list)
                        
                        prospect.profile.fecha_ultima_act_seguros = st.session_state.get(f"{rut}_f_seguros")
                        prospect.profile.fecha_ultima_act_deudas = st.session_state.get(f"{rut}_f_deudas")
                    
                        # Guardar Audio si existe uno nuevo
                        audio_dir = os.path.join("assets", "audio")
                        os.makedirs(audio_dir, exist_ok=True)
                        audio_to_save = None
                        if 'recorded_audio_dp' in locals() and recorded_audio_dp:
                            audio_to_save = recorded_audio_dp
                        elif 'uploaded_audio_dp' in locals() and uploaded_audio_dp:
                            audio_to_save = uploaded_audio_dp
                            
                        if audio_to_save:
                            ext = audio_to_save.name.split('.')[-1] if hasattr(audio_to_save, 'name') and '.' in audio_to_save.name else "wav"
                            safe_rut = str(rut).replace(".", "").replace("-", "_")
                            audio_filename = f"audio_{safe_rut}.{ext}"
                            audio_filepath = os.path.join(audio_dir, audio_filename)
                            with open(audio_filepath, "wb") as f:
                                f.write(audio_to_save.getbuffer())
                            prospect.profile.audio_path = audio_filepath
                    
                        # 2. Herederos (Sincronización total y persistencia)
                        df_hered_to_save = None
                        if "edited_herederos" in locals() and isinstance(edited_herederos, pd.DataFrame):
                            df_hered_to_save = edited_herederos
                            st.session_state[k_hered] = edited_herederos
                        elif k_hered in st.session_state and isinstance(st.session_state[k_hered], pd.DataFrame):
                            df_hered_to_save = st.session_state[k_hered]

                        if df_hered_to_save is not None:
                            db.query(ClientHeir).filter(ClientHeir.prospect_id == prospect.id).delete()
                            if not st.session_state.get(k_na, False):
                                for _, row in df_hered_to_save.iterrows():
                                    fecha_nac = None
                                    if pd.notnull(row.get("Fecha de Nacimiento")):
                                        fecha_nac = row["Fecha de Nacimiento"]
                                
                                    nuevo_heredero = ClientHeir(
                                        prospect_id=prospect.id,
                                        rut=str(row.get("RUT", "")),
                                        relacion=str(row.get("Relación", "")),
                                        nombre=str(row.get("Nombre", "")),
                                        fecha_nacimiento=fecha_nac,
                                        porcentaje_asignacion=float(row.get("% Asignación", 0.0) or 0.0),
                                        es_estudiante=bool(row.get("¿Estudiante (18-24 años)?", False))
                                    )
                                    db.add(nuevo_heredero)
                            
                        # 3. Propiedades
                        if "edited_propiedades" in locals():
                            db.query(ClientProperty).filter(ClientProperty.prospect_id == prospect.id).delete()
                            for _, row in edited_propiedades.iterrows():
                                nueva_prop = ClientProperty(
                                    prospect_id=prospect.id,
                                    direccion=row.get("Dirección", ""),
                                    comuna=row.get("Comuna", ""),
                                    destino=row.get("Destino", ""),
                                    fojas=str(row.get("Fojas", "")),
                                    numero=str(row.get("Número", "")),
                                    ano=int(float(str(row.get("Año")).strip())) if pd.notna(row.get("Año")) and str(row.get("Año")).strip() not in ["", "None", "nan"] else None,
                                    porcentaje_derecho=float(row.get("% de Derecho", 100.0) or 100.0),
                                    avaluo_fiscal=float(row.get("Avalúo Fiscal (CLP)", 0.0) or 0.0),
                                    rol=row.get("ROL", ""),
                                    valor_comercial_estimado=float(row.get("Valor Com. (UF)", 0.0) or 0.0),
                                    deuda_hipotecaria=float(1) if row.get("Deuda Hipotecaria") else 0.0,
                                    hipoteca_institucion=row.get("Institución Hipoteca", ""),
                                    hipoteca_monto_inicial=float(row.get("Monto Inicial (UF)")) if pd.notna(row.get("Monto Inicial (UF)")) else 0.0,
                                    hipoteca_saldo_actual=float(row.get("Saldo Actual (UF)")) if pd.notna(row.get("Saldo Actual (UF)")) else 0.0,
                                    hipoteca_fecha_escritura=str(row.get("Fecha Escritura", "")) if pd.notna(row.get("Fecha Escritura")) else "",
                                    hipoteca_valor_tasacion=float(row.get("Tasación (UF)")) if pd.notna(row.get("Tasación (UF)")) else 0.0,
                                    hipoteca_monto_asegurado=float(row.get("Monto Asegurado (UF)")) if pd.notna(row.get("Monto Asegurado (UF)")) else 0.0,
                                    hipoteca_tasa_interes=float(row.get("Tasa Interés (%)")) if pd.notna(row.get("Tasa Interés (%)")) else 0.0,
                                    hipoteca_tipo_tasa=row.get("Tipo Tasa", ""),
                                    hipoteca_cuota_actual=int(row.get("Cuota Actual", 0) or 0),
                                    hipoteca_total_cuotas=int(row.get("Total Cuotas", 0) or 0),
                                    hipoteca_fecha_ultima_actualizacion=row.get("__fecha_act_cuota"),
                                    dividendo_mensual=float(row.get("Dividendo")) if pd.notna(row.get("Dividendo")) else 0.0,
                                    arriendo_mensual=float(row.get("Monto Arriendo")) if pd.notna(row.get("Monto Arriendo")) else 0.0,
                                    arriendo_moneda=row.get("Moneda Arriendo", "CLP"),
                                    arriendo_fecha_contrato=str(row.get("Fecha Contrato Arriendo", "")) if pd.notna(row.get("Fecha Contrato Arriendo")) else "",
                                    arriendo_periodo_reajuste=int(row.get("Meses Reajuste Arriendo", 12)) if pd.notna(row.get("Meses Reajuste Arriendo")) else None,
                                    contribuciones_anuales=float(row.get("Contribuciones Trim.", 0.0) or 0.0) * 4,
                                    gastos_comunes=float(row.get("Gastos Comunes Mensuales", 0.0) or 0.0),
                                    gastos_mantencion_anual=float(row.get("Mantención Anual (CLP)", 0.0) or 0.0),
                                    plusvalia_esperada_anual=float(row.get("Plusvalía Esperada (%)", 0.0) or 0.0),
                                    observaciones=row.get("Nombre/Alias", "")
                                )
                                db.add(nueva_prop)
                        
                        # 4. Pólizas (Persistencia garantizada)
                        df_polizas_to_save = None
                        if "edited_polizas" in locals() and isinstance(edited_polizas, pd.DataFrame):
                            df_polizas_to_save = edited_polizas
                            st.session_state[k_poliza] = edited_polizas
                        elif k_poliza in st.session_state and isinstance(st.session_state[k_poliza], pd.DataFrame):
                            df_polizas_to_save = st.session_state[k_poliza]

                        if df_polizas_to_save is not None:
                            db.query(ClientInsurance).filter(ClientInsurance.prospect_id == prospect.id).delete()
                            for _, row in df_polizas_to_save.iterrows():
                                nueva_poliza = ClientInsurance(
                                    prospect_id=prospect.id,
                                    compania=str(row.get("Aseguradora", "")),
                                    asegurado=str(row.get("Asegurado", "")),
                                    contratante=str(row.get("Contratante", "")),
                                    tipo_seguro=str(row.get("Tipo", "")),
                                    numero_poliza=str(row.get("N° Póliza", "")),
                                    colectivo_individual=str(row.get("Colectivo / Individual", "")),
                                    alias_patente=str(row.get("Alias / Patente", "")),
                                    capital_asegurado=float(row.get("Monto (UF)", 0.0) or 0.0),
                                    prima_mensual=float(row.get("Prima", 0.0) or 0.0),
                                    medio_pago=str(row.get("Medio de Pago", "")),
                                    fecha_contratacion=str(row.get("Fecha Contratación", "")),
                                    es_apv_poliza=bool(row.get("¿APV Póliza?", False)),
                                    coberturas=str(row.get("Coberturas", "")),
                                    analisis_ia=str(row.get("Análisis IA", ""))
                                )
                                db.add(nueva_poliza)
                        
                        # 5. Deudas (Persistencia garantizada)
                        df_deudas_to_save = None
                        if "edited_deudas" in locals() and isinstance(edited_deudas, pd.DataFrame):
                            df_deudas_to_save = edited_deudas
                            st.session_state[k_debt] = edited_deudas
                        elif k_debt in st.session_state and isinstance(st.session_state[k_debt], pd.DataFrame):
                            df_deudas_to_save = st.session_state[k_debt]

                        if df_deudas_to_save is not None:
                            db.query(ClientDebt).filter(ClientDebt.prospect_id == prospect.id).delete()
                            for _, row in df_deudas_to_save.iterrows():
                                inst_val = str(row.get("Institucion", "")).strip() if pd.notna(row.get("Institucion")) else ""
                                if not inst_val or inst_val in ["None", "nan", ""]:
                                    continue

                                def safe_float(val):
                                    if pd.isna(val) or str(val).strip().lower() in ["none", "nan", ""]:
                                        return 0.0
                                    try:
                                        return float(val)
                                    except:
                                        return 0.0
                                        
                                kwargs = {
                                    "prospect_id": prospect.id,
                                    "institucion": inst_val,
                                    "tipo_credito": str(row.get("Tipo_Credito", "")) if pd.notna(row.get("Tipo_Credito")) and str(row.get("Tipo_Credito")) != "None" else "",
                                    "monto_original": safe_float(row.get("Monto Original")),
                                    "monto_actual": safe_float(row.get("Monto Actual")),
                                    "carga_financiera": safe_float(row.get("Carga Financiera")),
                                    "fecha_otorgamiento": str(row.get("Otorgamiento", "")) if pd.notna(row.get("Otorgamiento")) and str(row.get("Otorgamiento")) not in ["nan", "None"] else "",
                                    "fecha_vencimiento": str(row.get("Vencimiento", "")) if pd.notna(row.get("Vencimiento")) and str(row.get("Vencimiento")) not in ["nan", "None"] else "",
                                    "monto_mora": safe_float(row.get("Mora"))
                                }
                                nueva_deuda = ClientDebt(**kwargs)
                                setattr(nueva_deuda, "observaciones", str(row.get("Observaciones", "")) if pd.notna(row.get("Observaciones")) and str(row.get("Observaciones")) != "None" else "")
                                db.add(nueva_deuda)
                        
                        # 6. Sociedades
                        if "edited_sociedades" in locals():
                            st.session_state[k_comp] = edited_sociedades
                            db.query(ClientCompany).filter(ClientCompany.prospect_id == prospect.id).delete()
                            for _, row in edited_sociedades.iterrows():
                                try:
                                    cap_str = str(row.get("% Capital", "0")).replace("%", "").replace(",", ".").strip()
                                    cap = float(cap_str) if cap_str else 0.0
                                except:
                                    cap = 0.0
                                try:
                                    ut_str = str(row.get("% Utilidades", "0")).replace("%", "").replace(",", ".").strip()
                                    ut = float(ut_str) if ut_str else 0.0
                                except:
                                    ut = 0.0
                                    
                                nueva_sociedad = ClientCompany(
                                    prospect_id=prospect.id,
                                    rut_empresa=str(row.get("RUT Empresa", "")),
                                    razon_social=str(row.get("Razón Social", "")),
                                    fecha_incorporacion=str(row.get("Incorporación", "")),
                                    porcentaje_capital=cap,
                                    porcentaje_utilidades=ut
                                )
                                db.add(nueva_sociedad)
                        # 7. Inversiones (Persistencia garantizada)
                        df_inv_to_save = None
                        if "edited_inv" in locals() and isinstance(edited_inv, pd.DataFrame):
                            df_inv_to_save = edited_inv
                            st.session_state[k_inv] = edited_inv
                        elif k_inv in st.session_state and isinstance(st.session_state[k_inv], pd.DataFrame):
                            df_inv_to_save = st.session_state[k_inv]

                        if df_inv_to_save is not None:
                            db.query(ClientPortfolio).filter(ClientPortfolio.prospect_id == prospect.id).delete()
                            for _, row in df_inv_to_save.iterrows():
                                inst_name = str(row.get("Institucion", "")).strip() if pd.notna(row.get("Institucion")) else ""
                                if not inst_name or inst_name in ["None", "nan", ""]:
                                    continue
                                def safe_float(val):
                                    try: return float(val) if pd.notna(val) else 0.0
                                    except: return 0.0
                                kwargs = {
                                    "prospect_id": prospect.id,
                                    "institucion": inst_name,
                                    "activo": str(row.get("Activo", "")),
                                    "tipo_activo": str(row.get("Tipo", "")),
                                    "monto_original": safe_float(row.get("Monto")),
                                    "moneda_original": str(row.get("Moneda", "CLP")),
                                    "monto_clp": safe_float(row.get("Monto CLP"))
                                }
                                db.add(ClientPortfolio(**kwargs))


                        # 7. Datos de Persona Jurídica (Socios y Representantes)
                        if st.session_state.get(k_tipo_persona) == "PJ":
                        
                            prospect.profile.fecha_constitucion = st.session_state[k_fecha_const] if pd.notna(st.session_state[k_fecha_const]) else None
                            prospect.profile.notaria_constitucion = st.session_state[k_notaria]
                            prospect.profile.repertorio_constitucion = st.session_state[k_repertorio]
                            prospect.profile.fecha_ultima_vigencia = st.session_state[k_fecha_vig] if pd.notna(st.session_state[k_fecha_vig]) else None
                        
                            if 'uploaded_doc_legal' in locals() and uploaded_doc_legal:
                                docs_dir = os.path.join("assets", "docs")
                                os.makedirs(docs_dir, exist_ok=True)
                                safe_rut = str(rut).replace(".", "").replace("-", "_")
                                doc_filepaths = []
                                
                                for idx, doc in enumerate(uploaded_doc_legal):
                                    ext = doc.name.split('.')[-1] if hasattr(doc, 'name') and '.' in doc.name else "pdf"
                                    doc_filename = f"legal_{safe_rut}_{idx}.{ext}"
                                    doc_filepath = os.path.join(docs_dir, doc_filename)
                                    with open(doc_filepath, "wb") as f:
                                        f.write(doc.getbuffer())
                                    doc_filepaths.append(doc_filepath)
                                    
                                combined_paths = ";".join(doc_filepaths)
                                prospect.profile.documentos_legales_path = combined_paths
                                st.session_state[k_doc_legal] = combined_paths
                        
                            if "edited_socios" in locals():
                                db.query(CompanyShareholder).filter(CompanyShareholder.prospect_id == prospect.id).delete()
                                for _, row in edited_socios.iterrows():
                                    if pd.notna(row.get("Nombre")):
                                        nuevo_socio = CompanyShareholder(
                                            prospect_id=prospect.id,
                                            rut=row.get("RUT"),
                                            nombre=row.get("Nombre"),
                                            porcentaje_participacion=row.get("% Participación") if pd.notna(row.get("% Participación")) else None,
                                            capital_aportado=row.get("Capital Aportado") if pd.notna(row.get("Capital Aportado")) else None
                                        )
                                        db.add(nuevo_socio)
                        
                            if "edited_repres" in locals():
                                db.query(CompanyRepresentative).filter(CompanyRepresentative.prospect_id == prospect.id).delete()
                                for _, row in edited_repres.iterrows():
                                    if pd.notna(row.get("Nombre")):
                                        nuevo_rep = CompanyRepresentative(
                                            prospect_id=prospect.id,
                                            rut=str(row.get("RUT", "")),
                                            nombre=str(row.get("Nombre", "")),
                                            poderes_restricciones=str(row.get("Poderes y Restricciones", ""))
                                        )
                                        db.add(nuevo_rep)

                        db.commit()
                        st.success("¡Perfil integral guardado exitosamente en la base de datos permanente!")
                except Exception as e:
                    st.error(f"Error guardando en base de datos: {e}")
                finally:
                    if 'db' in locals():
                        db.close()
            
                st.rerun()
            
            st.markdown("---")
