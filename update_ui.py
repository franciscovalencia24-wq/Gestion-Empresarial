import sys

def update_file():
    with open('src/web/client_management_ui.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Imports
    target_imports = "import io\nimport datetime"
    replace_imports = "import io\nimport datetime\nimport plotly.express as px\nimport plotly.graph_objects as go\nfrom src.osint.parser_inversiones import parse_investment_files"
    if target_imports in content:
        content = content.replace(target_imports, replace_imports)

    # 2. Plantilla Inmobiliaria
    target_plantilla = "st.info(\"Sube el archivo Excel descargado desde la pǭgina del SII ('Consultar mis bienes races').\")\n                        render_manual_button"
    replace_plantilla = "st.info(\"Sube el archivo Excel descargado desde la pǭgina del SII ('Consultar mis bienes races').\")\n                        \n                        def generar_plantilla():\n                            cols_manual = [\"ROL\", \"Nombre/Alias\", \"Valor Com. (UF)\", \"Deuda Hipotecaria\", \"Institucin Hipoteca\", \"Monto Inicial (UF)\", \"Saldo Actual (UF)\", \"Monto Asegurado (UF)\", \"Tasacin (UF)\", \"Tasa InterǸs (%)\", \"Tipo Tasa\", \"Fecha Escritura\", \"Dividendo\", \"Cuota Actual\", \"Total Cuotas\", \"Arrendada\", \"Monto Arriendo\", \"Moneda Arriendo\", \"Fecha Contrato Arriendo\", \"Meses Reajuste Arriendo\", \"Contribuciones Trim.\", \"Gastos Comunes Mensuales\", \"Mantencin Anual (CLP)\", \"Plusvala Esperada (%)\"]\n                            df_plantilla = pd.DataFrame(columns=cols_manual)\n                            buffer = io.BytesIO()\n                            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:\n                                df_plantilla.to_excel(writer, index=False)\n                            return buffer.getvalue()\n                            \n                        st.download_button(\n                            label=\"Y"" Descargar Plantilla Inmobiliaria FV\",\n                            data=generar_plantilla(),\n                            file_name=\"Plantilla_Inmobiliaria_FV.xlsx\",\n                            mime=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\"\n                        )\n                        \n                        render_manual_button"
    
    if target_plantilla in content:
        content = content.replace(target_plantilla, replace_plantilla)
        
    # 3. Cartolas
    target_cartolas = "if st.button(\"Procesar Cartolas\", type=\"primary\"):\n                                st.warning(\"Procesamiento de cartolas mǧltiples en desarrollo.\")"
    replace_cartolas = "if st.button(\"Procesar Cartolas con IA\", type=\"primary\"):\n                                with st.spinner(\"Analizando cartolas con Inteligencia Artificial (Gemini)...\"):\n                                    file_bytes_list = [f.read() for f in inv_files]\n                                    file_names = [f.name for f in inv_files]\n                                    try:\n                                        df_extracted = parse_investment_files(file_bytes_list, file_names)\n                                        if not df_extracted.empty:\n                                            st.session_state[k_inv] = pd.concat([st.session_state[k_inv], df_extracted], ignore_index=True)\n                                            st.success(f\"o. Se extrajeron {len(df_extracted)} posiciones correctamente.\")\n                                        else:\n                                            st.error(\"No se encontraron posiciones o hubo un error en la extraccin.\")\n                                    except Exception as e:\n                                        st.error(f\"Error procesando cartolas: {e}\")"
    
    if target_cartolas in content:
        content = content.replace(target_cartolas, replace_cartolas)

    # 4. Graficos Plotly
    target_graficos = "                            \"Monto (CLP)\": st.column_config.NumberColumn(format=\"$ %,d\")\n                        }\n                    )"
    replace_graficos = "                            \"Monto (CLP)\": st.column_config.NumberColumn(format=\"$ %,d\")\n                        }\n                    )\n                    \n                    if not edited_inv.empty:\n                        st.markdown(\"##### Y"" Distribucin del Portafolio\")\n                        df_plot = edited_inv.copy()\n                        df_plot[\"Monto (CLP)\"] = pd.to_numeric(df_plot[\"Monto (CLP)\"], errors='coerce').fillna(0)\n                        df_plot = df_plot[df_plot[\"Monto (CLP)\"] > 0]\n                        \n                        if not df_plot.empty:\n                            col1, col2 = st.columns(2)\n                            with col1:\n                                fig1 = px.pie(df_plot, values=\"Monto (CLP)\", names=\"Institucin\", title=\"Por Institucin\", hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)\n                                fig1.update_traces(textposition='inside', textinfo='percent+label')\n                                st.plotly_chart(fig1, use_container_width=True)\n                            with col2:\n                                fig2 = px.pie(df_plot, values=\"Monto (CLP)\", names=\"Tipo\", title=\"Por Tipo de Activo\", hole=0.4, color_discrete_sequence=px.colors.sequential.Burg)\n                                fig2.update_traces(textposition='inside', textinfo='percent+label')\n                                st.plotly_chart(fig2, use_container_width=True)\n                        else:\n                            st.info(\"Ingresa montos vǭlidos en CLP para visualizar la distribucin.\")"
    
    if target_graficos in content:
        content = content.replace(target_graficos, replace_graficos)

    with open('src/web/client_management_ui.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done")

update_file()
