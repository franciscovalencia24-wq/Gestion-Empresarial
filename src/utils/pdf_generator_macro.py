import os
import io
import base64
from datetime import datetime
from xhtml2pdf import pisa
import markdown

def generate_macro_pdf(cliente_nombre: str, contenido_markdown: str, output_path: str):
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Logos
    logo_fv_path = os.path.join(root_dir, "assets", "Logo_FV_Principal.png")
    altus_logo_path = os.path.join(root_dir, "assets", "Logo_ALTUS AI_Principal_Fondo oscuro.png")
    
    try:
        with open(logo_fv_path, "rb") as f:
            fv_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')
    except:
        fv_b64 = ""
        
    try:
        from PIL import Image, ImageDraw
        import io as pil_io
        with Image.open(altus_logo_path).convert("RGBA") as img:
            rad = 40
            circle = Image.new('L', (rad * 2, rad * 2), 0)
            draw = ImageDraw.Draw(circle)
            draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
            alpha = Image.new('L', img.size, 255)
            w, h = img.size
            alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
            alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
            alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
            alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
            img.putalpha(alpha)
            buffered = pil_io.BytesIO()
            img.save(buffered, format="PNG")
            altus_b64 = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        try:
            with open(altus_logo_path, "rb") as f:
                altus_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')
        except:
            altus_b64 = ""

    # Reemplazar marcadores manuales de salto de página
    markdown_processed = contenido_markdown.replace("[SALTO]", "<pdf:nextpage />")
    markdown_processed = markdown_processed.replace("---", "<pdf:nextpage />")

    # Convertir markdown a HTML
    contenido_html = markdown.markdown(markdown_processed, extensions=['extra', 'nl2br'])

    # HTML TEMPLATE
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4 portrait;
                margin: 2cm;
                margin-bottom: 2cm;
                @frame footer_frame {{
                    -pdf-frame-content: footer_content;
                    left: 2cm; right: 2cm; bottom: 0.5cm; height: 1cm;
                }}
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                color: #333333;
                line-height: 1.5;
                font-size: 11pt;
            }}
            h1 {{
                color: #104b3c;
                font-size: 20px;
                text-align: center;
                margin-top: 15px;
            }}
            h2 {{
                color: #1a202c;
                font-size: 16px;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 5px;
                margin-top: 25px;
            }}
            h3 {{
                color: #1a202c;
                font-size: 14px;
                margin-top: 20px;
            }}
            p {{
                text-align: justify;
                margin-bottom: 10px;
            }}
            ul, ol {{
                margin-bottom: 15px;
                margin-top: 5px;
            }}
            li {{
                margin-bottom: 5px;
                text-align: justify;
            }}
            .disclaimer {{
                font-size: 10px;
                color: #64748b;
                text-align: justify;
                border-top: 1px solid #e2e8f0;
                padding-top: 10px;
                margin-top: 30px;
            }}
            .corp-desc {{
                background-color: #f8fafc;
                border-left: 3px solid #D4AF37; /* Altus Gold */
                padding: 12px;
                font-size: 9pt;
                margin-top: 20px;
                color: #374151;
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
            Somos un Multi-Family Office Digital potenciado por <b>Altus AI</b>, nuestro Software Cuantitativo Privado. Combinamos la precisión algorítmica de la Inteligencia Artificial con la exclusividad de la banca privada para auditar portafolios, cruzar normativas tributarias complejas, incorporar información de valor para cada cliente y diseñar estrategias patrimoniales hiper-personalizadas de grado institucional.
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
