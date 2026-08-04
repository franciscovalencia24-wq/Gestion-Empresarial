import os
import io
import base64
from datetime import datetime
from xhtml2pdf import pisa
import markdown

def _parse_md_tables_to_html(md_text):
    lines = md_text.split('\n')
    in_table = False
    html_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            parts = [p.strip() for p in stripped.split('|')[1:-1]]
            if all(set(p) <= set(':- ') for p in parts if p):
                continue
            if not in_table:
                in_table = True
                html_lines.append('<table style="width:100%; border-collapse:collapse; margin:10px 0 14px 0; font-size:9pt; page-break-inside:avoid;"><thead><tr style="background-color:#0A2342; color:#ffffff;">')
                for h in parts:
                    html_lines.append(f'<th style="padding:6px 8px; border:1px solid #cbd5e1; text-align:left; font-weight:bold;">{h}</th>')
                html_lines.append('</tr></thead><tbody>')
            else:
                html_lines.append('<tr style="page-break-inside:avoid;">')
                for c in parts:
                    html_lines.append(f'<td style="padding:5px 8px; border:1px solid #cbd5e1; text-align:left; vertical-align:top;">{c}</td>')
                html_lines.append('</tr>')
        else:
            if in_table:
                in_table = False
                html_lines.append('</tbody></table>')
            html_lines.append(line)
            
    if in_table:
        html_lines.append('</tbody></table>')
        
    return '\n'.join(html_lines)

