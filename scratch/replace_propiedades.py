import re

file_path = r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\web\client_management_ui.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'(?s)edited_propiedades = st\.data_editor\(.*?\)\s+# --- CÁLCULO DE MÉTRICAS INMOBILIARIAS EN VIVO ---'

replacement = '''                    # --- NUEVO RENDERIZADO VERTICAL DE PROPIEDADES (HITO 1) ---
                    edited_rows = []
                    for idx, row in df_display.iterrows():
                        with st.expander(f"🏠 Propiedad {row.get('N°', idx+1)}: {row.get('Dirección', 'Sin Dirección')} ({row.get('Comuna', '')})", expanded=False):
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                rol = st.text_input("ROL", value=str(row.get("ROL", "")), key=f"rol_{rut}_{idx}")
                                direccion = st.text_input("Dirección", value=str(row.get("Dirección", "")), key=f"dir_{rut}_{idx}")
                                comuna = st.text_input("Comuna", value=str(row.get("Comuna", "")), key=f"com_{rut}_{idx}")
                                destino = st.text_input("Destino", value=str(row.get("Destino", "HABITACIONAL")), key=f"dest_{rut}_{idx}")
                            with col2:
                                avaluo = st.number_input("Avalúo Fiscal ($)", value=float(row.get("Avalúo Fiscal (CLP)") or 0.0), key=f"avaluo_{rut}_{idx}")
                                val_com = st.number_input("Valor Comercial (UF)", value=float(row.get("Valor Com. (UF)") or 0.0), key=f"valcom_{rut}_{idx}")
                                origen = st.selectbox("Origen Valor", ["Sugerida por AI", "Tasación Real / Cliente"], index=0 if row.get("Origen Tasación", "") == "Sugerida por AI" else 1, key=f"orig_{rut}_{idx}")
                                pct_derecho = st.number_input("% de Derecho", value=float(row.get("% de Derecho") or 100.0), max_value=100.0, key=f"pct_{rut}_{idx}")
                            with col3:
                                tiene_deuda = st.checkbox("¿Tiene Deuda?", value=bool(row.get("Deuda Hipotecaria", False)), key=f"deuda_{rut}_{idx}")
                                monto_ini = st.number_input("Monto Inicial (UF)", value=float(row.get("Monto Inicial (UF)") or 0.0), key=f"mini_{rut}_{idx}")
                                saldo_act = st.number_input("Saldo Actual (UF)", value=float(row.get("Saldo Actual (UF)") or 0.0), key=f"sact_{rut}_{idx}")
                                dividendo = st.number_input("Dividendo (UF)", value=float(row.get("Dividendo") or 0.0), key=f"div_{rut}_{idx}")
                            with col4:
                                arrendada = st.checkbox("¿Arrendada?", value=bool(row.get("Arrendada", False)), key=f"arren_{rut}_{idx}")
                                monto_arr = st.number_input("Monto Arriendo ($)", value=float(row.get("Monto Arriendo") or 0.0), key=f"marr_{rut}_{idx}")
                                cap_rate = st.number_input("Cap Rate (%)", value=float(row.get("Rentabilidad S/Deuda (Cap Rate %)") or 0.0), disabled=True, key=f"cap_{rut}_{idx}")
                                roe = st.number_input("ROE (%)", value=float(row.get("Retorno C/Deuda (ROE %)") or 0.0), disabled=True, key=f"roe_{rut}_{idx}")
                            
                            new_row = row.copy()
                            new_row["ROL"] = rol
                            new_row["Dirección"] = direccion
                            new_row["Comuna"] = comuna
                            new_row["Destino"] = destino
                            new_row["Avalúo Fiscal (CLP)"] = avaluo
                            new_row["Valor Com. (UF)"] = val_com
                            new_row["Origen Tasación"] = origen
                            new_row["% de Derecho"] = pct_derecho
                            new_row["Deuda Hipotecaria"] = tiene_deuda
                            new_row["Monto Inicial (UF)"] = monto_ini
                            new_row["Saldo Actual (UF)"] = saldo_act
                            new_row["Dividendo"] = dividendo
                            new_row["Arrendada"] = arrendada
                            new_row["Monto Arriendo"] = monto_arr
                            edited_rows.append(new_row)

                    if st.button("➕ Añadir Propiedad Manual", key=f"add_prop_{rut}"):
                        empty_row = {c: 0.0 if "UF" in c or "CLP" in c or "%" in c else "" for c in df_display.columns}
                        empty_row["N°"] = len(edited_rows) + 1
                        edited_rows.append(empty_row)
                        st.session_state[k_prop] = pd.DataFrame(edited_rows)
                        st.rerun()

                    edited_propiedades = pd.DataFrame(edited_rows) if edited_rows else df_display

                    # --- CÁLCULO DE MÉTRICAS INMOBILIARIAS EN VIVO ---'''

new_content, count = re.subn(pattern, replacement, content)
print(f"Replaced {count} instances.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
