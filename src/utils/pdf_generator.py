import os
import datetime
from io import BytesIO
from xhtml2pdf import pisa
import base64

def _get_logo_base64():
    logo_path = r"c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\logo_flat.jpg"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded}"
    return ""

def generate_kyc_manual(cliente_nombre: str) -> bytes:
    """
    Genera el Manual de Onboarding (KYC) en PDF con instrucciones 
    para obtener Carpeta Tributaria, CMF Seguros y CMF Deudas.
    """
    logo_src = _get_logo_base64()
    
    img_tag = f'<img src="{logo_src}" width="150" style="margin-bottom: 20px;"/>' if logo_src else '<h2>FV Asesorías</h2>'

    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: a4 portrait;
                margin: 2cm;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                font-size: 11pt;
                color: #333333;
                line-height: 1.5;
            }}
            h1 {{ color: #1a365d; font-size: 18pt; text-align: center; border-bottom: 1px solid #1a365d; padding-bottom: 10px; }}
            h2 {{ color: #2b6cb0; font-size: 14pt; margin-top: 20px; }}
            h3 {{ color: #4a5568; font-size: 12pt; }}
            .step {{ background-color: #f7fafc; padding: 10px; border-left: 4px solid #3182ce; margin-bottom: 15px; }}
            .footer {{ text-align: center; font-size: 9pt; color: #718096; margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div style="text-align: center;">
            {img_tag}
        </div>
        
        <h1>Manual de Recopilación de Antecedentes</h1>
        <p>Estimado/a <strong>{cliente_nombre}</strong>,</p>
        <p>Para brindarle una asesoría patrimonial de excelencia y estructurar una planificación integral, necesitamos recopilar información oficial sobre su situación tributaria, financiera y de seguros. 
        Este manual le guiará paso a paso para descargar los documentos requeridos desde los portales oficiales del Estado (SII y CMF).</p>
        
        <h2>1. Carpeta Tributaria Regular (Servicio de Impuestos Internos - SII)</h2>
        <p>Este documento nos permite conocer su estructura de ingresos y participación en sociedades.</p>
        <div class="step">
            <b>Paso 1:</b> Ingrese a la página web del SII en <a href="https://homer.sii.cl/">www.sii.cl</a> y haga clic en "Mi SII" (arriba a la derecha).<br>
            <b>Paso 2:</b> Ingrese con su RUT y Clave Tributaria o Clave Única.<br>
            <b>Paso 3:</b> En el menú superior, vaya a <b>"Situación Tributaria"</b> > <b>"Carpeta Tributaria Electrónica"</b> > <b>"Generar Carpeta Tributaria"</b>.<br>
            <b>Paso 4:</b> Seleccione la opción <b>"Regular para Solicitar Créditos"</b>.<br>
            <b>Paso 5:</b> Haga clic en <b>"Generar PDF"</b>. Guarde el archivo descargado.
        </div>
        
        <h2>2. Informe de Deudas (Comisión para el Mercado Financiero - CMF)</h2>
        <p>Este informe detalla sus compromisos financieros actuales, permitiéndonos calcular su flujo de caja y evaluar oportunidades de refinanciamiento.</p>
        <div class="step">
            <b>Paso 1:</b> Ingrese al portal "Conoce tu Deuda" de la CMF en <a href="https://conocetudeuda.cmfchile.cl/">https://conocetudeuda.cmfchile.cl/</a>.<br>
            <b>Paso 2:</b> Ingrese con su RUT y Clave Única.<br>
            <b>Paso 3:</b> En la pantalla principal, busque el botón que dice <b>"Descargar CSV"</b> o "Exportar a Excel" (generalmente ubicado en la sección superior derecha de la tabla).<br>
            <b>Paso 4:</b> Descargue y guarde el archivo en formato CSV o Excel.
        </div>
        
        <h2>3. Certificado de Seguros (Comisión para el Mercado Financiero - CMF)</h2>
        <p>Este certificado nos indica qué seguros tiene contratados, vital para evaluar coberturas y evitar pagos duplicados o "seguros zombis".</p>
        <div class="step">
            <b>Paso 1:</b> Ingrese al portal "Conoce tu Seguro" de la CMF en <a href="https://www.conocetuseguro.cl/">www.conocetuseguro.cl</a>.<br>
            <b>Paso 2:</b> Inicie sesión utilizando su Clave Única.<br>
            <b>Paso 3:</b> Una vez dentro de su perfil, presione el botón <b>"Descargar Certificado (PDF)"</b>.<br>
            <b>Paso 4:</b> Guarde el documento PDF descargado.
        </div>
        
        <br>
        <p>Una vez que haya descargado estos tres documentos (1 PDF del SII, 1 CSV de Deudas CMF y 1 PDF de Seguros CMF), por favor envíelos por correo o Whatsapp a su asesor asignado. Su información será tratada con estricta confidencialidad bajo nuestros protocolos de seguridad.</p>
        
        <div class="footer">
            Generado automáticamente por FV Asesorías e Inversiones - Sistema Integral de Asesoría Patrimonial
        </div>
    </body>
    </html>
    """
    
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=result)
    
    if pisa_status.err:
        print("Error generating PDF KYC")
        return b""
        
    return result.getvalue()
    return result.getvalue()


def generate_succession_report_pdf(prospect_id: int) -> bytes:
    """
    Genera el Informe Ejecutivo de Planificación Sucesoria, Distribución Patrimonial
    y Sustento Legal en PDF para el cliente.
    """
    from src.osint.herencia import calculate_advanced_succession
    data = calculate_advanced_succession(prospect_id)
    if not data:
        return b""

    logo_src = _get_logo_base64()
    img_tag = f'<img src="{logo_src}" width="160" style="margin-bottom: 15px;"/>' if logo_src else '<h2>FV ASESORÍAS</h2>'

    tot = data["totales"]
    nombre_cliente = data["nombre"]
    rut_cliente = data["rut"]
    estado_prev = data["estado_previsional"]

    # Generar tabla de herederos y beneficiarios en HTML
    herederos_rows = ""
    for h in data["herederos_legales"]:
        est_txt = "Sí (Estudiante 18-24)" if h["es_estudiante"] else "No"
        herederos_rows += f"""
        <tr>
            <td>{h['nombre']}</td>
            <td>{h['relacion']}</td>
            <td>{h['edad']} años</td>
            <td>{est_txt}</td>
            <td>{h['asignacion_pct']}%</td>
        </tr>
        """

    beneficiarios_rows = ""
    for b in data["beneficiarios_sobrevivencia"]:
        est_txt = "Sí (Estudiante DL 3500 Art. 5)" if b["es_estudiante"] else "No"
        beneficiarios_rows += f"""
        <tr>
            <td>{b['nombre']}</td>
            <td>{b['relacion']}</td>
            <td>{b['edad']} años</td>
            <td>{b['fundamento']}</td>
        </tr>
        """

    # Generar tablas de detalles patrimoniales
    detalles = data.get("detalles", {})
    
    prop_rows = ""
    for p in detalles.get("propiedades", []):
        prop_rows += f"""
        <tr>
            <td>{p['alias']}</td>
            <td>{p['comuna']} (ROL {p['rol']})</td>
            <td>{p['valor_uf']:,.2f} UF</td>
            <td>{p['deuda_uf']:,.2f} UF</td>
            <td><span style="color: green; font-weight: bold;">0.00 UF (Desgravamen Ley 20.449)</span></td>
        </tr>
        """
    if not prop_rows:
        prop_rows = "<tr><td colspan='5' style='text-align:center;'>No hay propiedades registradas</td></tr>"

    inv_rows = ""
    for inv in detalles.get("inversiones", []):
        inv_rows += f"""
        <tr>
            <td>{inv['institucion']}</td>
            <td>{inv['activo']}</td>
            <td>{inv['tipo']}</td>
            <td>${inv['monto_clp']:,.0f} CLP</td>
        </tr>
        """
    if not inv_rows:
        inv_rows = "<tr><td colspan='4' style='text-align:center;'>No hay inversiones registradas</td></tr>"

    pol_rows = ""
    for pol in detalles.get("polizas", []):
        apv_txt = "Sí (Art. 42 bis LIR)" if pol['es_apv'] else "No"
        pol_rows += f"""
        <tr>
            <td>{pol['aseguradora']}</td>
            <td>{pol['tipo']}</td>
            <td>{pol['monto_uf']:,.2f} UF</td>
            <td>{pol['fecha'] or 'Pre-2022'}</td>
            <td>{apv_txt}</td>
        </tr>
        """
    if not pol_rows:
        pol_rows = "<tr><td colspan='5' style='text-align:center;'>No hay pólizas registradas</td></tr>"

    debt_rows = ""
    for d in detalles.get("deudas", []):
        debt_rows += f"""
        <tr>
            <td>{d['institucion']}</td>
            <td>{d['tipo']}</td>
            <td>${d['monto_actual']:,.0f} CLP</td>
            <td>${d['mora']:,.0f} CLP</td>
        </tr>
        """
    if not debt_rows:
        debt_rows = "<tr><td colspan='4' style='text-align:center;'>Sin deudas vigentes registradas en CMF</td></tr>"

    sustento_rows = ""
    for s in data["sustento_legal"]:
        sustento_rows += f"""
        <tr>
            <td><b>{s['norma']}</b></td>
            <td>{s['detalle']}</td>
        </tr>
        """

    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: a4 portrait;
                margin: 1.5cm;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                font-size: 9.5pt;
                color: #2d3748;
                line-height: 1.4;
            }}
            h1 {{ color: #1a365d; font-size: 16pt; text-align: center; border-bottom: 2px solid #1a365d; padding-bottom: 6px; margin-top: 0; }}
            h2 {{ color: #2b6cb0; font-size: 11.5pt; border-bottom: 1px solid #cbd5e0; padding-bottom: 4px; margin-top: 14px; }}
            .card {{ background-color: #f7fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0; margin-bottom: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 8px; margin-bottom: 12px; font-size: 9pt; }}
            th {{ background-color: #2b6cb0; color: white; padding: 5px; text-align: left; }}
            td {{ padding: 5px; border-bottom: 1px solid #e2e8f0; }}
            .highlight {{ color: #2b6cb0; font-weight: bold; }}
            .legal-box {{ background-color: #ebf8ff; border-left: 4px solid #3182ce; padding: 10px; margin-top: 10px; font-size: 9pt; }}
            .footer {{ text-align: center; font-size: 8pt; color: #a0aec0; margin-top: 20px; border-top: 1px solid #e2e8f0; padding-top: 6px; }}
        </style>
    </head>
    <body>
        <div style="text-align: center;">
            {img_tag}
        </div>
        
        <h1>Informe Executive Consolidated 360° & Planificación Sucesoria</h1>
        
        <div class="card">
            <b>Cliente:</b> {nombre_cliente} &nbsp;&nbsp;|&nbsp;&nbsp; <b>RUT:</b> {rut_cliente}<br>
            <b>Estado Previsional:</b> {estado_prev} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Fecha Emisión:</b> {datetime.date.today().strftime('%d/%m/%Y')}
        </div>

        <h2>1. Balance Consolidado: Masa Hereditaria v/s Activos Excluidos</h2>
        <table>
            <tr>
                <th>Categoría de Activo / Pasivo</th>
                <th>Monto (UF)</th>
                <th>Tratamiento Legal y Tributario</th>
            </tr>
            <tr>
                <td><b>Patrimonio Inmobiliario</b></td>
                <td>{tot['propiedades_uf']:,.2f} UF</td>
                <td>Ingresa a la Masa Hereditaria. Impuesto a la Herencia (Ley 16.271).</td>
            </tr>
            <tr>
                <td><b>Deuda Hipotecaria / Consumo</b></td>
                <td><span style="color: green; font-weight: bold;">0.00 UF (Extinguida)</span></td>
                <td><b>Extinción 100% por Seguro de Desgravamen</b> (Ley 20.449 & DFL 251). Los inmuebles pasan libres de deuda.</td>
            </tr>
            <tr>
                <td><b>Portafolio de Inversiones</b></td>
                <td>{tot['inversiones_uf']:,.2f} UF</td>
                <td>Masa Hereditaria. Exención especial de <b>4.000 UF</b> para Cuenta 2 AFP (Art. 72 DL 3500).</td>
            </tr>
            <tr>
                <td><b>Seguros de Vida</b></td>
                <td>{tot['seguros_exentos_uf']:,.2f} UF</td>
                <td>Fuera de Masa Hereditaria / Exentos (Circular N° 20 de 2022 SII & Art. 20 Ley 16.271).</td>
            </tr>
            <tr style="background-color: #edf2f7;">
                <td><b>MASA HEREDITARIA IMPONIBLE NETO</b></td>
                <td><b class="highlight">{tot['masa_hereditaria_imponible_uf']:,.2f} UF</b></td>
                <td>Base neta imponible para cálculo del Impuesto a las Herencias tras exenciones.</td>
            </tr>
        </table>

        <h2>2. Cartera Inmobiliaria y Extinción por Desgravamen</h2>
        <table>
            <tr>
                <th>Propiedad / Alias</th>
                <th>Ubicación / ROL</th>
                <th>Valor Comercial</th>
                <th>Deuda Bruta</th>
                <th>Estado Tras Desgravamen</th>
            </tr>
            {prop_rows}
        </table>

        <h2>3. Portafolio de Inversiones Consolidadas</h2>
        <table>
            <tr>
                <th>Institución</th>
                <th>Activo / Fondo</th>
                <th>Tipo Instrumento</th>
                <th>Monto Estimado</th>
            </tr>
            {inv_rows}
        </table>

        <h2>4. Cobertura de Seguros de Vida y Evaluación Ley 21.420</h2>
        <table>
            <tr>
                <th>Aseguradora</th>
                <th>Tipo Cobertura</th>
                <th>Capital Asegurado</th>
                <th>Fecha Contratación</th>
                <th>APV Póliza</th>
            </tr>
            {pol_rows}
        </table>

        <h2>5. Compromisos Financieros CMF</h2>
        <table>
            <tr>
                <th>Institución Financiera</th>
                <th>Tipo Crédito</th>
                <th>Monto Actual</th>
                <th>Mora</th>
            </tr>
            {debt_rows}
        </table>

        <h2>6. Herederos Forzosos y Cobertura de Pensión de Sobrevivencia</h2>
        <p>Conforme al <b>DL 3500 Art. 5 y 58</b>, los hijos estudiantes de 18 a 24 años mantienen su pensión de sobrevivencia:</p>
        <table>
            <tr>
                <th>Heredero / Beneficiario</th>
                <th>Relación</th>
                <th>Edad</th>
                <th>Estudiante 18-24</th>
                <th>% Asignación Legal</th>
            </tr>
            {herederos_rows}
        </table>

        <h2>7. Matriz de Citas y Sustento Legal por Artículo</h2>
        <table>
            <tr>
                <th style="width: 35%;">Norma / Artículo</th>
                <th style="width: 65%;">Aplicación al Caso</th>
            </tr>
            {sustento_rows}
        </table>

        <div class="legal-box">
            <b>💡 Opción EXCLUSIVA del Cónyuge en Póliza de APV (Régimen B):</b> Al fallecer el titular, <u>únicamente el cónyuge sobreviviente</u> cuenta con la facultad legal de elegir entre:<br>
            • <b>1. Traspasar / Sumar Ahorros a su propio APV</b>: Integrar los saldos previsionales a sus propios fondos de pensiones manteniendo el diferimiento tributario (Art. 42 bis LIR).<br>
            • <b>2. Retirar el dinero en efectivo (85% Líquido)</b>: Pagar un <b>Impuesto Único del 15%</b> (retenido por la Aseguradora/AFP según Art. 42 bis N° 4 LIR), quedando el capital <b>100% exento del Impuesto a la Herencia (Ley 16.271)</b>.<br>
            <i>(Esta opción tributaria de rescate directo con tasa del 15% es un derecho reservado exclusivamente para el cónyuge en pólizas APV, no aplicando a otros herederos)</i>.
        </div>

        <div class="footer">
            Documento confidencial generado por FV Asesorías e Inversiones - Sistema Senior de Asesoría Patrimonial
        </div>
    </body>
    </html>
    """

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=result)
    
    if pisa_status.err:
        print("Error generating Succession PDF")
        return b""
        
    return result.getvalue()
