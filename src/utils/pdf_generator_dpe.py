import tempfile
from datetime import datetime

try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
except (ImportError, OSError):
    XHTML2PDF_AVAILABLE = False

def _generate_fallback_pdf(title, data, output_path):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt=f'Simulacion: {title}', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(200, 10, txt='Modo de compatibilidad (falta libreria Cairo).', ln=True)
    for k, v in data.items():
        if isinstance(v, (str, int, float)) and len(str(v)) < 100:
            pdf.cell(200, 10, txt=str(k) + ': ' + str(v), ln=True)
    try:
        pdf.output(output_path)
    except:
        pass

from src.utils.pdf_generator import _get_logo_base64

def generate_dpe_pdf(data: dict, output_path: str):
    if not XHTML2PDF_AVAILABLE:
        return _generate_fallback_pdf('Reporte Simulación', data, output_path)

    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    
    # Logos vectoriales (el método _get_logo_base64 ya debería proveer el Data URI correcto o el formato compatible)
    fv_b64 = _get_logo_base64("fv_logo_vector_pure.svg")
    altus_b64 = _get_logo_base64("altus_ai_logo_dark.svg")
    
    # Datos de DPE
    nombre_cliente = data.get("nombre", "Cliente")
    total_devolucion = data.get("total_devolucion", 0)
    meses_con_exceso = data.get("meses_con_exceso", [])
    
    total_formateado = f"${total_devolucion:,.0f}".replace(",", ".")
    
    tabla_meses = ""
    if not meses_con_exceso and total_devolucion > 0:
        tabla_meses = f"""
        <tr>
            <td style="text-align: left;">Promedio Anualizado</td>
            <td style="text-align: center;">N/A</td>
            <td>-</td>
            <td>-</td>
            <td style="color: #15803d;">{total_formateado}</td>
        </tr>
        """
    else:
        for mes in meses_con_exceso:
            renta_clp = f"${mes.get('renta_total', 0):,.0f}".replace(",", ".")
            exceso_clp = f"${mes.get('exceso_renta', 0):,.0f}".replace(",", ".")
            dev_clp = f"${mes.get('devolucion_estimada', 0):,.0f}".replace(",", ".")
            
            tabla_meses += f"""
            <tr>
                <td style="text-align: left;">{mes.get('periodo', 'N/A')}</td>
                <td style="text-align: center;">{mes.get('cantidad_empleadores', 1)}</td>
                <td>{renta_clp}</td>
                <td>{exceso_clp}</td>
                <td style="color: #15803d;">{dev_clp}</td>
            </tr>
            """
        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 1.2cm 1.5cm 2cm 1.5cm;
                @frame footer_frame {{
                    -pdf-frame-content: footer_content;
                    left: 42pt; width: 510pt; top: 800pt; height: 20pt;
                }}
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                color: #222222;
                font-size: 9pt;
                line-height: 1.4;
            }}
            h1 {{
                color: #000000;
                font-size: 14pt;
                text-align: left;
                margin-top: 15pt;
                margin-bottom: 5pt;
                text-transform: uppercase;
                border-bottom: 1.5px solid #000000;
                padding-bottom: 4pt;
                font-weight: bold;
            }}
            h2 {{
                color: #0A2342;
                font-size: 9.5pt;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 15pt;
                margin-bottom: 5pt;
                border-bottom: 0.5px solid #0A2342;
                padding-bottom: 2pt;
                font-weight: bold;
            }}
            .summary-box {{
                width: 100%;
                margin-bottom: 10pt;
                margin-top: 5pt;
            }}
            .summary-box td {{
                padding: 1pt 0;
                font-size: 8.5pt;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 5px;
                font-size: 8.5pt;
            }}
            .data-table th, .data-table td {{
                padding: 4px 0px;
            }}
            .data-table th {{
                color: #4b5563;
                font-weight: normal;
                text-align: left;
                border-bottom: 1px solid #0A2342;
            }}
            .data-table td {{
                text-align: right;
                font-weight: bold;
                border-bottom: 1px solid #e2e8f0;
            }}
            .total-row td, .total-row th {{
                font-size: 12pt;
                border-bottom: 1.5pt solid #0f172a;
                border-top: none;
                padding: 6px 4px;
                color: #15803d;
            }}
            .text-box {{
                font-size: 9pt;
                color: #374151;
                text-align: justify;
                line-height: 1.5;
                margin-bottom: 10pt;
            }}
            .disclaimer {{
                font-size: 7pt;
                color: #6b7280;
                text-align: justify;
                border-top: 1px solid #d1d5db;
                padding-top: 4px;
                margin-top: 15px;
                line-height: 1.3;
            }}
            .corp-desc {{
                background-color: #f8fafc;
                border-left: 3px solid #D4AF37;
                padding: 12px;
                font-size: 8.5pt;
                margin-top: 15px;
                color: #334155;
            }}
        </style>
    </head>
    <body>

        <table style="width: 100%; margin-bottom: 15pt; background-color: #0A2342; padding: 10pt;">
            <tr>
                <td style="text-align: left; width: 40%; vertical-align: middle; border: none;">
                    <img src="{fv_b64}" width="170">
                </td>
                <td style="text-align: right; width: 60%; vertical-align: middle; border: none;">
                    <table style="width: 100%; border: none; margin: 0; padding: 0;">
                        <tr style="border: none;">
                            <td style="text-align: right; vertical-align: middle; border: none; padding-right: 10px;">
                                <span style="font-size: 10pt; color: #ffffff; font-weight: bold;">DIGITAL FAMILY OFFICE ANALYTICS</span><br>
                                <span style="font-size: 8pt; color: #94a3b8;">Powered by</span>
                            </td>
                            <td style="text-align: right; width: 70px; vertical-align: middle; border: none; padding: 0;">
                                <img src="{altus_b64}" width="65">
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <h1 style="color: #0A2342; border-bottom: 2px solid #D4AF37;">Reporte Cuantitativo: Rescate Previsional (DPE)</h1>

        <table class="summary-box">
            <tr>
                <td width="50%"><strong>Cliente:</strong> {nombre_cliente}</td>
                <td width="50%" align="right"><strong>Fecha de Emisión:</strong> {fecha_actual}</td>
            </tr>
        </table>

        <h2>Monto Estimado a Recuperar (Líquido)</h2>
        <table class="data-table">
            <tr class="total-row">
                <th style="font-size: 12pt; color: #15803d; border-bottom: 1.5pt solid #0f172a;">TOTAL ESTIMADO DE DEVOLUCIÓN</th>
                <td style="text-align: right; font-size: 16pt;">{total_formateado} CLP</td>
            </tr>
        </table>
        <p class="text-box" style="margin-top: 0; font-size: 8pt;">* Corresponde a excesos por cotización obligatoria (Tope Imponible) históricamente no reclamados en la Administradora de Fondos de Pensiones.</p>

        <h2>1. Resumen de Períodos con Pagos en Exceso</h2>
        <p class="text-box">Según la lectura automatizada del certificado, detectamos los siguientes meses donde sus empleadores cotizaron de forma simultánea por sobre el límite máximo legal permitido:</p>
        
        <table class="data-table">
            <thead>
                <tr>
                    <th style="text-align: left;">Mes/Año</th>
                    <th style="text-align: center;">N° Empleadores</th>
                    <th style="text-align: right;">Renta Bruta Sumada</th>
                    <th style="text-align: right;">Renta Sobre Tope</th>
                    <th style="text-align: right;">Devolución Estimada</th>
                </tr>
            </thead>
            <tbody>
                {tabla_meses}
            </tbody>
        </table>

        <h2>2. Plan de Acción y Siguientes Pasos</h2>
        <p class="text-box">El dinero detallado en este informe le pertenece legalmente. Sin embargo, <strong>las AFP no lo devuelven de manera automática a la cuenta corriente</strong>; de no mediar una solicitud formal, estos fondos quedarán retenidos indefinidamente en las cuentas de rezago de la administradora.</p>
        
        <div class="corp-desc" style="margin-bottom: 10px;">
            <strong>Proceso Estándar de Recuperación (Regulado por la Superintendencia de Pensiones)</strong><br><br>
            El trámite para el rescate de estos fondos es estándar para todas las AFP en Chile (Habitat, Cuprum, Capital, Modelo, etc.), ya que se rige por la misma normativa de la Superintendencia. El proceso es 100% online y se realiza desde la sucursal virtual de su AFP:<br><br>
            1. <strong>Ingreso a su AFP:</strong> Con su RUT y Clave Web, ingrese a la Sucursal Virtual de su AFP.<br>
            2. <strong>Formulario DPE:</strong> Busque la sección de Trámites o Pagos en Exceso y complete el "Formulario de Devolución de Pagos en Exceso", adjuntando la cuenta bancaria de destino (que debe estar a su nombre).<br>
            3. <strong>Revisión Legal:</strong> La AFP analizará la solicitud y cruzará la información con Previred. Este proceso normativo toma entre 15 a 30 días hábiles.<br>
            4. <strong>Liquidación:</strong> Una vez aprobado, el dinero será transferido como monto líquido directamente a su cuenta bancaria.<br>
        </div>
        
        <div class="corp-desc" style="border-left: 3px solid #15803d; background-color: #f0fdf4; text-align: justify; line-height: 1.6;">
            <strong>¿Cómo le apoyamos desde FV Asesorías e Inversiones?</strong><br><br>
            Al ser un trámite estrictamente personal, <strong>nuestro equipo de asesores le guiará paso a paso en una breve sesión (o llamada) para que usted mismo ingrese la solicitud de forma rápida y segura</strong>, sin necesidad de mandatos notariales ni papeleos. El verdadero valor de nuestra asesoría comienza cuando recupere este capital: le presentaremos alternativas de inversión eficiente. <strong>El monto recuperado puede ser transferido a su cuenta corriente o reinvertido con beneficios tributarios en PRINCIPAL (APV / Cuenta 2) a través de FV Asesorías e Inversiones</strong>, rentabilizando este dinero imprevisto para generar un impacto real en su patrimonio.
        </div>

        <p style="font-size: 9pt; color: #4b5563; text-align: right; margin-top: 20px; margin-bottom: 30px; font-style: italic;">
            Atentamente,<br>
            <strong>FV ASESORIAS E INVERSIONES SPA</strong><br>
            (Powered by Altus Core)
        </p>

        <div class="disclaimer">
            <strong>AVISO LEGAL:</strong> Este análisis ha sido generado por el motor de inteligencia artificial de Altus AI, basado en la extracción y procesamiento de certificados históricos de cotizaciones previsionales. Los montos expresados son estimaciones matemáticas considerando topes imponibles estándar y tasas nominales de retención del 10%. El monto final a depositar por parte de la AFP puede variar levemente. FV Asesorías no garantiza el monto exacto, pero sí la gestión y asesoría integral para su máxima recuperación.
        </div>
        
        <div class="corp-desc">
            <strong>Sobre FV Asesorías e Inversiones</strong><br>
            FV Asesorías e Inversiones somos un Multi-Family Office Digital impulsado por nuestro software cuantitativo privado de Inteligencia Artificial (ALTUS AI). Combinamos la agilidad tecnológica de una WealthTech con la exclusividad de una oficina patrimonial privada, auditando en 360° la situación tributaria, inmobiliaria, composición familiar, seguros e inversiones para proteger su legado a través de las generaciones.
        </div>

        <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-left: 3px solid #0A2342; padding: 8px 12px; margin-top: 15px; font-size: 7.5pt; color: #334155; line-height: 1.4; font-family: Helvetica, Arial, sans-serif;">
            <strong>[Seguridad y Resguardo Patrimonial]:</strong> Toda la información analizada por Altus AI se encuentra protegida bajo cifrado nativo <strong>AES-256 bits</strong> y transmisión <strong>TLS 1.3</strong> de grado bancario. Garantizamos estricta confidencialidad bajo Secreto Patrimonial y cumplimiento riguroso de la Ley N° 19.628 de Protección de Datos Personales en Chile.
        </div>

        <div id="footer_content" style="text-align: right; font-size: 8pt; color: #94a3b8; border-top: 0.5px solid #e5e7eb; padding-top: 4pt;">
            FV Asesorías e Inversiones - Página <pdf:pagenumber>
        </div>

    </body>
    </html>
    """
    
    with open(output_path, "w+b") as out_pdf:
        pisa_status = pisa.CreatePDF(html_content, dest=out_pdf)
    
    return not pisa_status.err

def generate_dpe_pdf_simple(data, output_path):
    import xhtml2pdf.pisa as pisa
    
    meses_con_exceso = data.get("meses_con_exceso", [])
    
    tabla_meses = ""
    if not meses_con_exceso and data.get("total_devolucion", 0) > 0:
        tabla_meses = f"""
        <tr>
            <td style="text-align: center;">Promedio Anualizado</td>
            <td style="text-align: center;">N/A</td>
            <td style="text-align: right;">-</td>
            <td style="text-align: right;">-</td>
            <td style="text-align: right; color: #15803d; font-weight: bold;">${data.get("total_devolucion", 0):,.0f}</td>
        </tr>
        """
    else:
        for mes in meses_con_exceso:
            tabla_meses += f"""
            <tr>
                <td style="text-align: center;">{mes.get('periodo', 'N/A')}</td>
                <td style="text-align: center;">{mes.get('cantidad_empleadores', 1)}</td>
                <td style="text-align: right;">${mes.get('renta_total', 0):,.0f}</td>
                <td style="text-align: right;">${mes.get('tope_aplicado', 0):,.0f}</td>
                <td style="text-align: right; color: #15803d; font-weight: bold;">${mes.get('devolucion_estimada', 0):,.0f}</td>
            </tr>
            """
        
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Helvetica, Arial, sans-serif; font-size: 10pt; color: #1e293b; line-height: 1.5; }}
            h1 {{ font-size: 16pt; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }}
            h2 {{ font-size: 12pt; color: #334155; margin-top: 20px; }}
            .data-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 25px; }}
            .data-table th, .data-table td {{ border: 1px solid #cbd5e1; padding: 10px; font-size: 9pt; }}
            .data-table th {{ background-color: #f8fafc; font-weight: bold; text-align: left; color: #475569; }}
        </style>
    </head>
    <body>
        <div style="text-align: center; margin-bottom: 30px;">
            <h1>ANEXO TÉCNICO: CÁLCULO DE EXCESOS SOBRE TOPE IMPONIBLE</h1>
        </div>

        <h2>Identificación del Afiliado</h2>
        <p><strong>Nombre:</strong> {data.get("nombre", "No especificado")}</p>

        <h2>Detalle de Periodos con Exceso Detectado</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th style="text-align: center;">Mes/Año</th>
                    <th style="text-align: center;">N° Empleadores</th>
                    <th style="text-align: right;">Renta Bruta Sumada</th>
                    <th style="text-align: right;">Tope Legal Aplicado</th>
                    <th style="text-align: right;">Devolución (10%)</th>
                </tr>
            </thead>
            <tbody>
                {tabla_meses}
            </tbody>
        </table>

        <div style="margin-top: 30px; font-size: 9pt; text-align: justify;">
            <strong>Nota Técnica:</strong> El presente anexo detalla los cálculos matemáticos de las remuneraciones imponibles sumadas correspondientes a los periodos listados, cruzadas contra el valor oficial de la Unidad de Fomento (UF) del último día del mes respectivo y el tope imponible en UF vigente para el año tributario, de acuerdo a la normativa de la Superintendencia de Pensiones. Se solicita la devolución del 10% de cotización obligatoria pagada sobre dicho límite.
        </div>
    </body>
    </html>
    """
    
    with open(output_path, "w+b") as out_pdf:
        pisa_status = pisa.CreatePDF(html_content, dest=out_pdf)
    
    return not pisa_status.err
