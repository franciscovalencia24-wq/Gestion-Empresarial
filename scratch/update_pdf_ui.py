import re

file_path = r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\web\client_management_ui.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the PDF button logic
pattern = r'(?s)pdf_top_bytes = generate_succession_report_pdf\(p_top\.id\) if p_top else None.*?if pdf_top_bytes:.*?col_btn_pdf\.download_button\('
replacement = '''report_type = st.radio("Tipo de Reporte 360°", ["Ejecutivo (Resumen de Alto Impacto)", "Detallado (Análisis Completo)"], horizontal=True, key=f"rep_type_{rut}")
                pdf_top_bytes = generate_succession_report_pdf(p_top.id, "Ejecutivo" if "Ejecutivo" in report_type else "Detallado") if p_top else None
                db_top.close()
            except:
                pdf_top_bytes = None

            if pdf_top_bytes:
                col_btn_pdf.download_button('''

content, count1 = re.subn(pattern, replacement, content)
print(f"Replaced Top PDF Button: {count1}")

pattern2 = r'(?s)pdf_suc_bytes = generate_succession_report_pdf\(prospect\.id\) if prospect else None.*?if pdf_suc_bytes:.*?st\.download_button\('
replacement2 = '''report_type_sec = st.radio("Tipo de Reporte Sucesorio", ["Ejecutivo (Resumen de Alto Impacto)", "Detallado (Análisis Completo)"], horizontal=True, key=f"rep_type_sec_{rut}")
                            pdf_suc_bytes = generate_succession_report_pdf(prospect.id, "Ejecutivo" if "Ejecutivo" in report_type_sec else "Detallado") if prospect else None
                        except:
                            pdf_suc_bytes = None

                        if pdf_suc_bytes:
                            st.download_button('''

content, count2 = re.subn(pattern2, replacement2, content)
print(f"Replaced Sec PDF Button: {count2}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
