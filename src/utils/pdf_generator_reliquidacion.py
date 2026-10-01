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

import matplotlib.pyplot as plt
import base64
from src.utils.pdf_generator import _get_logo_base64

def generate_reliquidacion_pdf(data: dict, output_path: str):
    if not XHTML2PDF_AVAILABLE:
        return _generate_fallback_pdf('Reporte Simulación', data, output_path)

    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    
    # Logos vectoriales
    fv_b64 = _get_logo_base64("fv_logo_vector_pure.svg")
    altus_b64 = _get_logo_base64("altus_ai_logo_dark.svg")
    
    import markdown
    rag_response_md = data.get("rag_response", "")
    rag_html = markdown.markdown(rag_response_md) if rag_response_md else "<p><i>Análisis no disponible en esta simulación.</i></p>"
    
    holgura_md = data.get("holgura_mensaje", "")
    holgura_html = markdown.markdown(holgura_md) if holgura_md else ""

    compare_data = data.get("compare_data", [])
    chart_b64 = data.get("chart_b64", "")
    df_rentas = data.get("df_rentas", [])

    rentas_html = ""
    if df_rentas:
        rentas_html += f"""
        <h2>1. Detalle de Rentas Mensuales</h2>
        <table class="data-table" style="margin-bottom: 15px;">
            <tr>
                <th style="font-weight: bold; color: #000; border-bottom: 1px solid #000;">Periodo</th>
                <th style="text-align: right; font-weight: bold; color: #000; border-bottom: 1px solid #000;">Sueldo Bruto</th>
                <th style="text-align: right; font-weight: bold; color: #000; border-bottom: 1px solid #000;">Honorarios Brutos</th>
            </tr>
        """
        for row in df_rentas:
            sueldo = row.get("Sueldo Bruto (CLP)", 0)
            boletas = row.get("Boletas (CLP)", 0)
            rentas_html += f"""
            <tr>
                <td style="border-bottom: 1px solid #e2e8f0;">{row.get("Mes", "N/A")}</td>
                <td style="text-align: right; border-bottom: 1px solid #e2e8f0;">${sueldo:,.0f}</td>
                <td style="text-align: right; border-bottom: 1px solid #e2e8f0;">${boletas:,.0f}</td>
            </tr>
            """
        rentas_html += "</table>"


    compare_html = ""
    if compare_data:
        compare_html += f"""
        <h2>6. Comparación de Escenarios (Ahorro Tributario Final)</h2>
        <table class="data-table" style="margin-bottom: 15px;">
            <tr>
                <th style="width: 50%; font-weight: bold; color: #000; border-bottom: 1px solid #000;">Escenario</th>
                <th style="width: 25%; text-align: right; font-weight: bold; color: #000; border-bottom: 1px solid #000;">Resultado (TGR)</th>
                <th style="width: 25%; text-align: right; font-weight: bold; color: #000; border-bottom: 1px solid #000;">Incremento Capital</th>
            </tr>
        """
        for item in compare_data:
            saldo = item['Saldo']
            saldo_str = f"+${saldo:,.0f} (A favor)" if saldo > 0 else f"-${abs(saldo):,.0f} (Deuda)"
            color_saldo = "#15803d" if saldo > 0 else "#b91c1c"
            
            compare_html += f"""
            <tr>
                <td style="border-left: 4px solid {item['Color']}; padding-left: 6px;"><strong>{item['Escenario']}</strong></td>
                <td style="text-align: right; color: {color_saldo}; font-weight: bold;">{saldo_str}</td>
                <td style="text-align: right; font-weight: bold; color: {item['Color']};">${item['Inversion']:,.0f}</td>
            </tr>
            """
        compare_html += "</table>"

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
            .text-box {{
                font-size: 9pt;
                color: #374151;
                text-align: justify;
                line-height: 1.5;
                margin-bottom: 10pt;
            }}
            .rag-box {{
                font-size: 9pt;
                color: #111827;
                text-align: justify;
                line-height: 1.5;
            }}
            .rag-box ul {{
                margin-top: 5px;
                margin-bottom: 5px;
            }}
            .rag-box li {{
                margin-bottom: 4px;
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

        <h1 style="color: #0A2342; border-bottom: 2px solid #D4AF37;">Reporte Cuantitativo: Simulador de Reliquidación</h1>

        <table class="summary-box">
            <tr>
                <td width="50%"><strong>Cliente:</strong> {data.get("nombre", "No especificado")}</td>
                <td width="50%" align="right"><strong>Fecha de Emisión:</strong> {fecha_actual}</td>
            </tr>
            <tr>
                <td width="50%"><strong>RUT:</strong> {data.get("rut", "No especificado")}</td>
                <td width="50%" align="right"><strong>Holgura APV Max.:</strong> ${data.get("holgura_monto", 0):,.0f} CLP</td>
            </tr>
        </table>
        
        {rentas_html}

        <h2>2. Resumen de Ingresos Anuales (Consolidado)</h2>
        <table class="data-table">
            <tr>
                <th>Sueldo Bruto Anual</th>
                <td>${data.get("renta_bruta_anual", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>(+) Ganancias de Capital / Rentas Pasivas</th>
                <td>${data.get("ganancias_capital", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>(-) Descuentos Legales Anuales (AFP/Salud)</th>
                <td>${data.get("descuentos_legales", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>(-) Intereses Hipotecarios (Art. 55 Bis)</th>
                <td>${data.get("rebaja_55bis", 0):,.0f} CLP</td>
            </tr>
            <tr class="total-row">
                <th>Base Imponible Inicial (Pre-APV)</th>
                <td>${data.get("renta_bruta", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>Retiro APV Régimen B (Suma a la base)</th>
                <td>${data.get("retiro_apvb_anual", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>Total Retenciones e Impuestos Pagados (Acumulado)</th>
                <td>${data.get("retenciones", 0):,.0f} CLP</td>
            </tr>
        </table>

        <h2>3. Optimización Tributaria y Devolución Solicitada</h2>
        <table class="data-table">
            <tr>
                <th>Aporte APV Realizado (Régimen B)</th>
                <td>${data.get("aporte_apv", 0):,.0f} CLP</td>
            </tr>
            <tr class="total-row">
                <th>Base Imponible Optimizada Final</th>
                <td>${data.get("renta_neta", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>Impuesto Global Complementario (IGC) Determinado</th>
                <td>${data.get("igc_optimizado", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>(-) Impuesto Único Retiro APV B ({data.get("tasa_impuesto_unico", 0):.1f}%)</th>
                <td>${data.get("impuesto_unico_retiro", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>Beneficio Tributario Neto de la Estrategia</th>
                <td style="color: #15803d;">${data.get("beneficio_apv", 0):,.0f} CLP</td>
            </tr>
            <tr class="total-row">
                <th style="color: {'#15803d' if data.get("saldo_final", 0) > 0 else '#b91c1c'};">
                    {'DEVOLUCIÓN DE IMPUESTOS A FAVOR' if data.get("saldo_final", 0) > 0 else 'MONTO A PAGAR AL SII'}
                </th>
                <td style="color: {'#15803d' if data.get("saldo_final", 0) > 0 else '#b91c1c'};">
                    ${abs(data.get("saldo_final", 0)):,.0f} CLP
                </td>
            </tr>
        </table>
        
        <div class="corp-desc" style="border-left: 3px solid #15803d; background-color: #f0fdf4; text-align: justify; line-height: 1.6; margin-bottom: 15px;">
            <strong>¿Qué hacer con su Devolución de Impuestos?</strong><br><br>
            La devolución fiscal obtenida producto de una correcta planificación (Reliquidación) es capital líquido que le pertenece. <strong>Recomendamos que esta devolución sea capitalizada en PRINCIPAL</strong> (mediante APV Régimen B o Fondos Mutuos) a través de la asesoría de FV Asesorías e Inversiones. De esta manera, el monto recuperado entra inmediatamente a optimizar su ciclo tributario del año siguiente, generando un efecto compuesto de ahorro e inversión para su pensión.
        </div>

        <h2>4. Recomendación Algorítmica Estratégica</h2>
        <div class="text-box">
            {holgura_html}
        </div>

        <h2>5. Dictamen Jurídico-Tributario (Altus AI)</h2>
        <div class="rag-box">
            {rag_html}
        </div>
        
        {compare_html}

        <p style="font-size: 9pt; color: #4b5563; text-align: right; margin-top: 20px; margin-bottom: 30px; font-style: italic;">
            Atentamente,<br>
            <strong>FV ASESORIAS E INVERSIONES SPA</strong><br>
            (Powered by Altus Core)
        </p>

        <div class="disclaimer">
            <strong>AVISO LEGAL:</strong> Este documento es una simulación proyectada generada mediante algoritmos cuantitativos (Altus AI) basada en los tramos de Impuesto Global Complementario y valores UTM/UTA referenciales. No constituye asesoría tributaria vinculante, ni una declaración formal ante el Servicio de Impuestos Internos (SII). Los valores finales pueden variar por fluctuaciones inflacionarias (UF) o ajustes normativos. FV Asesorías e Inversiones SpA es un Multi-Family Office enfocado en optimización patrimonial y limita su responsabilidad al cálculo matemático proyectado. La información se encuentra cifrada bajo secreto patrimonial.
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
    
    with open(output_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(io.BytesIO(html_content.encode("utf-8")), dest=result_file, encoding='utf-8')

    if pisa_status.err:
        raise Exception("Error al generar el PDF de reliquidación.")

    return output_path
