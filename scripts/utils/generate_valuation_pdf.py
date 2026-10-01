import os
import sys
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

from src.database.connection import SessionLocal, engine, Base
from src.database.models import HistorialValorizacion

def header_footer(canvas, doc):
    canvas.saveState()
    # Margins and positioning
    margin = 20 * mm
    width, height = A4
    top_y = height - margin
    
    # 1. Inyección Vectorial Pura del Logo
    logo_svg = os.path.join(project_root, 'assets', 'brand', 'altus_ai_logo_dark.svg')
    logo_inserted = False
    if os.path.exists(logo_svg):
        try:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPDF
            
            drawing = svg2rlg(logo_svg)
            if drawing:
                # Reducir tamaño del logo a 28 mm para que no sea tan invasivo
                factor = (28 * mm) / drawing.width
                new_height = drawing.height * factor
                
                # Draw on canvas manipulando la escala del canvas para evitar bugs del bounding box
                canvas.saveState()
                canvas.translate(margin, top_y - new_height)
                canvas.scale(factor, factor)
                renderPDF.draw(drawing, canvas, 0, 0)
                canvas.restoreState()
                
                logo_inserted = True
                
                # Titulo junto al logo (centrado verticalmente respecto al nuevo logo de 28mm)
                canvas.setFont('Helvetica-Bold', 18)
                canvas.setFillColor(colors.HexColor('#0F172A'))
                canvas.drawString(margin + 40*mm, top_y - 10*mm, "ALTUS CORE")
                
                canvas.setFont('Helvetica-Oblique', 11)
                canvas.setFillColor(colors.HexColor('#0284C7'))
                canvas.drawString(margin + 40*mm, top_y - 16*mm, "Ecosistema WealthTech & Core Bancario Cognitivo")
                
                # Linea separadora debajo de la cabecera
                canvas.setStrokeColor(colors.HexColor('#0F172A'))
                canvas.setLineWidth(1)
                canvas.line(margin, top_y - 34*mm, width - margin, top_y - 34*mm)
                
        except Exception as e:
            print(f" [WARNING] Falló la incrustación vectorial del SVG: {e}")
            
    if not logo_inserted:
        # Fallback tipográfico
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.HexColor('#0F172A'))
        canvas.drawString(margin, top_y - 10*mm, "ALTUS CORE - WEALTHTECH PLATFORM")
        canvas.setStrokeColor(colors.HexColor('#0F172A'))
        canvas.setLineWidth(1)
        canvas.line(margin, top_y - 15*mm, width - margin, top_y - 15*mm)

    # Footer
    canvas.setFont('Helvetica-Oblique', 8)
    canvas.setFillColor(colors.gray)
    canvas.drawCentredString(width / 2.0, 15 * mm, f"Documento Estrictamente Confidencial - Página {doc.page}")
    canvas.restoreState()