def generate_macro_pdf(cliente_nombre: str, contenido_markdown: str, output_path: str):
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Logos vectoriales / HD de marca oficial
    from src.utils.pdf_generator import _get_logo_base64
    
    # Cargar logo FV oficial en alta definición PNG/SVG
    root_assets = os.path.join(root_dir, "assets")
    fv_logo_path = os.path.join(root_assets, "NUEVO LOGO FV.png")
    if os.path.exists(fv_logo_path):
        with open(fv_logo_path, "rb") as img_f:
            fv_b64 = f"data:image/png;base64,{base64.b64encode(img_f.read()).decode('utf-8')}"
    else:
        fv_b64 = _get_logo_base64("NUEVO LOGO FV.svg")
        
    altus_b64 = _get_logo_base64("Logo_ALTUS AI_Principal.svg")

    # Reemplazar marcadores manuales de salto de página y convertir tablas
    markdown_processed = _parse_md_tables_to_html(contenido_markdown)
    markdown_processed = markdown_processed.replace("[SALTO]", "<pdf:nextpage />")
    markdown_processed = markdown_processed.replace("---", "<pdf:nextpage />")

    # Convertir markdown a HTML
    contenido_html = markdown.markdown(markdown_processed, extensions=['extra', 'nl2br'])

    # HTML TEMPLATE CON ESTILOS INSTITUCIONALES Y TABLAS COMPACTAS
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4 portrait;
                margin: 1.8cm;
                margin-bottom: 2cm;
                @frame footer_frame {{
                    -pdf-frame-content: footer_content;
                    left: 1.8cm; right: 1.8cm; bottom: 0.5cm; height: 1cm;
                }}
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                color: #333333;
                line-height: 1.45;
                font-size: 10pt;
            }}
            h1 {{
                color: #0A2342;
                font-size: 18px;
                text-align: center;
                margin-top: 15px;
                font-weight: bold;
            }}
            h2 {{
                color: #104b3c;
                font-size: 14px;
                border-bottom: 1.5px solid #0A2342;
                padding-bottom: 4px;
                margin-top: 20px;
                font-weight: bold;
            }}
            h3 {{
                color: #1a202c;
                font-size: 12px;
                margin-top: 15px;
                font-weight: bold;
            }}
            p {{
                text-align: justify;
                margin-bottom: 8px;
            }}
            ul, ol {{
                margin-bottom: 10px;
                margin-top: 4px;
                padding-left: 18px;
            }}
            li {{
                margin-bottom: 4px;
                text-align: justify;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                margin-bottom: 14px;
                font-size: 9pt;
                page-break-inside: avoid;
            }}
            th, td {{
                border: 1px solid #cbd5e1;
                padding: 5px 8px;
                text-align: left;
                vertical-align: top;
            }}
            th {{
                background-color: #0A2342;
                color: #ffffff;
                font-weight: bold;
                font-size: 9pt;
            }}
            tr {{
                page-break-inside: avoid;
            }}
            tr:nth-child(even) {{
                background-color: #f8fafc;
            }}
            .disclaimer {{
                font-size: 8.5pt;
                color: #64748b;
                text-align: justify;
                border-top: 1px solid #e2e8f0;
                padding-top: 8px;
                margin-top: 20px;
                page-break-inside: avoid;
            }}
            .corp-desc {{
                background-color: #f8fafc;
                border-left: 3px solid #D4AF37; /* Altus Gold */
                padding: 10px;
                font-size: 8.5pt;
                margin-top: 12px;
                color: #374151;
                page-break-inside: avoid;
            }}
            strong, b {{
                color: #0f172a;
            }}
        </style>
    </head>
    <body>

        <table style="width: 100%; border-bottom: 2px solid #0A2342; margin-bottom: 20px; padding-bottom: 10px;">
            <tr>
                <td style="text-align: left; width: 40%; vertical-align: middle; border:none;">
                    <img src="{fv_b64}" width="190">
                </td>
                <td style="text-align: right; width: 60%; vertical-align: middle; border:none;">
                    <table style="width: 100%; border: none; margin: 0; padding: 0;">
                        <tr style="border: none; background-color: transparent;">
                            <td style="text-align: right; vertical-align: middle; border: none; padding-right: 12px;">
                                <span style="font-size: 11pt; color: #0A2342; font-weight: bold;">Digital Family Office Analytics</span><br>
                                <span style="font-size: 8pt; color: #6b7280;">Fecha de Emisión: {datetime.now().strftime("%d-%m-%Y")}</span>
                            </td>
                            <td style="text-align: right; width: 80px; vertical-align: middle; border: none; padding: 0;">
                                <img src="{altus_b64}" width="65">
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        
        <div style="text-align: right; font-size: 8pt; color: #6b7280; margin-bottom: 15px;">
            Reporte generado y certificado por <strong>Altus AI</strong> para uso exclusivo de FV Asesorías e Inversiones
        </div>

        <table style="width:100%; margin-bottom:15px; background-color:#f8fafc; padding:10px; border-left: 3px solid #cbd5e1;">
            <tr>
                <td width="50%" style="padding: 5px;"><strong>Atención a:</strong> {cliente_nombre}</td>
                <td width="50%" style="padding: 5px;"><strong>Fecha:</strong> {fecha_actual}</td>
            </tr>
            <tr>
                <td width="50%" style="padding: 5px;"><strong>Unidad:</strong> Inteligencia de Mercados</td>
                <td width="50%" style="padding: 5px;"></td>
            </tr>
        </table>

        {contenido_html}

        <div class="disclaimer">
            <strong>Aviso Legal:</strong> Las visiones y proyecciones macroeconómicas presentadas en este documento han sido procesadas mediante inteligencia artificial (Altus AI) cruzando múltiples visiones institucionales. Este documento no constituye una recomendación de inversión vinculante, sino una herramienta de información estratégica. Los mercados son volátiles y las rentabilidades pasadas no garantizan retornos futuros. FV Asesorías e Inversiones limita su responsabilidad al análisis cuantitativo.
        </div>
        
        <div class="corp-desc" style="margin-top: 20px; page-break-inside: avoid;">
            <strong>Sobre FV Asesorías e Inversiones</strong><br>
            FV Asesorías e Inversiones somos un Multi-Family Office Digital impulsado por nuestro software cuantitativo privado de Inteligencia Artificial (ALTUS AI). Combinamos la agilidad tecnológica de una WealthTech con la exclusividad de una oficina patrimonial privada, auditando en 360° la situación tributaria, inmobiliaria, composición familiar, seguros e inversiones para proteger su legado a través de las generaciones.
        </div>

        <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-left: 3px solid #0A2342; padding: 6px 10px; margin-top: 8px; font-size: 7.5pt; color: #334155; line-height: 1.3; font-family: Helvetica, Arial, sans-serif; page-break-inside: avoid;">
            <strong>🔒 Ciberseguridad & Resguardo Patrimonial:</strong> Toda la información analizada por Altus AI se encuentra protegida bajo cifrado nativo <strong>AES-256 bits</strong> y transmisión <strong>TLS 1.3</strong> de grado bancario. Garantizamos estricta confidencialidad bajo Secreto Patrimonial y cumplimiento riguroso de la Ley N° 19.628 de Protección de Datos Personales en Chile.
        </div>

        <div id="footer_content">
            <div style="text-align: right; font-size: 9px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 5px;">
                Generado por Altus AI - FV Asesorías e Inversiones - Página <pdf:pagenumber>
            </div>
        </div>

    </body>
    </html>
    """
    
    with open(output_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)

    if pisa_status.err:
        raise Exception("Error al generar el PDF del reporte macro.")

    return output_path
