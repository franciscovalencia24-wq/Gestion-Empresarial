import re

file_path = r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\web\client_management_ui.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'(?s)edited_polizas = st\.data_editor\(.*?\s+key=f"editor_polizas_\{rut\}",\s+column_config=\{.*?\}\s+\)'

replacement = '''
                    # --- NUEVO RENDERIZADO VERTICAL DE PÓLIZAS (HITO 3) ---
                    edited_polizas_rows = []
                    current_polizas = st.session_state[k_poliza]
                    
                    for idx, row in current_polizas.iterrows():
                        with st.expander(f"📄 Póliza: {row.get('Aseguradora', 'Sin Aseguradora')} - {row.get('Tipo', 'Sin Tipo')} ({row.get('N° Póliza', '')})", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                aseguradora = st.text_input("Aseguradora", value=str(row.get("Aseguradora", "")), key=f"pol_aseg_{rut}_{idx}")
                                asegurado = st.text_input("Asegurado", value=str(row.get("Asegurado", "")), key=f"pol_asedo_{rut}_{idx}")
                                contratante = st.text_input("Contratante", value=str(row.get("Contratante", "")), key=f"pol_cont_{rut}_{idx}")
                                tipo = st.text_input("Bien Asegurado (Tipo)", value=str(row.get("Tipo", "")), key=f"pol_tipo_{rut}_{idx}")
                            with col2:
                                n_pol = st.text_input("N° Póliza / Código", value=str(row.get("N° Póliza", "")), key=f"pol_num_{rut}_{idx}")
                                col_ind = st.text_input("Colectivo / Individual", value=str(row.get("Colectivo / Individual", "")), key=f"pol_col_{rut}_{idx}")
                                alias = st.text_input("Alias / Patente", value=str(row.get("Alias / Patente", "")), key=f"pol_alias_{rut}_{idx}")
                                f_cont = st.text_input("Fecha Contratación (DD/MM/YYYY)", value=str(row.get("Fecha Contratación", "")), help="Pólizas Post-04/02/2022 están afectas a impuesto a la herencia según Ley 21.420", key=f"pol_fcont_{rut}_{idx}")
                            with col3:
                                monto = st.number_input("Monto (UF)", value=float(row.get("Monto (UF)") or 0.0), key=f"pol_monto_{rut}_{idx}")
                                prima = st.number_input("Prima", value=float(row.get("Prima") or 0.0), key=f"pol_prima_{rut}_{idx}")
                                medio_pago = st.text_input("Medio de Pago", value=str(row.get("Medio de Pago", "")), key=f"pol_pago_{rut}_{idx}")
                                is_apv = st.checkbox("¿APV Póliza?", value=bool(row.get("¿APV Póliza?", False)), help="Pólizas de APV acogidas al Art. 42 LIR", key=f"pol_apv_{rut}_{idx}")
                            
                            st.markdown("**Coberturas (Letra Chica)**")
                            coberturas = st.text_area("Detalle de coberturas", value=str(row.get("Coberturas", "")), height=100, key=f"pol_cob_{rut}_{idx}")
                            st.markdown("**💡 Análisis IA Comercial**")
                            analisis_ia = st.text_area("Diagnóstico IA", value=str(row.get("Análisis IA", "")), height=100, disabled=True, key=f"pol_ia_{rut}_{idx}")
                            
                            new_row = row.copy()
                            new_row["Aseguradora"] = aseguradora
                            new_row["Asegurado"] = asegurado
                            new_row["Contratante"] = contratante
                            new_row["Tipo"] = tipo
                            new_row["N° Póliza"] = n_pol
                            new_row["Colectivo / Individual"] = col_ind
                            new_row["Alias / Patente"] = alias
                            new_row["Fecha Contratación"] = f_cont
                            new_row["Monto (UF)"] = monto
                            new_row["Prima"] = prima
                            new_row["Medio de Pago"] = medio_pago
                            new_row["¿APV Póliza?"] = is_apv
                            new_row["Coberturas"] = coberturas
                            new_row["Análisis IA"] = analisis_ia
                            edited_polizas_rows.append(new_row)

                    if st.button("➕ Añadir Póliza Manual", key=f"add_poliza_{rut}"):
                        empty_row = {c: "" for c in current_polizas.columns}
                        if "Monto (UF)" in empty_row: empty_row["Monto (UF)"] = 0.0
                        if "Prima" in empty_row: empty_row["Prima"] = 0.0
                        if "¿APV Póliza?" in empty_row: empty_row["¿APV Póliza?"] = False
                        edited_polizas_rows.append(empty_row)
                        st.session_state[k_poliza] = pd.DataFrame(edited_polizas_rows)
                        st.rerun()

                    edited_polizas = pd.DataFrame(edited_polizas_rows) if edited_polizas_rows else current_polizas
'''

content, count = re.subn(pattern, replacement, content)
print(f"Replaced UI: {count}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