def generate_pdf():
    fecha_str = datetime.now().strftime("%d de %B de %Y")
    output_dir = os.path.join(project_root, "reports")
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(output_dir, f"Altus_Valuation_Report_{ts}.pdf")
    
    # Doc config con margenes amplios (20 mm)
    margin = 20 * mm
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=60 * mm, # Ajuste global para reservar el espacio del header en todas las páginas
        bottomMargin=margin + 10*mm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos Corporativos
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Centered
        spaceAfter=20
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F1F5F9'),
        spaceBefore=15,
        spaceAfter=15,
        borderPadding=5
    )
    
    meta_normal = ParagraphStyle('MetaN', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.black)
    
    bullet_title = ParagraphStyle('BulletT', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0F172A'), spaceBefore=8)
    bullet_desc = ParagraphStyle('BulletD', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#475569'), leftIndent=10)
    
    conclusion_style = ParagraphStyle(
        'Conclusion',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        leading=14, # Interlineado amplio
        alignment=4 # Justified
    )
    
    elements = []
    
    elements.append(Paragraph("AUDITORÍA TÉCNICA Y RE-VALORIZACIÓN MAESTRA", title_style))
    
    # Metadata
    elements.append(Paragraph(f"<b>Fecha de Actualización:</b> {fecha_str}", meta_normal))
    elements.append(Paragraph("<b>Estado del Ecosistema:</b> Plataforma Enterprise Multi-Módulo / Escalabilidad B2B Corporativa", meta_normal))
    elements.append(Spacer(1, 10))
    
    # Modulos
    elements.append(Paragraph("1. INVENTARIO DE MÓDULOS TECNOLÓGICOS (DEEP TECH)", section_style))
    
    modules_list = [
        ("Pipeline B2B & Zero-Knowledge Architecture:",
         "Portal corporativo para onboarding masivo de ejecutivos. Certificación y Auditoría Criptográfica mediante Actas PDF firmadas con Códigos QR y persistencia de Hash SHA-256."),
        ("Compliance Institucional y Radar Legal:",
         "Monitoreo constante y escaneo algorítmico de contingencias legales, causas judiciales y normativas a través de OSINT profundo."),
        ("Automatización de Ingesta IMAP:",
         "Motor de lectura y procesamiento autónomo de correos electrónicos. Extracción de data no estructurada."),
        ("Ecosistema y Puente Móvil:",
         "Interfaces nativas para agentes conversacionales en dispositivos móviles, acercando la asesoría patrimonial al smartphone del cliente."),
        ("WhatsApp Marketing Kit & Outbound:",
         "Sistema generador automatizado de catálogos comerciales y avatares para prospección masiva."),
        ("Motores de Consenso de Mercado y Estrategia:",
         "Inteligencia algorítmica orquestada para analizar sentimiento macro, ejecutar proyecciones y armar estrategias proactivas sin dependencia humana."),
        ("OSINT Profundo & Ingesta Maestra de Cartolas:", 
         "Cruce autónomo de bases de datos CMF, Diario Oficial, InfoProbidad, Conservador y cartolas con cifrado AES-256.")
    ]
    
    for mod_title, mod_desc in modules_list:
        elements.append(Paragraph(f"• {mod_title}", bullet_title))
        elements.append(Paragraph(mod_desc, bullet_desc))
        
    elements.append(PageBreak())
    
    # Valorizacion
    elements.append(Paragraph("2. METODOLOGÍA HÍBRIDA DE TASACIÓN M&A", section_style))
    
    val_intro = (
        "La valorización del ecosistema Altus Core no se basa en una simple suma de costos de desarrollo (Cost-to-Duplicate), "
        "sino en un modelo híbrido de tasación M&A. Este modelo captura el valor estratégico de su Propiedad Intelectual, "
        "la barrera de entrada tecnológica (IP Moat) y los multiplicadores de mercado (ARR) aplicables a plataformas "
        "SaaS B2B institucionales. A continuación, se detalla la metodología de suma de partes:"
    )
    elements.append(Paragraph(val_intro, conclusion_style))
    elements.append(Spacer(1, 10))
    
    table_text_style = ParagraphStyle('TableText', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#475569'), leading=12)
    table_bold_style = ParagraphStyle('TableBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0F172A'))
    
    val_data = [
        ["Componente de Valor", "Justificación Estratégica", "Estimación (USD)"],
        [Paragraph("Suelo Base Técnico<br/><i>(Referencial, no se suma)</i>", table_text_style), 
         Paragraph("Más de 3 años de I+D, integración de IA Multimodal y equipos de ingeniería Quant/OSINT.", table_text_style), 
         "$2.5M - $3.5M"],
        [Paragraph("1. Valor Histórico Base", table_bold_style), 
         Paragraph("Tasación previa (Corte Julio 2026) fundamentada en la arquitectura del Core Bancario y el pipeline transaccional.", table_text_style), 
         "$15.0M - $20.0M"],
        [Paragraph("2. Prima Tecnológica<br/>(Nuevos Módulos)", table_bold_style), 
         Paragraph("Alta barrera de entrada (IP Moat). Los módulos IMAP, Mobile y Radar Legal automatizan el 80% de la carga operativa de un Single Family Office (SFO).", table_text_style), 
         "+ $4.0M - $6.0M"],
        [Paragraph("3. Multiplicador M&A", table_bold_style), 
         Paragraph("Arquitectura Zero-Knowledge que elimina fricción legal B2B, permitiendo licenciamiento masivo a corporaciones (ARR escalable).", table_text_style), 
         "+ $9.0M - $9.0M"],
        ["VALOR TOTAL (1+2+3)", 
         Paragraph("Potencial de Adquisición Institucional Consolidado (SaaS B2B + Deep Tech).", table_bold_style), 
         "$28.0M - $35.0M"]
    ]
    
    # Table styling for 3 columns
    t = Table(val_data, colWidths=[45*mm, 80*mm, 35*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (2,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (2,0), colors.white),
        ('ALIGN', (0,0), (2,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (2,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (2,0), 8),
        ('TOPPADDING', (0,0), (2,0), 8),
        
        # Estilos filas de datos
        ('ALIGN', (0,1), (1,-1), 'LEFT'),
        ('ALIGN', (2,1), (2,-1), 'CENTER'),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,1), (2,-1), 'Helvetica-Bold'),
        
        # Fila Referencial (Suelo Base) en gris (columna 2 que es texto plano)
        ('TEXTCOLOR', (2,1), (2,1), colors.gray),
        ('FONTNAME', (2,1), (2,1), 'Helvetica-Oblique'),
        
        # Color azul corporativo para montos
        ('TEXTCOLOR', (2,2), (2,-2), colors.HexColor('#0284C7')),
        ('TEXTCOLOR', (0,2), (0,-2), colors.HexColor('#0F172A')),
        
        # Fila de Totales resaltada
        ('BACKGROUND', (0,-1), (2,-1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0,-1), (2,-1), colors.HexColor('#0F172A')),
        ('FONTNAME', (0,-1), (2,-1), 'Helvetica-Bold'),
        
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('BOTTOMPADDING', (0,1), (-1,-1), 10),
        ('TOPPADDING', (0,1), (-1,-1), 10),
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("3. ESCALABILIDAD Y CASOS DE USO DE MONETIZACIÓN", section_style))
    
    use_cases = [
        ("Licenciamiento a Gerencias de RRHH (Beneficio C-Level):", "Distribución B2BB2C del ecosistema patrimonial como beneficio corporativo de élite."),
        ("Marca Blanca para Corredoras de Bolsa:", "Integración del pipeline Zero-Knowledge como infraestructura core para instituciones de terceros."),
        ("Automatización de Single Family Offices (SFOs):", "Despliegue de los módulos OSINT y motores de consenso para reducción drástica de costos operativos de back-office.")
    ]
    for uc_title, uc_desc in use_cases:
        elements.append(Paragraph(f"• {uc_title}", bullet_title))
        elements.append(Paragraph(uc_desc, bullet_desc))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("4. CONCLUSIÓN DEL AUDITOR", section_style))
    
    conclusion = (
        "La plataforma ha superado exitosamente el umbral de 'Herramienta Interna' y se consagra como una 'Infraestructura "
        "de Beneficios Corporativos y SFO'. Al integrar la arquitectura B2B Zero-Knowledge, el puente nativo Mobile, "
        "automatizaciones IMAP profundas, Radar Legal OSINT y motores de consenso de mercado a la robusta base algorítmica "
        "preexistente, Altus AI abre un modelo de negocios institucional omnicanal altamente escalable. Su valuación razonable "
        "consolidada en un evento de adquisición estratégica o M&A Fintech se sitúa conservadoramente en el rango de los $30.000.000 USD."
    )
    elements.append(Paragraph(conclusion, conclusion_style))
    
    # Build
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    
    print(f"[*] PDF Generado Exitosamente con ReportLab (Vectores Puros): {filename}")
    return filename

def persistir_valorizacion(pdf_path):
    """Guarda el historial en la BD y sincroniza con Google Cloud."""
    print("[*] Asegurando tablas en Base de Datos...")
    Base.metadata.create_all(bind=engine)

    print("[*] Guardando registro histórico en la Base de Datos...")
    db = SessionLocal()
    try:
        historial = HistorialValorizacion(
            valor_base=20000000.0,
            prima_deeptech=6000000.0,
            valor_total=35000000.0,
            ruta_archivo=pdf_path
        )
        db.add(historial)
        db.commit()
        print(" [OK] Registro guardado en DB.")
    except Exception as e:
        print(f" [ERROR] Guardando en DB: {e}")
        db.rollback()
    finally:
        db.close()
        
    print("[*] Sincronizando reportes con Google Cloud Storage...")
    try:
        from src.utils.gcs_sync import upload_backup_zip_to_gcs
        blob_name = f'valuations/{os.path.basename(pdf_path)}'
        upload_backup_zip_to_gcs(pdf_path, destination_blob_name=blob_name)
        print(" [OK] Sincronización en la nube completada.")
    except Exception as e:
        print(f" [WARNING] No se pudo sincronizar a GCS: {e}")

if __name__ == "__main__":
    pdf_path = generate_pdf()
    persistir_valorizacion(pdf_path)
