import re

file_path = r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\web\client_management_ui.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the UI block
ui_pattern = r'(?s)edited_sociedades = st\.data_editor\(.*?\s+key=f"editor_sociedades_\{rut\}"\s+\)'
ui_replacement = '''
                    edited_sociedades_rows = []
                    # Initialize columns if missing
                    if "Valor Estimado ($)" not in current_df.columns:
                        current_df["Valor Estimado ($)"] = 0.0
                    if "¿Posee Bienes Raíces?" not in current_df.columns:
                        current_df["¿Posee Bienes Raíces?"] = False

                    for idx, row in current_df.iterrows():
                        with st.expander(f"🏢 Sociedad: {row.get('Razon Social', row.get('Razón Social', 'Sin Nombre'))} ({row.get('RUT Empresa', '')})"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                rut_emp = st.text_input("RUT Empresa", value=str(row.get("RUT Empresa", "")), key=f"emp_rut_{rut}_{idx}")
                                razon = st.text_input("Razón Social", value=str(row.get("Razón Social", row.get("Razon Social", ""))), key=f"emp_rs_{rut}_{idx}")
                            with col2:
                                incorp = st.text_input("Incorporación", value=str(row.get("Incorporación", "")), key=f"emp_inc_{rut}_{idx}")
                                cap = st.text_input("% Capital", value=str(row.get("% Capital", "")), key=f"emp_cap_{rut}_{idx}")
                                util = st.text_input("% Utilidades", value=str(row.get("% Utilidades", "")), key=f"emp_util_{rut}_{idx}")
                            with col3:
                                st.markdown("**Valorización (VPP)**")
                                val_est = st.number_input("Valor Estimado de la Sociedad ($)", value=float(row.get("Valor Estimado ($)") or 0.0), key=f"emp_val_{rut}_{idx}")
                                bienes = st.checkbox("¿Posee Bienes Raíces?", value=bool(row.get("¿Posee Bienes Raíces?", False)), key=f"emp_bienes_{rut}_{idx}")
                            
                            new_row = row.copy()
                            new_row["RUT Empresa"] = rut_emp
                            new_row["Razón Social"] = razon
                            new_row["Incorporación"] = incorp
                            new_row["% Capital"] = cap
                            new_row["% Utilidades"] = util
                            new_row["Valor Estimado ($)"] = val_est
                            new_row["¿Posee Bienes Raíces?"] = bienes
                            edited_sociedades_rows.append(new_row)

                    if st.button("➕ Añadir Sociedad Manual", key=f"add_soc_{rut}"):
                        empty_row = {c: "" for c in current_df.columns}
                        empty_row["Valor Estimado ($)"] = 0.0
                        empty_row["¿Posee Bienes Raíces?"] = False
                        edited_sociedades_rows.append(empty_row)
                        st.session_state[k_comp] = pd.DataFrame(edited_sociedades_rows)
                        st.rerun()

                    edited_sociedades = pd.DataFrame(edited_sociedades_rows) if edited_sociedades_rows else current_df
'''
content, count_ui = re.subn(ui_pattern, ui_replacement, content)
print(f"Replaced UI: {count_ui}")

# 2. Update the save logic
save_pattern = r'(?s)(nueva_sociedad = ClientCompany\(\s+prospect_id=prospect\.id,\s+rut_empresa=str\(row\.get\("RUT Empresa", ""\)\),\s+razon_social=str\(row\.get\("Raz.*?n Social", ""\)\),\s+fecha_incorporacion=str\(row\.get\("Incorporaci.*?n", ""\)\),\s+porcentaje_capital=cap,\s+porcentaje_utilidades=ut\s+\))'
save_replacement = r'''\1
                                  nueva_sociedad.valor_estimado = float(row.get("Valor Estimado ($)", 0.0))
                                  nueva_sociedad.posee_bienes_raices = bool(row.get("¿Posee Bienes Raíces?", False))'''
content, count_save = re.subn(save_pattern, save_replacement, content)
print(f"Replaced Save Logic: {count_save}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
