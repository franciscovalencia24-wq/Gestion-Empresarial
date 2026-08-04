import os
from fpdf import FPDF

# Asegurar directorio
save_dir = "data/knowledge/camv_pdfs"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=15)
pdf.cell(200, 10, txt="Normativa CAMV - Resumen de Acreditación (Muestra Automática)", ln=1, align='C')

pdf.set_font("Arial", size=12)
text = """
Articulo 1. El análisis de idoneidad según la norma N 412: 
Debe indicar expresamente el perfil de riesgo del cliente, sus objetivos de inversión, su horizonte de tiempo y su tolerancia a la pérdida. 

Articulo 2. Un Intermediario de Valores:
Es aquella entidad o persona natural registrada en la CMF, autorizada para transar valores y ofrecer asesoría financiera de forma pública.

Esta es una prueba generada automáticamente para inicializar la base de vectores del motor RAG, dado que la página oficial de CAMV restringe los PDFs detrás de un login o iframes complejos en su portada.
"""
pdf.multi_cell(0, 10, text)
pdf.output(os.path.join(save_dir, "Normativa_CAMV_Muestra.pdf"))
print("PDF de muestra generado correctamente.")
