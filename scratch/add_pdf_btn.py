import os

with open('src/web/analysis_hub_ui.py', 'r', encoding='utf-8') as f:
    text = f.read()

if 'generar_pdf_analisis_integral' not in text:
    pdf_button_code = """
            # BOTON PARA GENERAR PDF
            st.markdown("---")
            if st.button("📄 Generar Reporte PDF (Análisis Integral)", type="primary"):
                with st.spinner("Generando documento PDF institucional..."):
                    from src.utils.pdf_generator_analysis import generar_pdf_analisis_integral
                    # get client name if available
                    rut_cliente = st.session_state.get("current_client_rut", "12345678-9")
                    target = summary.get("target_mean_price", "N/A") if 'summary' in locals() else "N/A"
                    try:
                        pdf_path = generar_pdf_analisis_integral(
                            ticker=ticker,
                            tech_opinion=tech_opinion if do_tech else "No solicitado.",
                            fund_opinion=fund_opinion if do_fund else "No solicitado.",
                            is_generic=False,
                            client_rut=rut_cliente,
                            target_price=target
                        )
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="📥 Descargar PDF Analítico",
                                    data=pdf_file,
                                    file_name=f"Reporte_Analisis_{ticker}.pdf",
                                    mime="application/pdf"
                                )
                        else:
                            st.error("No se pudo generar el archivo PDF.")
                    except Exception as e:
                        st.error(f"Error en la generación del reporte: {e}")
"""
    with open('src/web/analysis_hub_ui.py', 'a', encoding='utf-8') as f:
        f.write(pdf_button_code)
    print("PDF Button Added")
else:
    print("PDF Button already exists")
