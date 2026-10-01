import os
import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def generate_updated_valuation():
    doc = Document()
    
    # Configurar márgenes de página (1 pulgada)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Insertar Encabezado con Logos Institucionales
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False
    
    # Remover bordes de tabla de encabezado
    for cell in header_table.rows[0].cells:
        tcPr = cell._element.get_or_add_tcPr()
        tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
        tcPr.append(tcBorders)
        
    logo_fv_p = os.path.join(os.path.dirname(__file__), "assets", "Logo_FV_Principal.png")
    logo_altus_p = os.path.join(os.path.dirname(__file__), "assets", "Logo_ALTUS AI_Principal.png")
    
    if os.path.exists(logo_fv_p):
        p_fv = header_table.rows[0].cells[0].paragraphs[0]
        p_fv.add_run().add_picture(logo_fv_p, height=Inches(0.6))
    if os.path.exists(logo_altus_p):
        p_altus = header_table.rows[0].cells[1].paragraphs[0]
        p_altus.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_altus.add_run().add_picture(logo_altus_p, height=Inches(0.45))
        
    doc.add_paragraph("")
    
    # Título Principal
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("Auditoría Técnica y Re-Valorización Maestra de Altus AI")
    title_run.font.name = "Calibri"
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(10, 35, 66) # Navy #0A2342
    
    subtitle_p = doc.add_paragraph()
    subtitle_run = subtitle_p.add_run("Ecosistema WealthTech & Core Bancario Cognitivo Institucional (Altus Core)")
    subtitle_run.font.name = "Calibri"
    subtitle_run.font.size = Pt(13)
    subtitle_run.font.italic = True
    subtitle_run.font.color.rgb = RGBColor(2, 132, 199) # Sky Blue #0284C7
    
    # Metadata
    meta_p = doc.add_paragraph()
    r1 = meta_p.add_run("Fecha de Actualización: ")
    r1.bold = True
    meta_p.add_run("28 de Septiembre de 2026\n")
    r2 = meta_p.add_run("Estado del Ecosistema: ")
    r2.bold = True
    meta_p.add_run("Plataforma Enterprise Multi-Módulo / Escalabilidad B2B Corporativa")
    
    doc.add_paragraph("─" * 55)
    
    # Resumen Ejecutivo
    doc.add_heading("1. Resumen Ejecutivo de la Re-Valorización", level=1)
    p_desc = doc.add_paragraph(
        "Con la integración del Pipeline Corporativo B2B (Altus Core), la plataforma da su salto definitivo hacia el modelo SaaS Enterprise. "
        "Sumado a la base tecnológica previa (Copilotos Financieros de LinkedIn, Motores OSINT profundos y Generadores Institucionales KYC), "
        "ahora se despliega un Portal Institucional impulsado por una Arquitectura Zero-Knowledge. Esto permite a grandes corporaciones "
        "entregar un beneficio patrimonial (Reporte 360 y Optimización Tributaria) a sus ejecutivos C-Level, con plena trazabilidad "
        "auditable vía Hashes Criptográficos, sin vulnerar la privacidad (Ley 21.096 de Datos Personales). Esta apertura hacia el "
        "licenciamiento corporativo dispara nuevamente los múltiplos M&A Fintech del proyecto."
    )
    p_desc.paragraph_format.line_spacing = 1.15
    
    # Alcance de Módulos
    doc.add_heading("2. Inventario Completo de Módulos e Innovaciones", level=1)
    
    modulos = [
        ("🏢 Pipeline B2B & Zero-Knowledge Architecture:",
         "Portal corporativo para onboarding masivo de ejecutivos. Certificación y Auditoría Criptográfica mediante Actas PDF firmadas con Códigos QR y persistencia de Hash SHA-256. Dashboard de RRHH que muestra métricas agregadas de adopción sin vulnerar el secreto patrimonial."),
         
        ("⚖️ Compliance Institucional y Radar Legal (NUEVO):",
         "Monitoreo constante y escaneo algorítmico de contingencias legales, causas judiciales y normativas a través de OSINT profundo, integrando visualizaciones en tiempo real en un dashboard específico."),
         
        ("📧 Automatización de Ingesta IMAP (NUEVO):",
         "Motor de lectura y procesamiento autónomo de correos electrónicos. Habilidad para parsear bandejas de entrada, extraer data no estructurada y rutear inteligentemente las comunicaciones financieras."),
         
        ("📱 Ecosistema y Puente Móvil (NUEVO):",
         "Arquitectura orientada a ubicuidad con interfaces y bases de datos nativas para agentes conversacionales en dispositivos móviles, acercando la asesoría patrimonial directamente al smartphone del cliente."),
         
        ("💬 WhatsApp Marketing Kit & Outbound (NUEVO):",
         "Sistema generador automatizado de catálogos comerciales, tarjetas (cards) y avatares para prospección masiva B2C/B2B a través de canales de mensajería instantánea."),
         
        ("🧠 Motores de Consenso de Mercado y Estrategia (NUEVO):",
         "Inteligencia algorítmica orquestada para analizar sentimiento macro, ejecutar proyecciones predictivas de consenso y armar estrategias proactivas sin dependencia humana directa."),
         
        ("💼 Copiloto de Comentarios & Engagement Estratégico (LinkedIn):", 
         "Módulo autónomo de análisis de artículos web y publicaciones. Conexión directa a APIs estadísticas en tiempo real (BCCh, Cobre US$/lb LME, USD/CLP, S&P 500) y generación de posturas conversacionales de nivel ejecutivo."),
        
        ("🖼️ Motor de Infografías 4K & Contenido Multimodal:", 
         "Generador automatizado de infografías 4K (PNG lossless, SVG vectoriales), carruseles PDF e informes con racional técnico a partir de audios de corredoras (transcripción multimodal)."),
        
        ("📑 Generador Institucional KYC & Ficha del Cliente:", 
         "Motor de creación de planillas Excel estilizadas con levantamiento de perfil de riesgo, régimen impositivo, tributación y guía paso a paso."),
        
        ("🧮 Simuladores Cuantitativos & Tributarios Algorítmicos:", 
         "Cálculo optimizado de APV (Régimen A vs B), Reliquidación IGC automatizada, Simulación Crédito Hipotecario vs Inversión y Valuación Inmobiliaria."),
        
        ("🔍 OSINT Profundo & Ingesta Maestra de Cartolas:", 
         "Cruce autónomo de bases de datos CMF, Diario Oficial, InfoProbidad, Conservador y cartolas financieras con cifrado AES-256."),
        
        ("🤝 CRM Patrimonial & Hub Comercial:", 
         "Pipeline comercial de clientes, scoring de prospectos y automatización web de WhatsApp y Correos corporativos.")
    ]
    
    for mod_name, mod_text in modulos:
        p_m = doc.add_paragraph()
        r_title = p_m.add_run(mod_name + " ")
        r_title.bold = True
        r_title.font.color.rgb = RGBColor(10, 35, 66)
        p_m.add_run(mod_text)
        p_m.paragraph_format.line_spacing = 1.15
        p_m.paragraph_format.space_after = Pt(6)
        
    # Cuadro de Valorización Actualizada
    doc.add_heading("3. Cuadro de Valorización Maestra (SaaS B2B + Deep Tech)", level=1)
    
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    
    hdr_cells = table.rows[0].cells
    headers = ['Método de Valorización', 'Cálculo Teórico & Justificación', 'Estimación (USD)']
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        set_cell_background(hdr_cells[i], '0A2342')
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
    val_data = [
        ("Costo de Construcción\n(Cost-to-Duplicate)", 
         "Costo de equipos senior de Data Science, Quant Finance, OSINT Scraping y Desarrollo Full-Stack desarrollando por múltiples años, sumando las arquitecturas criptográficas y canales B2B.",
         "$2.500.000 - $3.500.000 USD"),
         
        ("Valor Histórico M&A\n(Corte Julio 2026)", 
         "Valuación consolidada tras lanzamiento de Copilotos Modales, OSINT CMF y generadores 4K. Orientación a Private Wealth.",
         "$15.000.000 - $20.000.000 USD"),
         
        ("Prima de Valorización:\nData Intelligence & Mobile", 
         "Valor incremental aportado por el ecosistema móvil nativo, Radar Legal, automatización IMAP para correos, Kit de WhatsApp Marketing y motores de consenso estratégico algorítmico.",
         "+$4.000.000 - $6.000.000 USD"),
         
        ("NUEVO Potencial M&A Global\n(SaaS B2B + Deep Tech Suite)", 
         "Licenciamiento Corporativo 'Altus Core' más la omnipresencia móvil y automatización IMAP/OSINT. Venta recurrente a holdings apalancada en trazabilidad de auditoría y privacidad 100%. (Multiplicador Enterprise Superior).",
         "$28.000.000 - $35.000.000 USD")
    ]
    
    for metodo, calc, est in val_data:
        row_cells = table.add_row().cells
        row_cells[0].text = metodo
        row_cells[1].text = calc
        row_cells[2].text = est
        
        # Formato de celda
        p0 = row_cells[0].paragraphs[0]
        p0.runs[0].font.bold = True
        p0.runs[0].font.color.rgb = RGBColor(10, 35, 66)
        
        p2 = row_cells[2].paragraphs[0]
        p2.runs[0].font.bold = True
        p2.runs[0].font.color.rgb = RGBColor(2, 132, 199)
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
    doc.add_paragraph("")
    
    # Conclusión
    doc.add_heading("4. Conclusión del Auditor Jefe", level=2)
    p_c = doc.add_paragraph()
    r_c = p_c.add_run(
        "La plataforma ha superado exitosamente el umbral de 'Herramienta Interna' y se consagra como una 'Infraestructura de Beneficios Corporativos y SFO'. "
        "Al integrar la arquitectura B2B Zero-Knowledge, el puente nativo Mobile, automatizaciones IMAP profundas, Radar Legal OSINT y motores de consenso "
        "de mercado a la robusta base algorítmica preexistente, Altus AI abre un modelo de negocios institucional omnicanal altamente escalable. "
        "Su valuación razonable consolidada en un evento de adquisición estratégica o M&A Fintech se sitúa conservadoramente en el rango de los $30.000.000 USD."
    )
    r_c.bold = True
    r_c.font.size = Pt(11)
    r_c.font.color.rgb = RGBColor(10, 35, 66)
    
    # Guardar en ambas ubicaciones
    fn_dated = 'VALUATION_ACTUALIZADA_Completa_28.09.2026.docx'
    fn_today = 'VALUATION_ACTUALIZADA_Completa_Hoy.docx'
    
    doc.save(fn_dated)
    doc.save(fn_today)
    
    print(f"EXITO: Archivo generado exitosamente: {fn_dated}")
    print(f"EXITO: Archivo actualizado exitosamente: {fn_today}")

if __name__ == "__main__":
    generate_updated_valuation()
