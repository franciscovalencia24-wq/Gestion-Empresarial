import os

filepath = "src/web/cartolas_ui.py"

with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

execution_logic = """
                    st.markdown("---")
                    st.markdown("### 🚀 Ejecución Autónoma (Agente de Salida)")
                    col_exec1, col_exec2 = st.columns(2)
                    
                    with col_exec1:
                        if st.button("📄 Exportar a PDF", use_container_width=True):
                            from src.intelligence.execution_agent import ExecutionAgent
                            import tempfile
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
                        st.markdown(f\"\"\"<a href="{email_data['mailto_link']}" target="_blank">
                                    <button style='background-color:#1e3a8a;color:white;padding:10px;border:none;border-radius:5px;cursor:pointer;width:100%;font-weight:bold;'>
                                    🚀 Abrir directamente en Outlook / Mail</button></a>\"\"\", unsafe_allow_html=True)
"""

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if 'st.markdown(st.session_state[f"estrategia_{prospect.id}"])' in line:
        new_lines.append(execution_logic)

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Phase 3 Patch applied successfully.")
