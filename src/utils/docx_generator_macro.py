import os
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def generate_macro_docx(cliente_nombre: str, contenido_markdown: str, output_path: str):
    """
    Genera un informe institucional ejecutable en formato Word (.docx)
    con encabezados corporativos, disclaimers, Sobre FV Asesorías y ciberseguridad.
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
    run_sub = title_p.add_run("DIGITAL FAMILY OFFICE ANALYTICS | FV ASESORÍAS & ALTUS AI\n")
    run_sub.font.size = Pt(8.5)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(10, 35, 66)
    
    run_date = title_p.add_run(f"Fecha de Emisión: {datetime.now().strftime('%d-%m-%Y')}\n")
    run_date.font.size = Pt(8)
    run_date.font.color.rgb = RGBColor(100, 116, 139)

    # Tabla de Datos del Reporte
    tbl = doc.add_table(rows=2, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = True
    
    cell_a = tbl.cell(0, 0)
    cell_a.text = f"Atención a: {cliente_nombre}"
    cell_b = tbl.cell(0, 1)
    cell_b.text = f"Fecha: {datetime.now().strftime('%d/%m/%Y')}"
    cell_c = tbl.cell(1, 0)
    cell_c.text = "Unidad: Inteligencia de Mercados & Asignación de Activos"
    cell_d = tbl.cell(1, 1)
    cell_d.text = "Certificado por: Altus AI Macro Engine"
    
    doc.add_paragraph()

    # Título Principal del Reporte
    h1 = doc.add_heading("Consenso Definitivo e Inteligencia de Mercado", level=1)
    h1.runs[0].font.color.rgb = RGBColor(16, 75, 60)
    h1.runs[0].font.size = Pt(18)

    # Procesar líneas de Markdown a párrafos Word
    lines = contenido_markdown.split('\n')
    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        if line_s.startswith("# "):
            h = doc.add_heading(line_s[2:], level=1)
            h.runs[0].font.color.rgb = RGBColor(10, 35, 66)
        elif line_s.startswith("## "):
            h = doc.add_heading(line_s[3:], level=2)
            h.runs[0].font.color.rgb = RGBColor(16, 75, 60)
        elif line_s.startswith("### "):
            h = doc.add_heading(line_s[4:], level=3)
            h.runs[0].font.color.rgb = RGBColor(30, 41, 59)
        elif line_s.startswith("- ") or line_s.startswith("* "):
            p = doc.add_paragraph(line_s[2:], style='List Bullet')
            p.paragraph_format.space_after = Pt(4)
        else:
            p = doc.add_paragraph(line_s)
            p.paragraph_format.space_after = Pt(6)

    doc.add_paragraph()

    # Aviso Legal / Disclaimer
    p_disc = doc.add_paragraph()
    p_disc.paragraph_format.space_before = Pt(14)
    run_disc_t = p_disc.add_run("Aviso Legal: ")
    run_disc_t.bold = True
    run_disc_t.font.size = Pt(8.5)
    run_disc_t.font.color.rgb = RGBColor(100, 116, 139)
    run_disc_b = p_disc.add_run(
        "Las visiones y proyecciones macroeconómicas presentadas en este documento han sido procesadas mediante inteligencia artificial (Altus AI) cruzando múltiples visiones institucionales. Este documento no constituye una recomendación de inversión vinculante, sino una herramienta de información estratégica. Los mercados son volátiles y las rentabilidades pasadas no garantizan retornos futuros. FV Asesorías e Inversiones limita su responsabilidad al análisis cuantitativo."
    )
    run_disc_b.font.size = Pt(8.5)
    run_disc_b.font.color.rgb = RGBColor(100, 116, 139)

    # Sobre FV Asesorías e Inversiones
    p_fv = doc.add_paragraph()
    p_fv.paragraph_format.space_before = Pt(10)
    run_fv_t = p_fv.add_run("Sobre FV Asesorías e Inversiones:\n")
    run_fv_t.bold = True
    run_fv_t.font.size = Pt(9)
    run_fv_t.font.color.rgb = RGBColor(212, 175, 55) # Altus Gold
    run_fv_b = p_fv.add_run(
        "FV Asesorías e Inversiones somos un Multi-Family Office Digital impulsado por nuestro software cuantitativo privado de Inteligencia Artificial (ALTUS AI). Combinamos la agilidad tecnológica de una WealthTech con la exclusividad de una oficina patrimonial privada, auditando en 360° la situación tributaria, inmobiliaria, composición familiar, seguros e inversiones para proteger su legado a través de las generaciones."
    )
    run_fv_b.font.size = Pt(9)
    run_fv_b.font.color.rgb = RGBColor(55, 65, 81)

    # Ciberseguridad & Resguardo Patrimonial
    p_sec = doc.add_paragraph()
    p_sec.paragraph_format.space_before = Pt(10)
    run_sec_t = p_sec.add_run("🔒 Ciberseguridad & Resguardo Patrimonial: ")
    run_sec_t.bold = True
    run_sec_t.font.size = Pt(8.5)
    run_sec_t.font.color.rgb = RGBColor(10, 35, 66)
    run_sec_b = p_sec.add_run(
        "Toda la información analizada por Altus AI se encuentra protegida bajo cifrado nativo AES-256 bits y transmisión TLS 1.3 de grado bancario. Garantizamos estricta confidencialidad bajo Secreto Patrimonial y cumplimiento riguroso de la Ley N° 19.628 de Protección de Datos Personales en Chile."
    )
    run_sec_b.font.size = Pt(8.5)
    run_sec_b.font.color.rgb = RGBColor(51, 65, 85)

    doc.save(output_path)
    return output_path

def generar_docx_reporte_360(data_360: dict, output_path: str):
    """
    Genera el Reporte Patrimonial 360 en formato Word (.docx).
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
    run_sub = title_p.add_run("DIGITAL FAMILY OFFICE ANALYTICS | FV ASESORÍAS & ALTUS AI\n")
    run_sub.font.size = Pt(8.5)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(10, 35, 66)
    
    run_date = title_p.add_run(f"Fecha de Emisión: {datetime.now().strftime('%d-%m-%Y')}\n")
    run_date.font.size = Pt(8)
    run_date.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph()

    # Título Principal del Reporte
    h1 = doc.add_heading("Reporte Patrimonial Consolidado 360°", level=1)
    h1.runs[0].font.color.rgb = RGBColor(16, 75, 60)
    h1.runs[0].font.size = Pt(18)
    
    rut_cliente = data_360.get('current_rut') or 'N/A'
    p_cliente = doc.add_paragraph()
    run_cliente = p_cliente.add_run(f"RUT Cliente: {rut_cliente}")
    run_cliente.font.bold = True
    
    doc.add_paragraph()

    # -------------------- TABLA 1: CARTERA INMOBILIARIA --------------------
    h2_inm = doc.add_heading("1. Cartera Inmobiliaria", level=2)
    h2_inm.runs[0].font.color.rgb = RGBColor(10, 35, 66)
    
    props = data_360.get('propiedades', [])
    if not props:
        p_info = doc.add_paragraph("Sin activos registrados")
        p_info.style = 'List Bullet'
    else:
        # Headers: Propiedad, Destino, Avalúo Fiscal, Valor Comercial, Arriendo, Dividendo, Gastos Operativos, Flujo Neto, Cap Rate
        t_props = doc.add_table(rows=1, cols=9)
        t_props.style = 'Table Grid'
        t_props.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_props.autofit = True
        
        hdr_cells = t_props.rows[0].cells
        headers = ["Propiedad", "Destino", "Avalúo Fiscal (Ref)", "Valor Com. (UF)", "Arriendo", "Dividendo", "Gastos Op.", "Flujo Neto", "Cap Rate"]
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            shading_elm = parse_xml(r'<w:shd {} w:fill="0A2342"/>'.format(nsdecls('w')))
            hdr_cells[i]._tc.get_or_add_tcPr().append(shading_elm)
            for paragraph in hdr_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(255, 255, 255)
            
        for p in props:
            row_cells = t_props.add_row().cells
            row_cells[0].text = str(p.get("nombre", ""))
            row_cells[1].text = str(p.get("destino", ""))
            row_cells[2].text = "N/A"
            row_cells[3].text = f"{p.get('valor_uf', 0):,.0f}"
            row_cells[4].text = f"${p.get('arriendo', 0):,.0f}"
            row_cells[5].text = f"${p.get('dividendo', 0):,.0f}"
            gastos = float(p.get('gastos_comunes', 0) or 0) + float(p.get('seguros', 0) or 0) + (float(p.get('contribuciones', 0) or 0) / 3)
            row_cells[6].text = f"${gastos:,.0f}"
            row_cells[7].text = f"${p.get('flujo_neto', 0):,.0f}"
            row_cells[8].text = f"{p.get('cap_rate', 0):.2f}%"
            
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(8)
                        
    doc.add_paragraph()

    # -------------------- TABLA 2: PORTAFOLIO DE INVERSIONES --------------------
    h2_inv = doc.add_heading("2. Portafolio de Inversiones", level=2)
    h2_inv.runs[0].font.color.rgb = RGBColor(10, 35, 66)
    
    invs = data_360.get('inversiones', [])
    if not invs:
        p_info = doc.add_paragraph("Sin activos registrados")
        p_info.style = 'List Bullet'
    else:
        # Headers: Institución, Activo, Clase, Riesgo, Moneda, Monto, TIR y Rentabilidad Acumulada
        t_inv = doc.add_table(rows=1, cols=8)
        t_inv.style = 'Table Grid'
        t_inv.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_inv.autofit = True
        
        hdr_cells = t_inv.rows[0].cells
        headers = ["Institución", "Activo", "Clase", "Riesgo", "Moneda", "Monto", "TIR (%)", "Rent. Acum (%)"]
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            shading_elm = parse_xml(r'<w:shd {} w:fill="0A2342"/>'.format(nsdecls('w')))
            hdr_cells[i]._tc.get_or_add_tcPr().append(shading_elm)
            for paragraph in hdr_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    
        for inv in invs:
            row_cells = t_inv.add_row().cells
            row_cells[0].text = str(inv.get("nombre", ""))
            row_cells[1].text = str(inv.get("nombre", "")) # Repetimos ya que en web es el mismo campo
            row_cells[2].text = str(inv.get("tipo", ""))
            row_cells[3].text = str(inv.get("riesgo", ""))
            row_cells[4].text = str(inv.get("moneda", ""))
            row_cells[5].text = f"${inv.get('monto', 0):,.0f}"
            row_cells[6].text = f"{inv.get('tir', 0)}%"
            row_cells[7].text = f"{inv.get('rentabilidad', 0)}%"
            
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(8)
                        
    doc.add_paragraph()

    # -------------------- TABLA 3: FLUJO SUCESORIO --------------------
    h2_flujo = doc.add_heading("3. Flujo de Caja Sucesorio y Mantenimiento", level=2)
    h2_flujo.runs[0].font.color.rgb = RGBColor(10, 35, 66)
    
    flujo = data_360.get('flujo_sucesorio')
    if not flujo:
        p_info = doc.add_paragraph("Sin activos registrados")
        p_info.style = 'List Bullet'
    else:
        t_flujo = doc.add_table(rows=1, cols=3)
        t_flujo.style = 'Table Grid'
        t_flujo.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_flujo.autofit = True
        
        hdr_cells = t_flujo.rows[0].cells
        headers = ["Concepto", "Mensual", "Anual"]
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            shading_elm = parse_xml(r'<w:shd {} w:fill="0A2342"/>'.format(nsdecls('w')))
            hdr_cells[i]._tc.get_or_add_tcPr().append(shading_elm)
            for paragraph in hdr_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    
        items = [
            ("Gastos de Vida y Familia", flujo.get('gastos_vida', 0)),
            ("Sueldos y Servicios Domésticos", flujo.get('sueldos', 0)),
            ("Compromisos Fijos de Activos", flujo.get('compromisos', 0)),
            ("Seguros Generales y de Vida", flujo.get('seguros', 0))
        ]
        
        total_mensual = 0
        for desc, val in items:
            val = val or 0
            row_cells = t_flujo.add_row().cells
            row_cells[0].text = desc
            row_cells[1].text = f"${val:,.0f}"
            row_cells[2].text = f"${val * 12:,.0f}"
            total_mensual += val
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        
        row_cells = t_flujo.add_row().cells
        row_cells[0].text = "Total Gastos Estimados"
        row_cells[1].text = f"${total_mensual:,.0f}"
        row_cells[2].text = f"${total_mensual * 12:,.0f}"
        for cell in row_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(9)
                    
        ingresos_pasivos = flujo.get('ingresos_pasivos', 0)
        row_cells = t_flujo.add_row().cells
        row_cells[0].text = "Ingresos Pasivos Proyectados"
        row_cells[1].text = f"${ingresos_pasivos:,.0f}"
        row_cells[2].text = f"${ingresos_pasivos * 12:,.0f}"
        for cell in row_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9)
                    
        flujo_neto = ingresos_pasivos - total_mensual
        row_cells = t_flujo.add_row().cells
        row_cells[0].text = "FLUJO NETO"
        row_cells[1].text = f"${flujo_neto:,.0f}"
        row_cells[2].text = f"${flujo_neto * 12:,.0f}"
        for cell in row_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(9)
                    
        # Brecha Sucesoria
        doc.add_paragraph()
        if flujo_neto < 0:
            brecha = abs(flujo_neto * 12) / 0.04
            p_brecha = doc.add_paragraph()
            run_brecha = p_brecha.add_run(f"Brecha Patrimonial Sucesoria al 4%: ${brecha:,.0f}")
            run_brecha.font.bold = True
            run_brecha.font.color.rgb = RGBColor(185, 28, 28)
        else:
            p_brecha = doc.add_paragraph()
            run_brecha = p_brecha.add_run("Brecha Patrimonial Sucesoria: Cubierta (Superávit)")
            run_brecha.font.bold = True
            run_brecha.font.color.rgb = RGBColor(4, 120, 87)

    doc.add_paragraph()
    
    # -------------------- TABLA 4: OPTIMIZACIÓN TRIBUTARIA --------------------
    hipo = data_360.get('intereses_hipotecarios', 0)
    edu = data_360.get('gastos_educacion', 0)
    ret2cat = data_360.get('retenciones_2da_cat', 0)
    
    if hipo > 0 or edu > 0 or ret2cat > 0:
        h2_trib = doc.add_heading("4. Optimización Tributaria y Fuga Fiscal", level=2)
        h2_trib.runs[0].font.color.rgb = RGBColor(10, 35, 66)
        
        t_trib = doc.add_table(rows=1, cols=3)
        t_trib.style = 'Table Grid'
        t_trib.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_trib.autofit = True
        
        hdr_cells = t_trib.rows[0].cells
        headers = ["Beneficio Tributario Detectado", "Monto Anual (CLP)", "Impacto en Liquidez"]
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            shading_elm = parse_xml(r'<w:shd {} w:fill="0A2342"/>'.format(nsdecls('w')))
            hdr_cells[i]._tc.get_or_add_tcPr().append(shading_elm)
            for paragraph in hdr_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    
        if hipo > 0:
            row_cells = t_trib.add_row().cells
            row_cells[0].text = "Rebaja Intereses Hipotecarios (Art. 55 bis)"
            row_cells[1].text = f"${hipo:,.0f}"
            row_cells[2].text = "Deducción Directa de la Base Imponible"
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        
        if edu > 0:
            row_cells = t_trib.add_row().cells
            row_cells[0].text = "Crédito por Gasto Educación (Art. 55 ter)"
            row_cells[1].text = f"${edu:,.0f}"
            row_cells[2].text = "Crédito Directo contra IGC"
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        
        if ret2cat > 0:
            row_cells = t_trib.add_row().cells
            row_cells[0].text = "Retenciones Honorarios (2da Categoría)"
            row_cells[1].text = f"${ret2cat:,.0f}"
            row_cells[2].text = "Devolución Anticipada o Crédito"
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        
        p_note = doc.add_paragraph("* La devolución fiscal recuperable dependerá del Tramo Marginal de IGC del contribuyente (simulable en Altus AI).")
        p_note.runs[0].font.size = Pt(8)
        p_note.runs[0].font.italic = True
        
        doc.add_paragraph()
        
    # -------------------- TABLA 5: AUDITORÍA PATRIMONIAL DE SEGUROS --------------------
    if data_360.get("audit_seguros") and data_360["audit_seguros"].get("polizas"):
        ad = data_360["audit_seguros"]
        h2_audit = doc.add_heading("5. Auditoría Patrimonial de Seguros", level=2)
        h2_audit.runs[0].font.color.rgb = RGBColor(10, 35, 66)
        
        # 5.1 Desglose de Pólizas
        h3_desglose = doc.add_heading("5.1 Desglose y Clasificación de Pólizas", level=3)
        h3_desglose.runs[0].font.color.rgb = RGBColor(10, 35, 66)
        h3_desglose.runs[0].font.size = Pt(11)
        
        t_pol = doc.add_table(rows=1, cols=4)
        t_pol.style = 'Table Grid'
        t_pol.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_pol.autofit = True
        
        hdr_cells_pol = t_pol.rows[0].cells
        headers_pol = ["Compañía", "Contratante", "Tipo de Cobertura", "Destino del Beneficio"]
        for i, h in enumerate(headers_pol):
            hdr_cells_pol[i].text = h
            shading_elm = parse_xml(r'<w:shd {} w:fill="0A2342"/>'.format(nsdecls('w')))
            hdr_cells_pol[i]._tc.get_or_add_tcPr().append(shading_elm)
            for paragraph in hdr_cells_pol[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    
        for p in ad["polizas"]:
            row_cells = t_pol.add_row().cells
            row_cells[0].text = p.get('compania', 'N/A')
            row_cells[1].text = p.get('contratante', 'N/A')
            row_cells[2].text = p.get('tipo', 'N/A')
            row_cells[3].text = p.get('destino_beneficio', 'N/A')
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(8.5)
                        
        doc.add_paragraph()
        
        # 5.2 Resumen Financiero y Brecha
        h3_brecha = doc.add_heading("5.2 Resumen Financiero y Brecha Sucesoria", level=3)
        h3_brecha.runs[0].font.color.rgb = RGBColor(10, 35, 66)
        h3_brecha.runs[0].font.size = Pt(11)

        t_audit = doc.add_table(rows=1, cols=2)
        t_audit.style = 'Table Grid'
        t_audit.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_audit.autofit = True
        
        hdr_cells = t_audit.rows[0].cells
        headers = ["Métrica Sucesoria", "Monto (UF)"]
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            shading_elm = parse_xml(r'<w:shd {} w:fill="0A2342"/>'.format(nsdecls('w')))
            hdr_cells[i]._tc.get_or_add_tcPr().append(shading_elm)
            for paragraph in hdr_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    
        items_audit = [
            ("Capital Vida Total (Bruto)", f"{ad['capital_vida_total_uf']:,.0f} UF"),
            ("Deuda Hipotecaria Total", f"{ad['deuda_total_uf']:,.0f} UF"),
            ("Capital Líquido Familiar (Real)", f"{ad['liquidez_familiar_uf']:,.0f} UF"),
            ("Brecha Sucesoria Proyectada (4%)", f"{ad['brecha_sucesoria_uf']:,.0f} UF")
        ]
        
        for desc, val in items_audit:
            row_cells = t_audit.add_row().cells
            row_cells[0].text = desc
            row_cells[1].text = val
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        
        deficit_lbl = "Déficit Patrimonial / Descalce" if ad["tiene_deficit"] else "Superávit de Protección"
        row_cells = t_audit.add_row().cells
        row_cells[0].text = deficit_lbl
        row_cells[1].text = f"{ad['deficit_sucesorio_uf']:,.0f} UF"
        for cell in row_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(9)
                    if ad["tiene_deficit"] and cell == row_cells[1]:
                        run.font.color.rgb = RGBColor(185, 28, 28)
                    elif not ad["tiene_deficit"] and cell == row_cells[1]:
                        run.font.color.rgb = RGBColor(4, 120, 87)
                        
        doc.add_paragraph()
        
        if ad["tiene_deficit"] or ad["liquidez_familiar_uf"] == 0:
            p_diag = doc.add_paragraph(f"Riesgo de Liquidez Sucesoria: {ad['diag_proteccion']}")
            p_diag.runs[0].font.bold = True
            p_diag.runs[0].font.color.rgb = RGBColor(185, 28, 28) # Rojo
        else:
            p_diag = doc.add_paragraph(f"Protección Familiar: {ad['diag_proteccion']}")
            p_diag.runs[0].font.bold = True
            p_diag.runs[0].font.color.rgb = RGBColor(4, 120, 87) # Verde

        if ad.get('diag_duplicidad') and "No se detecta" not in ad['diag_duplicidad']:
            p_dup = doc.add_paragraph(f"Duplicidad y Dispersión: {ad['diag_duplicidad']}")
            p_dup.runs[0].font.bold = True
            p_dup.runs[0].font.color.rgb = RGBColor(204, 153, 0) # Amarillo oscuro
                        
        p_dict = doc.add_paragraph(f"Propuesta de Canje y Reestructuración con PRINCIPAL: {ad['dictamen']}")
        p_dict.runs[0].font.bold = True
        p_dict.runs[0].font.size = Pt(9)
        p_dict.runs[0].font.color.rgb = RGBColor(10, 35, 66)
        
        doc.add_paragraph()
    
    # Ciberseguridad & Resguardo Patrimonial
    p_sec = doc.add_paragraph()
    p_sec.paragraph_format.space_before = Pt(10)
    run_sec_t = p_sec.add_run("🔒 Ciberseguridad & Resguardo Patrimonial: ")
    run_sec_t.bold = True
    run_sec_t.font.size = Pt(8.5)
    run_sec_t.font.color.rgb = RGBColor(10, 35, 66)
    run_sec_b = p_sec.add_run(
        "Toda la información analizada por Altus AI se encuentra protegida bajo cifrado nativo AES-256 bits y transmisión TLS 1.3 de grado bancario. Garantizamos estricta confidencialidad bajo Secreto Patrimonial y cumplimiento riguroso de la Ley N° 19.628 de Protección de Datos Personales en Chile."
    )
    run_sec_b.font.size = Pt(8.5)
    run_sec_b.font.color.rgb = RGBColor(51, 65, 85)
    
    doc.save(output_path)
    return output_path
