import re

with open('src/web/client_management_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
content = re.sub(
    r'(import datetime)',
    r'\1\nimport plotly.express as px\nimport plotly.graph_objects as go\nfrom src.osint.parser_inversiones import parse_investment_files',
    content,
    count=1
)

# 2. Plantilla Inmobiliaria
plantilla_code = """
                        def generar_plantilla():
                            cols_manual = ["ROL", "Nombre/Alias", "Valor Com. (UF)", "Deuda Hipotecaria", "Institución Hipoteca", "Monto Inicial (UF)", "Saldo Actual (UF)", "Monto Asegurado (UF)", "Tasación (UF)", "Tasa Interés (%)", "Tipo Tasa", "Fecha Escritura", "Dividendo", "Cuota Actual", "Total Cuotas", "Arrendada", "Monto Arriendo", "Moneda Arriendo", "Fecha Contrato Arriendo", "Meses Reajuste Arriendo", "Contribuciones Trim.", "Gastos Comunes Mensuales", "Mantención Anual (CLP)", "Plusvalía Esperada (%)"]
                            df_plantilla = pd.DataFrame(columns=cols_manual)
                            buffer = io.BytesIO()
                            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                df_plantilla.to_excel(writer, index=False)
                            return buffer.getvalue()
                            
                        st.download_button(
                            label="📥 Descargar Plantilla Inmobiliaria FV",
                            data=generar_plantilla(),
                            file_name="Plantilla_Inmobiliaria_FV.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        render_manual_button("manual_sii_bienes_raices.pdf","""

content = re.sub(
    r'(st\.info\([^)]*bienes raíces[^)]*\)\n\s*)(render_manual_button\("manual_sii_bienes_raices\.pdf",)',
    r'\1' + plantilla_code.replace('\\', '\\\\'),
    content,
    flags=re.IGNORECASE
)


# 3. Cartolas
cartolas_code = """if st.button("Procesar Cartolas con IA", type="primary"):
                                with st.spinner("Analizando cartolas con Inteligencia Artificial (Gemini)..."):
                                    file_bytes_list = [f.read() for f in inv_files]
                                    file_names = [f.name for f in inv_files]
                                    try:
                                        df_extracted = parse_investment_files(file_bytes_list, file_names)
                                        if not df_extracted.empty:
                                            st.session_state[k_inv] = pd.concat([st.session_state[k_inv], df_extracted], ignore_index=True)
                                            st.success(f"✅ Se extrajeron {len(df_extracted)} posiciones correctamente.")
                                        else:
                                            st.error("No se encontraron posiciones o hubo un error en la extracción.")
                                    except Exception as e:
                                        st.error(f"Error procesando cartolas: {e}")"""
                                        
content = re.sub(
    r'if st\.button\("Procesar Cartolas", type="primary"\):\n\s*st\.warning\("Procesamiento de cartolas[^"]*"\)',
    cartolas_code,
    content
)

# 4. Graficos Plotly
graficos_code = """                            "Monto (CLP)": st.column_config.NumberColumn(format="$ %,d")
                        }
                    )
                    
                    if not edited_inv.empty:
                        st.markdown("##### 📊 Distribución del Portafolio")
                        df_plot = edited_inv.copy()
                        df_plot["Monto (CLP)"] = pd.to_numeric(df_plot["Monto (CLP)"], errors='coerce').fillna(0)
                        df_plot = df_plot[df_plot["Monto (CLP)"] > 0]
                        
                        if not df_plot.empty:
                            col1, col2 = st.columns(2)
                            with col1:
                                fig1 = px.pie(df_plot, values="Monto (CLP)", names="Institución", title="Por Institución", hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
                                fig1.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig1, use_container_width=True)
                            with col2:
                                fig2 = px.pie(df_plot, values="Monto (CLP)", names="Tipo", title="Por Tipo de Activo", hole=0.4, color_discrete_sequence=px.colors.sequential.Burg)
                                fig2.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig2, use_container_width=True)
                        else:
                            st.info("Ingresa montos válidos en CLP para visualizar la distribución.")"""

content = re.sub(
    r'("Monto \(CLP\)": st\.column_config\.NumberColumn\(format="\$ %,d"\)\n\s*\}\n\s*\))',
    graficos_code,
    content
)

with open('src/web/client_management_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Regex replace applied")
