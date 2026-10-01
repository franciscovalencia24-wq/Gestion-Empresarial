import streamlit as st
import pandas as pd
from src.database.connection import SessionLocal
from src.database.models import OsintLead, Prospect
from src.osint.radar_legal import process_folder
import os

def render_radar_legal():
    st.title("⚖️ Radar Legal y Notarial (OSINT)")
    st.markdown("Extrae automáticamente oportunidades de liquidez (Leads) desde documentos legales, notariales y judiciales usando Inteligencia Artificial.")
    
    tab_scan, tab_leads = st.tabs(["1. Escanear Carpeta Local", "2. Gestión de Leads Detectados"])
    
    with tab_scan:
        st.subheader("Configuración de Ingesta")
        st.info("Asegúrate de tener instalada la aplicación de Google Drive en tu PC y que la carpeta esté sincronizada localmente.")
        
        default_path = os.path.join(os.path.expanduser("~"), "Google Drive", "CARLOS MEZA")
        folder_path = st.text_input("Ruta de la carpeta a analizar", value=default_path)
        
        if st.button("🚀 Iniciar Escaneo Profundo con IA", type="primary"):
            if os.path.exists(folder_path):
                with st.spinner("Leyendo documentos y enviando a Gemini para extracción (puede tomar varios minutos)..."):
                    docs_count, leads_count = process_folder(folder_path)
                st.success(f"✔️ Análisis completado. Documentos procesados: {docs_count}. **NUEVAS** oportunidades encontradas: {leads_count} (se omitieron las que ya estaban en base de datos).")
                st.balloons()
            else:
                st.error("❌ La ruta no existe. Por favor verifica que la carpeta de Google Drive esté accesible en ese directorio.")

    with tab_leads:
        st.subheader("Oportunidades de Inversión (Leads)")
        
        db = SessionLocal()
        
        # Filtros de búsqueda rápida
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_term = st.text_input("🔍 Buscar por Nombre, RUT o Motivo:", "")
        with col_s2:
            monto_minimo = st.number_input("💰 Filtrar Monto Mínimo (CLP):", min_value=0, value=0, step=50000000)
            
        query = db.query(OsintLead).filter(OsintLead.estado == "Pendiente")
        if search_term:
            query = query.filter(
                OsintLead.nombre_persona_empresa.ilike(f"%{search_term}%") | 
                OsintLead.rut.ilike(f"%{search_term}%") | 
                OsintLead.motivo.ilike(f"%{search_term}%")
            )
        if monto_minimo > 0:
            query = query.filter(OsintLead.monto >= monto_minimo)
            
        leads = query.order_by(OsintLead.monto.desc()).all()
        
        if not leads:
            st.info("No hay leads pendientes en este momento o que coincidan con la búsqueda.")
        else:
            # Métricas rápidas
            total_monto = sum(l.monto for l in leads if l.monto)
            c1, c2, c3 = st.columns(3)
            c1.metric("Leads Encontrados", len(leads))
            c2.metric("Monto Total Identificado", f"$ {total_monto:,.0f}".replace(",", "."))
            c3.metric("Última Detección", leads[0].creado_el.strftime("%Y-%m-%d %H:%M") if leads[0].creado_el else "N/A")
            
            import urllib.parse
            raw_data = []
            for l in leads:
                # Generar enlace de búsqueda inteligente en LinkedIn
                nombre_clean = str(l.nombre_persona_empresa).replace('S.A.', '').replace('SPA', '').replace('LIMITADA', '').strip()
                nombre_enc = urllib.parse.quote(f'site:linkedin.com/in "{nombre_clean}"')
                linkedin_url = f"https://www.google.com/search?q={nombre_enc}"
                
                raw_data.append({
                    "ID_Original": l.id,
                    "Fecha Evento": l.fecha_documento if l.fecha_documento else "N/D",
                    "Nombre": l.nombre_persona_empresa,
                    "RUT": str(l.rut).strip() if l.rut else "",
                    "Monto": l.monto if l.monto else 0.0,
                    "Motivo": str(l.motivo) if l.motivo else "",
                    "Certeza": l.nivel_certeza,
                    "Archivo Origen": os.path.basename(l.archivo_origen) if l.archivo_origen else "N/D",
                    "OSINT LinkedIn": linkedin_url
                })
                
            df_raw = pd.DataFrame(raw_data)
            
            # Preparar Vista Detalle
            df_detalle = df_raw.copy()
            df_detalle["Monto (CLP)"] = df_detalle["Monto"].apply(lambda x: f"$ {x:,.0f}".replace(",", "."))
            df_detalle = df_detalle.drop(columns=["Monto"])
            df_detalle = df_detalle.rename(columns={"ID_Original": "ID"})
            
            # Preparar Vista Consolidada
            df_raw["GroupKey"] = df_raw.apply(lambda row: row["RUT"] if row["RUT"] else row["Nombre"], axis=1)
            
            df_cons = df_raw.groupby("GroupKey").agg(
                Nombre=("Nombre", "first"),
                RUT=("RUT", "first"),
                Monto_Total=("Monto", "sum"),
                Cantidad_Eventos=("Monto", "count"),
                Ultimo_Evento=("Fecha Evento", lambda x: sorted([d for d in x if d != "N/D"])[-1] if [d for d in x if d != "N/D"] else "N/D"),
                Motivos=("Motivo", lambda x: " | ".join(set([m for m in x if m]))),
                ID=("ID_Original", "first"),
                OSINT_LinkedIn=("OSINT LinkedIn", "first")
            ).reset_index(drop=True)
            
            df_cons = df_cons.sort_values(by="Monto_Total", ascending=False)
            df_cons["Monto Total (CLP)"] = df_cons["Monto_Total"].apply(lambda x: f"$ {x:,.0f}".replace(",", "."))
            
            df_consolidado = df_cons[["ID", "Nombre", "RUT", "Monto Total (CLP)", "Cantidad_Eventos", "Ultimo_Evento", "Motivos", "OSINT_LinkedIn"]]
            df_consolidado = df_consolidado.rename(columns={"Cantidad_Eventos": "Cant. Eventos", "Ultimo_Evento": "Último Evento", "OSINT_LinkedIn": "OSINT LinkedIn"})

            tab_cons, tab_det = st.tabs(["📊 Consolidado por Persona", "📄 Detalle por Documento"])
            
            with tab_cons:
                csv_cons = df_consolidado.to_csv(index=False, sep=";").encode('utf-8-sig')
                col_c1, col_c2 = st.columns([3, 1])
                with col_c2:
                    st.download_button("📥 Descargar a Excel (CSV)", data=csv_cons, file_name="leads_consolidados.csv", mime="text/csv", width="stretch", key="btn_cons")
                st.dataframe(df_consolidado, width="stretch", hide_index=True, column_config={"OSINT LinkedIn": st.column_config.LinkColumn("Búsqueda LinkedIn", display_text="🔗 Buscar Perfil")})
                
            with tab_det:
                csv_det = df_detalle.to_csv(index=False, sep=";").encode('utf-8-sig')
                col_d1, col_d2 = st.columns([3, 1])
                with col_d2:
                    st.download_button("📥 Descargar a Excel (CSV)", data=csv_det, file_name="leads_detalle.csv", mime="text/csv", width="stretch", key="btn_det")
                st.dataframe(df_detalle, width="stretch", hide_index=True, column_config={"OSINT LinkedIn": st.column_config.LinkColumn("Búsqueda LinkedIn", display_text="🔗 Buscar Perfil")})

            st.markdown("---")
            st.markdown("### Promover a Prospecto")
            col_id, col_btn = st.columns([2, 1])
            with col_id:
                selected_id = st.selectbox("Selecciona el ID del Lead que deseas promover:", df_consolidado["ID"].tolist())
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🎯 Convertir a Prospecto", width="stretch"):
                    lead_to_promote = db.query(OsintLead).filter_by(id=selected_id).first()
                    if lead_to_promote:
                        # Check if RUT already exists to avoid duplicates
                        rut_clean = lead_to_promote.rut.replace(".", "").replace("-", "") if lead_to_promote.rut else ""
                        existing_prospect = db.query(Prospect).filter(Prospect.rut.contains(rut_clean) | (Prospect.rut == lead_to_promote.rut)).first()
                        
                        if existing_prospect and rut_clean != "":
                            st.warning(f"El RUT {lead_to_promote.rut} ya existe en tu base de datos.")
                        else:
                            # Create new prospect
                            new_prospect = Prospect(
                                nombre=lead_to_promote.nombre_persona_empresa,
                                rut=lead_to_promote.rut if lead_to_promote.rut else "SIN-RUT",
                                estado="Lead OSINT",
                                ultima_interaccion=lead_to_promote.fecha_documento
                            )
                            db.add(new_prospect)
                            
                            # Mark lead as converted
                            lead_to_promote.estado = "Convertido"
                            db.commit()
                            
                            st.success(f"¡{lead_to_promote.nombre_persona_empresa} ha sido añadido a tu Gestión de Clientes!")
                            st.rerun()

        db.close()
