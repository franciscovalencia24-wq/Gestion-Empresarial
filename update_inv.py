import sys

def main():
    try:
        with open('src/web/client_management_ui.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. k_inv
        target1 = "k_repres = f\"df_repres_{rut}\""
        replace1 = target1 + "\n            k_inv = f\"df_inversiones_{rut}\""
        content = content.replace(target1, replace1)
        
        # 2. df_inv init empty
        target2 = "df_repres = pd.DataFrame(columns=[\"RUT\", \"Nombre\", \"Poderes y Restricciones\"])"
        replace2 = target2 + "\n                df_inv = pd.DataFrame(columns=[\"Institución\", \"Activo\", \"Tipo\", \"Monto\", \"Moneda\", \"Monto (CLP)\"])"
        content = content.replace(target2, replace2)
        
        # 3. df_inv init full
        target3 = "if prospect.company_shareholders:"
        replace3 = "df_inv = pd.DataFrame([{\n                        \"Institución\": i.institucion,\n                        \"Activo\": i.activo,\n                        \"Tipo\": i.tipo_activo,\n                        \"Monto\": i.monto_original,\n                        \"Moneda\": i.moneda_original,\n                        \"Monto (CLP)\": i.monto_clp\n                    } for i in prospect.portfolios])\n                    if df_inv.empty:\n                        df_inv = pd.DataFrame(columns=[\"Institución\", \"Activo\", \"Tipo\", \"Monto\", \"Moneda\", \"Monto (CLP)\"])\n\n                    " + target3
        content = content.replace(target3, replace3)
        
        # 4. Save to session state
        target4 = "st.session_state[k_repres] = df_repres"
        replace4 = target4 + "\n                st.session_state[k_inv] = df_inv"
        content = content.replace(target4, replace4)
        
        # 5. UI Section 6
        target5 = "with st.expander(\"📈 (6) Inversiones Consolidadas\"):\n                st.session_state[f\"omit_{rut}_inversiones\"] = st.checkbox(\"Omitir sección\", value=st.session_state.get(f\"omit_{rut}_inversiones\", False), key=f\"cb_omit_{rut}_inversiones\")\n                if st.session_state[f\"omit_{rut}_inversiones\"]:\n                    st.info(\"⚠️ La sección de Inversiones fue omitida intencionalmente.\")\n                else:\n                    st.info(\"ℹ️ Consolidación de portafolios de inversión, fondos mutuos, acciones y depósitos a plazo. (En desarrollo)\")\n                    st.write(\"Esta sección está en construcción. Próximamente podrás subir cartolas de inversión para análisis automático.\")\n                    st.file_uploader(\"Subir Cartola de Inversiones (PDF/Excel)\", key=f\"inv_dummy_new\", disabled=True)"
        
        replace5 = """with st.expander("📈 (6) Inversiones Consolidadas"):
                st.session_state[f"omit_{rut}_inversiones"] = st.checkbox("Omitir sección", value=st.session_state.get(f"omit_{rut}_inversiones", False), key=f"cb_omit_{rut}_inversiones")
                if st.session_state[f"omit_{rut}_inversiones"]:
                    st.info("⚠️ La sección de Inversiones fue omitida intencionalmente.")
                else:
                    st.info("ℹ️ Consolidación de portafolios de inversión, AFP y otros activos.")
                    
                    with st.expander("📥 Importar Cartolas de Inversión y AFP", expanded=False):
                        st.info("Sube múltiples cartolas de AFP, Fondos Mutuos o Inversiones.")
                        inv_files = st.file_uploader("Subir archivos (PDF/Excel)", type=["pdf", "xlsx", "xls", "csv"], accept_multiple_files=True, key=f"inv_files_{rut}")
                        if inv_files:
                            if st.button("Procesar Cartolas", type="primary"):
                                st.warning("Procesamiento de cartolas múltiples en desarrollo.")
                    
                    st.markdown("##### Portafolio de Inversiones")
                    edited_inv = st.data_editor(
                        st.session_state[k_inv],
                        num_rows="dynamic",
                        use_container_width=True,
                        key=f"editor_inversiones_{rut}",
                        column_config={
                            "Monto": st.column_config.NumberColumn(format="$ %,d"),
                            "Monto (CLP)": st.column_config.NumberColumn(format="$ %,d")
                        }
                    )"""
        
        content = content.replace(target5, replace5)
        
        # 6. Save in session
        target6 = "if \"edited_repres\" in locals():\n                    st.session_state[k_repres] = edited_repres"
        replace6 = target6 + "\n                if \"edited_inv\" in locals():\n                    st.session_state[k_inv] = edited_inv"
        content = content.replace(target6, replace6)
        
        # 7. Save to DB
        target7 = "# --- PERSISTENCIA EN BASE DE DATOS REAL ---"
        replace7 = """if "edited_inv" in locals():
                            from src.database.models import ClientPortfolio
                            db.query(ClientPortfolio).filter(ClientPortfolio.prospect_id == prospect.id).delete()
                            for _, row in edited_inv.iterrows():
                                def safe_float(val):
                                    try: return float(val) if pd.notna(val) else 0.0
                                    except: return 0.0
                                kwargs = {
                                    "prospect_id": prospect.id,
                                    "institucion": str(row.get("Institución", "")),
                                    "activo": str(row.get("Activo", "")),
                                    "tipo_activo": str(row.get("Tipo", "")),
                                    "monto_original": safe_float(row.get("Monto")),
                                    "moneda_original": str(row.get("Moneda", "CLP")),
                                    "monto_clp": safe_float(row.get("Monto (CLP)"))
                                }
                                db.add(ClientPortfolio(**kwargs))
                        
                        # --- PERSISTENCIA EN BASE DE DATOS REAL ---"""
        content = content.replace(target7, replace7)
        
        with open('src/web/client_management_ui.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Updated Section 6 logic!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
