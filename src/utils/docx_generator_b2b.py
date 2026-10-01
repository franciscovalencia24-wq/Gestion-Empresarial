import os
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import B2B_LICENSE_TIERS

def generar_propuesta_b2b_docx(output_path: str):
    """
    Genera el documento comercial B2B de Altus Core en formato Word (.docx).
    """
    doc = Document()
    
    # Configuración de márgenes
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Encabezado con Logo Oficial FV desde la carpeta de marca assets/brand
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    fv_logo_path = os.path.join(root_dir, "assets", "brand", "fv_logo_principal_light.png")
    if not os.path.exists(fv_logo_path):
        fv_logo_path = os.path.join(root_dir, "assets", "brand", "fv_logo_principal_trimmed.png")
    if os.path.exists(fv_logo_path):
        try:
            p_logo = doc.add_paragraph()
            p_logo.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run_logo = p_logo.add_run()
            run_logo.add_picture(fv_logo_path, width=Inches(1.8))
        except Exception:
            pass

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run_sub = title_p.add_run("PROPUESTA COMERCIAL INSTITUCIONAL B2B | ALTUS AI SpA\n")
    run_sub.font.size = Pt(8.5)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(10, 35, 66)
    
    run_date = title_p.add_run(f"Fecha de Emisión: {datetime.now().strftime('%d-%m-%Y')}\n")
    run_date.font.size = Pt(8)
    run_date.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph()

    # Título Principal del Reporte
    h1 = doc.add_heading("Altus Core: Beneficio de Bienestar Financiero Ejecutivo", level=1)
    h1.runs[0].font.color.rgb = RGBColor(16, 75, 60)
    h1.runs[0].font.size = Pt(18)
    
    doc.add_paragraph()

    # 1. Diagnóstico del Dolor Empresarial
    h2_diag = doc.add_heading("1. El Desafío de Retención de Talento Ejecutivo", level=2)
    h2_diag.runs[0].font.color.rgb = RGBColor(10, 35, 66)
    
    p_diag = doc.add_paragraph(
        "El ecosistema corporativo actual, particularmente en la gran minería y alta dirección, enfrenta una fuga constante de talento clave (C-Level). Los paquetes de compensación tradicionales han perdido tracción frente a la falta de herramientas personalizadas para el resguardo patrimonial del ejecutivo.\n\n"
        "Existe un dolor crítico y silencioso en las gerencias: la desorganización de sus estructuras de ahorro, la fuga fiscal por ineficiencia tributaria (Operación Renta) y la exposición de sus familias por pólizas de seguros cautivas asociadas a créditos hipotecarios (que protegen a la banca, no a los herederos)."
    )
    p_diag.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # 2. Detalle del Beneficio Reporte 360
    h2_360 = doc.add_heading("2. La Solución: Reporte Patrimonial 360", level=2)
    h2_360.runs[0].font.color.rgb = RGBColor(10, 35, 66)

    p_360 = doc.add_paragraph(
        "Altus AI SpA ofrece a su organización la plataforma SaaS 'Altus Core' bajo un modelo B2B2C. Este licenciamiento permite a la empresa otorgar a sus gerentes una auditoría patrimonial integral, determinista y absolutamente confidencial, sin involucrar intermediación ni captación de fondos.\n\n"
        "El Reporte 360 integra:"
    )
    p_360.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    items_360 = [
        "Consolidación Patrimonial (Activos financieros e inmobiliarios).",
        "Auditoría Activa de Deudas (Sincronización normativa con Comisión para el Mercado Financiero - CMF).",
        "Protección Sucesoria (Auditoría 'Conoce tu Seguro' para mitigar riesgo de liquidez familiar y canjear pólizas bancarias).",
        "Optimización Fiscal DPE y Reliquidación (Ahorro tributario algorítmico sin intervención manual)."
    ]
    for item in items_360:
        doc.add_paragraph(item, style='List Bullet')
        
    doc.add_paragraph()

    # 3. Modelo de Suscripción B2B2C
    h2_lic = doc.add_heading("3. Licenciamiento SaaS Institucional", level=2)
    h2_lic.runs[0].font.color.rgb = RGBColor(10, 35, 66)

    p_lic = doc.add_paragraph(
        "El licenciamiento de Altus Core se estructura mediante un fee anual recurrente (SaaS) escalable por volumen de usuarios ejecutivos activos en la corporación:"
    )

    t_lic = doc.add_table(rows=1, cols=4)
    t_lic.style = 'Table Grid'
    t_lic.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_lic.autofit = True
    
    hdr_cells = t_lic.rows[0].cells
    headers = ["Nivel de Suscripción", "Límite de Usuarios Activos", "Valor Unitario (UF/Año)", "Alcance del Servicio"]
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        shading_elm = parse_xml(r'<w:shd {} w:fill="0A2342"/>'.format(nsdecls('w')))
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading_elm)
        for paragraph in hdr_cells[i].paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.size = Pt(8.5)
                run.font.color.rgb = RGBColor(255, 255, 255)

    for tier_key, tier_data in B2B_LICENSE_TIERS.items():
        row_cells = t_lic.add_row().cells
        row_cells[0].text = tier_key.replace("_", " ")
        max_users = str(tier_data['max_users']) if tier_data['max_users'] != float('inf') else "Ilimitado (> 200)"
        row_cells[1].text = max_users
        row_cells[2].text = f"{tier_data['price_per_user_uf']} UF"
        row_cells[3].text = tier_data['description']
        for cell in row_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9)

    doc.add_paragraph()

    # 4. Ciberseguridad & Cumplimiento Normativo
    h2_sec = doc.add_heading("4. Cumplimiento Regulatorio y Seguridad (Zero-Knowledge)", level=2)
    h2_sec.runs[0].font.color.rgb = RGBColor(10, 35, 66)

    p_sec_det = doc.add_paragraph(
        "Para garantizar la estricta privacidad de los ejecutivos frente a su empleador corporativo, Altus Core se arquitectura bajo un esquema Zero-Knowledge y pseudonimización. "
        "Toda información PII (Nombres, RUT, Balances) se cifra algorítmicamente mediante AES-256 (Advanced Encryption Standard). "
        "Este diseño permite a Altus AI SpA asegurar el cumplimiento preventivo de la nueva Ley Fintec (Ley 21.521) y el estándar bancario de Protección de Datos Personales (Ley 21.096)."
    )
    p_sec_det.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_paragraph()
    
    # Footer Ciberseguridad
    p_sec = doc.add_paragraph()
    p_sec.paragraph_format.space_before = Pt(10)
    run_sec_t = p_sec.add_run("🔒 Certificación Tecnológica: ")
    run_sec_t.bold = True
    run_sec_t.font.size = Pt(8.5)
    run_sec_t.font.color.rgb = RGBColor(10, 35, 66)
    run_sec_b = p_sec.add_run(
        "Documento generado de manera autónoma. La propiedad intelectual de los algoritmos de tributación y la estructura del Reporte 360 pertenece exclusivamente a ALTUS AI SpA, salvaguardada por Acuerdos Institucionales de No Divulgación (NDA)."
    )
    run_sec_b.font.size = Pt(8.5)
    run_sec_b.font.color.rgb = RGBColor(51, 65, 85)
    
    # Save the document
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    doc.save(output_path)
    return output_path

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    export_path = os.path.join(root_dir, "exports", "Propuesta_Comercial_B2B_Altus_Core.docx")
    generar_propuesta_b2b_docx(export_path)
    print(f"Propuesta generada en: {export_path}")
