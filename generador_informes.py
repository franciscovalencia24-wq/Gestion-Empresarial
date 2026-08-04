import os
import markdown
from xhtml2pdf import pisa
import base64
from datetime import datetime
import io

def get_fv_logo_b64():
    logo_path = os.path.join(os.path.dirname(__file__), "src", "web", "assets", "NUEVO LOGO FV.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')
    return ""

def get_altus_logo_b64():
    logo_path = os.path.join(os.path.dirname(__file__), "assets/brand/altus_ai_logo_principal.png")
    try:
        from PIL import Image, ImageDraw
        with Image.open(logo_path).convert("RGBA") as img:
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
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode('utf-8')
    except:
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')
    return ""

def generar_pdf_bytes(titulo, contenido_md):
    fv_b64 = get_fv_logo_b64()
    altus_b64 = get_altus_logo_b64()
    fecha_hoy = datetime.now().strftime("%d-%m-%Y")
    
    html_content = markdown.markdown(contenido_md, extensions=['tables'])
    
    # Reemplazar la línea horizontal de Markdown (---) por un salto de página forzado en xhtml2pdf
    html_content = html_content.replace('<hr />', '<pdf:nextpage />').replace('<hr>', '<pdf:nextpage />')
    
    # Corrección del Bug de xhtml2pdf: Si Markdown detecta un espacio en blanco entre viñetas, las envuelve en <p>. 
    # xhtml2pdf oculta el punto de la viñeta si hay un <p> dentro del <li>. Esto lo soluciona.
    html_content = html_content.replace('<li><p>', '<li>').replace('</p></li>', '</li>')
    html_content = html_content.replace('<li>\n<p>', '<li>').replace('</p>\n</li>', '</li>')
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        @page {{
            size: letter portrait;
            margin: 1.5cm 1.5cm 2.5cm 1.5cm;
            @frame footer {{
                -pdf-frame-content: footer_content;
                bottom: 1.0cm;
                margin-left: 1.5cm;
                margin-right: 1.5cm;
                height: 1.0cm;
            }}
        }}
        body {{
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: 10.5pt;
            color: #2b3035;
            line-height: 1.6;
            text-align: justify;
        }}
        p {{
            text-align: justify;
            margin-bottom: 12px;
        }}
        h1, h2, h3 {{
            color: #0A2342;
            margin-top: 18px;
            margin-bottom: 12px;
            font-weight: bold;
        }}
        h1 {{ border-bottom: 2px solid #D4AF37; padding-bottom: 4px; font-size: 16pt; }}
        h2 {{ font-size: 14pt; }}
        h3 {{ font-size: 12pt; }}
        
        strong, b {{
            font-weight: bold;
            color: #0A2342; /* Las negritas en azul corporativo sutil para destacar */
        }}
        ul, ol {{
            margin-top: 5px;
            margin-bottom: 12px;
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 6px;
            text-align: left;
        }}
        em, i {{
            font-style: italic;
        }}
        
        .corp-desc {{
            background-color: #f8fafc;
            border-left: 3px solid #D4AF37;
            padding: 12px;
            font-size: 9pt;
            margin-top: 30px;
            margin-bottom: 15px;
            color: #374151;
        }}
        .contact-info {{
            background-color: #f8fafc;
            border-left: 3px solid #D4AF37;
            padding: 8px 12px;
            font-size: 9pt;
            font-weight: bold;
            color: #0A2342;
        }}
        #footer_content {{
            font-size: 8pt;
            color: #6b7280;
            text-align: center;
            border-top: 1px solid #e5e7eb;
            padding-top: 5px;
        }}
    </style>
    </head>
    <body>
        <table style="width: 100%; border-bottom: 2px solid #0A2342; margin-bottom: 20px; padding-bottom: 10px;">
            <tr>
                <td style="text-align: left; width: 40%; vertical-align: middle; border:none;">
                    <img src="{fv_b64}" width="140">
                </td>
                <td style="text-align: right; width: 60%; vertical-align: middle; border:none;">
                    <table style="width: 100%; border: none; margin: 0; padding: 0;">
                        <tr style="border: none; background-color: transparent;">
                            <td style="text-align: right; vertical-align: middle; border: none; padding-right: 12px;">
                                <span style="font-size: 11pt; color: #0A2342; font-weight: bold;">Digital Family Office Analytics</span><br>
                                <span style="font-size: 8pt; color: #6b7280;">Fecha de Emisión: {fecha_hoy}</span>
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
            Análisis procesado cuantitativamente por <strong>Altus AI</strong> para uso exclusivo de FV Asesorías e Inversiones
        </div>

        <h1>{titulo}</h1>

        <div>
            {html_content}
        </div>
        
        <div class="corp-desc">
            <strong>Sobre FV Asesorías e Inversiones</strong><br>
            FV Asesorías e Inversiones somos un Multi-Family Office Digital impulsado por nuestro software cuantitativo privado de Inteligencia Artificial (ALTUS AI). Combinamos la agilidad tecnológica de una WealthTech con la exclusividad de una oficina patrimonial privada, auditando en 360° la situación tributaria, inmobiliaria, composición familiar, seguros e inversiones para proteger su legado a través de las generaciones.
        </div>

        <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-left: 3px solid #0A2342; padding: 6px 10px; margin-top: 8px; font-size: 7.5pt; color: #334155; line-height: 1.3; font-family: Helvetica, Arial, sans-serif;">
            <strong>🔒 Ciberseguridad & Resguardo Patrimonial:</strong> Toda la información analizada por Altus AI se encuentra protegida bajo cifrado nativo <strong>AES-256 bits</strong> y transmisión <strong>TLS 1.3</strong> de grado bancario. Garantizamos estricta confidencialidad bajo Secreto Patrimonial y cumplimiento riguroso de la Ley N° 19.628 de Protección de Datos Personales en Chile.
        </div>
        
        <div class="contact-info">
            Contacto: contacto@fv-inversiones.com | +569 89779862
        </div>
        
        <div id="footer_content">
            FV Asesorías e Inversiones | Análisis Confidencial | Página <pdf:pagenumber> de <pdf:pagecount>
        </div>
    </body>
    </html>
    """
    
    result_bytes = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_template, dest=result_bytes, encoding='utf-8')
    
    if pisa_status.err:
        return None
    return result_bytes.getvalue()
