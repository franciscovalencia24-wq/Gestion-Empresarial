import tempfile
import io
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

import base64
from src.utils.pdf_generator import _get_logo_base64

def generate_cuenta2_pdf(data: dict, output_path: str):
    if not XHTML2PDF_AVAILABLE:
        return _generate_fallback_pdf('Reporte Simulación', data, output_path)

    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    
    # Logos vectoriales
    fv_b64 = _get_logo_base64("fv_logo_vector_pure.svg")
    altus_b64 = _get_logo_base64("altus_ai_logo_dark.svg")
    
    # HTML TEMPLATE
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
                color: #0A2342;
                font-size: 14pt;
                text-align: left;
                margin-top: 15pt;
                margin-bottom: 5pt;
                text-transform: uppercase;
                border-bottom: 2px solid #D4AF37;
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
                width: 70%;
                font-weight: normal;
                text-align: left;
            }}
            .data-table td {{
                text-align: right;
                font-weight: bold;
            }}
            .total-row td, .total-row th {{
                font-size: 9.5pt;
                border-bottom: 1.5pt solid #0f172a;
                border-top: none;
                padding: 6px 4px;
                color: #000000;
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

        <h1>Propuesta de Inversión Patrimonial: Cuenta 2 / Fondos Mutuos</h1>

        <table class="summary-box">
            <tr>
                <td width="50%"><strong>Cliente:</strong> {data.get("nombre", "No especificado")}</td>
                <td width="50%" align="right"><strong>Fecha de Emisión:</strong> {fecha_actual}</td>
            </tr>
            <tr>
                <td width="50%"><strong>RUT:</strong> {data.get("rut", "No especificado")}</td>
                <td width="50%" align="right"><strong>Horizonte de Inversión:</strong> {data.get("horizonte_anios", 0)} Años</td>
            </tr>
        </table>

        <h2>1. Estructura de Aportes</h2>
        <table class="data-table">
            <tr>
                <th>Aporte Inicial (Monto de Apertura)</th>
                <td>${data.get("monto_apertura", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>Aporte Mensual Programado</th>
                <td>${data.get("aporte_mensual", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>Perfil de Inversión Estimado (Tasa Anualizada)</th>
                <td>{data.get("tasa_anual", 0):.2f}%</td>
            </tr>
            <tr class="total-row">
                <th>Total Aportado Directamente por el Cliente</th>
                <td>${data.get("total_aportes", 0):,.0f} CLP</td>
            </tr>
        </table>

        <h2>2. Proyección de Capitalización</h2>
        <table class="data-table">
            <tr>
                <th>Ganancia de Capital (Rentabilidad Proyectada)</th>
                <td style="color: #15803d;">+${data.get("rentabilidad_total", 0):,.0f} CLP</td>
            </tr>
            <tr class="total-row">
                <th>Saldo Final Estimado en la Cuenta</th>
                <td style="color: #0A2342; font-size: 11pt;">${data.get("saldo_final", 0):,.0f} CLP</td>
            </tr>
        </table>

        <h2>3. Optimización Tributaria (Impacto IGC y 30 UTM)</h2>
        <div style="font-size: 8.5pt; text-align: justify; margin-bottom: 8px;">
            Al momento de rescatar los fondos, solo la <strong>rentabilidad real</strong> está afecta a impuestos. Además, bajo el Régimen General, se cuenta con una exención tributaria que libera de pago hasta <strong>30 UTM</strong> anuales de utilidad generada.
        </div>
        <table class="data-table">
            <tr>
                <th>Rentabilidad Exenta Estimada (Bajo Límite de 30 UTM)</th>
                <td style="color: #15803d;">${data.get("rentabilidad_exenta", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>Rentabilidad Afecta Estimada (Sobre Límite de 30 UTM)</th>
                <td style="color: #b91c1c;">${data.get("rentabilidad_afecta", 0):,.0f} CLP</td>
            </tr>
        </table>
        
        <h2>4. Exención Tributaria de Herencia (Art. 72 D.L. 3.500)</h2>
        <div class="corp-desc" style="border-left: 3px solid #0f766e; background-color: #f0fdfa; margin-top: 5px;">
            <strong>Beneficio Sucesorio Legal:</strong> Los fondos mantenidos en Cuenta 2 de AFP gozan de un beneficio patrimonial excepcional. En caso de fallecimiento, hasta <strong>4.000 UF</strong> (Aprox. ${data.get("limite_4000_uf_clp", 0):,.0f} CLP) del saldo quedan totalmente exentos del Impuesto a las Herencias, Asignaciones y Donaciones. Esto convierte a la Cuenta 2 en un vehículo óptimo de protección patrimonial intergeneracional.
        </div>

        <h2>5. Recomendación Comercial</h2>
        <div class="corp-desc" style="border-left: 3px solid #15803d; background-color: #f0fdf4;">
            <strong>Diversificación a través de PRINCIPAL</strong><br><br>
            A través de FV Asesorías e Inversiones, le recomendamos canalizar esta estrategia de liquidez y crecimiento a través de las alternativas de inversión y multifondos en <strong>PRINCIPAL</strong>. Esto le permite acceder a la máxima flexiblidad de aportes y retiros, administración de clase mundial y consolidar sus objetivos patrimoniales bajo un mismo alero institucional.
        </div>

        <p style="font-size: 9pt; color: #4b5563; text-align: right; margin-top: 20px; margin-bottom: 30px; font-style: italic;">
            Atentamente,<br>
            <strong>FV ASESORIAS E INVERSIONES SPA</strong><br>
            (Powered by Altus Core)
        </p>

        <div class="disclaimer">
            <strong>AVISO LEGAL:</strong> Las rentabilidades presentadas en este documento son meramente proyectadas y referenciales. La rentabilidad pasada no garantiza la rentabilidad futura. Los valores en UF y UTM pueden fluctuar según la inflación. Esta proyección no constituye asesoría tributaria vinculante, ni declaración ante el Servicio de Impuestos Internos (SII). FV Asesorías e Inversiones SpA limita su responsabilidad al cálculo matemático estimado en base a los inputs ingresados.
        </div>
        
        <div class="corp-desc" style="margin-top: 10px;">
            <strong>Sobre FV Asesorías e Inversiones</strong><br>
            Somos un Multi-Family Office Digital impulsado por inteligencia cuantitativa (ALTUS AI). Auditamos en 360° la situación tributaria, inmobiliaria y previsional de nuestros clientes para proteger su legado. Toda información es manejada bajo estricto Secreto Patrimonial (AES-256 bits).
        </div>

        <div id="footer_content" style="text-align: right; font-size: 8pt; color: #94a3b8; border-top: 0.5px solid #e5e7eb; padding-top: 4pt;">
            FV Asesorías e Inversiones - Página <pdf:pagenumber>
        </div>

    </body>
    </html>
    """
    
    with open(output_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(io.BytesIO(html_content.encode("utf-8")), dest=result_file, encoding='utf-8')

    if pisa_status.err:
        raise Exception("Error al generar el PDF de Cuenta 2.")

    return output_path
