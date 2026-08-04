import os
import datetime
from io import BytesIO
from xhtml2pdf import pisa
import base64

def _get_logo_base64(filename="fv_logo_vector_pure.svg"):
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    candidates = []
    if filename.endswith(".png") or filename.endswith(".jpg"):
        candidates.append(os.path.splitext(filename)[0] + ".svg")
    candidates.append(filename)
    
    name_map = {
        "fv_logo_principal_light.png": "fv_logo_vector_pure.svg",
        "fv_logo_principal_hd.png": "fv_logo_vector_pure.svg",
        "fv_emblem_3d_metallic.png": "fv_logo_vector_pure.svg",
        "altus_logo_minimalist_1780936005587.png": "altus_ai_logo_dark.svg",
        "Logo_ALTUS AI_Negativo.png": "altus_ai_logo_dark.svg",
        "Logo_ALTUS AI_Negativo.svg": "altus_ai_logo_dark.svg",
        "altus_ai_logo_dark.svg": "altus_ai_logo_dark.svg",
        "NUEVO LOGO FV.svg": "fv_logo_vector_pure.svg",
        "Logo_FV_Principal.svg": "fv_logo_vector_pure.svg",
        "fv_logo_vector_principal.svg": "fv_logo_vector_pure.svg"
    }
    if filename in name_map:
        candidates.insert(0, name_map[filename])
        
    search_dirs = [
        os.path.join(root_dir, "assets", "brand"),
        os.path.join(root_dir, "assets"),
        os.path.join(root_dir, "src", "web", "assets", "brand"),
        os.path.join(root_dir, "src", "web", "assets"),
    ]
    
    for cand in candidates:
        for d in search_dirs:
            p = os.path.join(d, cand)
            if os.path.exists(p):
                with open(p, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode('utf-8')
                    ext = "svg+xml" if cand.endswith(".svg") else ("png" if cand.endswith(".png") else "jpeg")
                    return f"data:image/{ext};base64,{encoded}"
    return ""

def generate_kyc_manual(cliente_nombre: str) -> bytes:
    """
    Genera el Manual de Onboarding (KYC) en PDF con instrucciones 
    para obtener Carpeta Tributaria, CMF Seguros y CMF Deudas,
    usando el logo oficial corporativo de FV Asesorías e Inversiones.
    """
    logo_src = _get_logo_base64("fv_logo_principal_light.png")
    if not logo_src:
        logo_src = _get_logo_base64("fv_emblem_3d_metallic.png")
    img_tag = f'<img src="{logo_src}" width="200" style="margin-bottom: 15px;"/>' if logo_src else '<h2>FV Asesorías e Inversiones</h2>'

    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: a4 portrait;
                margin: 1.8cm;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                font-size: 10.5pt;
                color: #2d3748;
                line-height: 1.5;
            }}
            .header-box {{ text-align: center; margin-bottom: 20px; }}
            h1 {{ color: #0f172a; font-size: 18pt; text-align: center; border-bottom: 2px solid #e5b154; padding-bottom: 8px; margin-top: 10px; }}
            h2 {{ color: #0A2342; font-size: 13pt; margin-top: 18px; margin-bottom: 8px; }}
            .kyc-intro {{ background-color: #f8fafc; padding: 12px 15px; border-left: 4px solid #e5b154; margin-bottom: 18px; border-radius: 4px; font-size: 10pt; }}
            .step {{ background-color: #f1f5f9; padding: 10px 14px; border-left: 4px solid #0A2342; margin-bottom: 12px; border-radius: 4px; line-height: 1.6; }}
            .security-box {{ background-color: #ecfdf5; border: 1px solid #a7f3d0; padding: 12px 15px; border-radius: 6px; margin-top: 20px; font-size: 9.5pt; color: #065f46; }}
            .legal-box {{ background-color: #f0f9ff; border: 1px solid #bae6fd; padding: 12px 15px; border-radius: 6px; margin-top: 12px; font-size: 9.5pt; color: #0369a1; }}
            .footer {{ text-align: center; font-size: 8.5pt; color: #64748b; margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 8px; }}
        </style>
    </head>
    <body>
        <div class="header-box">
            {img_tag}
        </div>
        
        <h1>Manual de Recopilación de Antecedentes (KYC)</h1>
        
        <p>Estimado/a <strong>{cliente_nombre}</strong>,</p>
        
        <div class="kyc-intro">
            <strong>💡 ¿Qué es el KYC (Know Your Customer)?</strong><br>
            Es el estándar internacional de debida diligencia patrimonial. Nos permite conocer con precisión la estructura de su patrimonio, grupo familiar e historial financiero para diseñar una estrategia integral 360° a la medida, exenta de sesgos y ajustada al marco tributario vigente en Chile.
        </div>
        
        <p>Este manual le guiará paso a paso para descargar los documentos oficiales requeridos desde los portales institucionales del Estado (SII y CMF):</p>
        
        <h2>1. Carpeta Tributaria Regular (Servicio de Impuestos Internos - SII)</h2>
        <div class="step">
            <b>Paso 1:</b> Ingrese a la página web del SII en <a href="https://homer.sii.cl/">www.sii.cl</a> y haga clic en "Mi SII".<br>
            <b>Paso 2:</b> Ingrese con su RUT y Clave Tributaria o Clave Única.<br>
            <b>Paso 3:</b> Vaya a <b>"Situación Tributaria"</b> > <b>"Carpeta Tributaria Electrónica"</b> > <b>"Generar Carpeta Tributaria"</b>.<br>
            <b>Paso 4:</b> Seleccione la opción <b>"Regular para Solicitar Créditos"</b>.<br>
            <b>Paso 5:</b> Haga clic en <b>"Generar PDF"</b> y guarde el archivo descargado.
        </div>
        
        <h2>2. Informe de Deudas (Comisión para el Mercado Financiero - CMF)</h2>
        <div class="step">
            <b>Paso 1:</b> Ingrese al portal oficial CMF en <a href="https://conocetudeuda.cmfchile.cl/">conocetudeuda.cmfchile.cl</a>.<br>
            <b>Paso 2:</b> Inicie sesión con su RUT y Clave Única.<br>
            <b>Paso 3:</b> Presione <b>"Descargar CSV / PDF"</b> para obtener su informe oficial de obligaciones consolidadas.
        </div>
        
        <h2>3. Certificado de Seguros (Comisión para el Mercado Financiero - CMF)</h2>
        <div class="step">
            <b>Paso 1:</b> Ingrese a <a href="https://www.conocetuseguro.cl/">www.conocetuseguro.cl</a>.<br>
            <b>Paso 2:</b> Inicie sesión con su Clave Única y presione <b>"Descargar Certificado (PDF)"</b>.
        </div>

        <div class="security-box">
            <strong>🔒 Resguardo de Información & Protocolos de Ciberseguridad:</strong><br>
            En FV Asesorías e Inversiones sus datos están protegidos bajo estándares de grado bancario (Cifrado AES-256 en reposo y TLS 1.3 en tránsito). Garantizamos confidencialidad absoluta bajo Secreto Patrimonial y estricto cumplimiento de la Ley N° 19.628 sobre Protección de la Vida Privada. Sus datos no son compartidos con terceros bajo ninguna circunstancia.
        </div>

        <div class="legal-box">
            <strong>⚖️ Validez Legal del Formulario KYC (Ley N° 19.799):</strong><br>
            Conforme a la Ley N° 19.799 sobre Documentos Electrónicos en Chile, la entrega de antecedentes y respuestas enviadas desde su correo electrónico personal o corporativo constituye una <strong>Firma Electrónica Simple (FES)</strong> válida y vinculante como declaración jurada de antecedentes de onboarding.
        </div>
        
        <div class="footer">
            FV Asesorías e Inversiones SpA • Multi-Family Office Digital impulsado por Altus AI
        </div>
    </body>
    </html>
    """
    
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=result)
    return result.getvalue() if not pisa_status.err else b""


def generate_succession_report_pdf(prospect_id: int) -> bytes:
    """
    Genera el Informe Ejecutivo Consolidado 360° & Planificación Sucesoria
    con doble columna UF/$ CLP, segregación previsional y estética corporativa.
    """
    from src.osint.herencia import calculate_advanced_succession
    data = calculate_advanced_succession(prospect_id)
    if not data:
        return b""

    logo_fv = _get_logo_base64("fv_logo_vector_pure.svg")
    logo_altus = _get_logo_base64("altus_ai_logo_dark.svg")

    img_fv_tag = f'<img src="{logo_fv}" width="200" style="vertical-align: middle;"/>' if logo_fv else '<strong style="color:#fff; font-size:16pt;">FV ASESORÍAS</strong>'
    img_altus_tag = f'<img src="{logo_altus}" width="70" style="vertical-align: middle; margin-left: 20px;"/>' if logo_altus else ''

    tot = data["totales"]
    nombre_cliente = data["nombre"]
    rut_cliente = data["rut"]
    estado_prev = data["estado_previsional"]
    uf_val = tot.get("uf_actual", 39650.0)

    # 1. HEREDEROS LEGALES Y DERECHOS PROPORCIONALES
    herederos_rows = ""
    for h in data["herederos_legales"]:
        est_txt = "Sí (Estudiante 18-24)" if h["es_estudiante"] else "No"
        herederos_rows += f"""
        <tr>
            <td><b>{h['nombre']}</b></td>
            <td>{h['relacion']}</td>
            <td>{h['edad']} años</td>
            <td>{est_txt}</td>
            <td><b style="color: #2b6cb0;">{h['asignacion_pct']}%</b></td>
            <td><b>{h['monto_uf']:,.2f} UF</b></td>
            <td><b>${h['monto_clp']:,.0f} CLP</b></td>
            <td style="color: #c53030;">{h['impuesto_uf']:,.2f} UF (${h['impuesto_clp']:,.0f})</td>
            <td style="color: #276749; font-weight: bold;">{h['liquido_uf']:,.2f} UF (${h['liquido_clp']:,.0f})</td>
        </tr>
        """
    if not herederos_rows:
        herederos_rows = "<tr><td colspan='9' style='text-align:center;'>Sin herederos registrados</td></tr>"

    # 2. PROPIEDADES DETALLADAS
    detalles = data.get("detalles", {})
    prop_rows = ""
    for p in detalles.get("propiedades", []):
        prop_rows += f"""
        <tr>
            <td><b>{p['alias']}</b></td>
            <td>{p['comuna']} (ROL {p['rol']})</td>
            <td>{p['valor_uf']:,.2f} UF<br><small style="color:#718096;">(${p['valor_clp']:,.0f} CLP)</small></td>
            <td>{p['deuda_uf']:,.2f} UF<br><small style="color:#718096;">(${p['deuda_clp']:,.0f} CLP)</small></td>
            <td><span style="color: #276749; font-weight: bold;">0.00 UF (Extinguida por Seguro de Desgravamen Ley 20.449)</span></td>
        </tr>
        """
    if not prop_rows:
        prop_rows = "<tr><td colspan='5' style='text-align:center;'>No hay bienes raíces registrados</td></tr>"

    # 3. INVERSIONES SEPARADAS: PREVISIONALES V/S NO PREVISIONALES
    inv_prev_rows = ""
    for inv in detalles.get("inversiones_previsionales", []):
        inv_prev_rows += f"""
        <tr>
            <td><b>{inv['institucion']}</b></td>
            <td>{inv['activo']}</td>
            <td><span style="background-color:#ebf8ff; color:#2b6cb0; padding:2px 6px; border-radius:4px; font-weight:bold;">{inv['tipo']}</span></td>
            <td>{inv['monto_uf']:,.2f} UF</td>
            <td><b>${inv['monto_clp']:,.0f} CLP</b></td>
        </tr>
        """
    if not inv_prev_rows:
        inv_prev_rows = "<tr><td colspan='5' style='text-align:center;'>No se registran inversiones previsionales (APV, Cuenta 2, AFP)</td></tr>"

    inv_noprev_rows = ""
    for inv in detalles.get("inversiones_no_previsionales", []):
        inv_noprev_rows += f"""
        <tr>
            <td><b>{inv['institucion']}</b></td>
            <td>{inv['activo']}</td>
            <td><span style="background-color:#edf2f7; color:#4a5568; padding:2px 6px; border-radius:4px;">{inv['tipo']}</span></td>
            <td>{inv['monto_uf']:,.2f} UF</td>
            <td><b>${inv['monto_clp']:,.0f} CLP</b></td>
        </tr>
        """
    if not inv_noprev_rows:
        inv_noprev_rows = "<tr><td colspan='5' style='text-align:center;'>No se registran inversiones no previsionales generales</td></tr>"

    # 4. PÓLIZAS
    pol_rows = ""
    for pol in detalles.get("polizas", []):
        apv_txt = "Sí (Art. 42 bis LIR)" if pol['es_apv'] else "No"
        pol_rows += f"""
        <tr>
            <td><b>{pol['aseguradora']}</b></td>
            <td>{pol['tipo']}</td>
            <td>{pol['monto_uf']:,.2f} UF</td>
            <td>${pol['monto_clp']:,.0f} CLP</td>
            <td>{pol['fecha'] or 'Pre-2022'}</td>
            <td><b>{apv_txt}</b></td>
        </tr>
        """
    if not pol_rows:
        pol_rows = "<tr><td colspan='6' style='text-align:center;'>No hay pólizas registradas</td></tr>"

    # 5. DEUDAS CMF
    debt_rows = ""
    for d in detalles.get("deudas", []):
        d_uf = d['monto_actual'] / uf_val if uf_val > 0 else 0
        debt_rows += f"""
        <tr>
            <td><b>{d['institucion']}</b></td>
            <td>{d['tipo']}</td>
            <td>${d['monto_actual']:,.0f} CLP</td>
            <td>{d_uf:,.2f} UF</td>
            <td style="color:#c53030;">${d['mora']:,.0f} CLP</td>
        </tr>
        """
    if not debt_rows:
        debt_rows = "<tr><td colspan='5' style='text-align:center;'>Sin deudas vigentes registradas en CMF</td></tr>"

    # SUSTENTO LEGAL
    sustento_rows = ""
    for s in data["sustento_legal"]:
        sustento_rows += f"""
        <tr>
            <td style="width: 32%;"><b>{s['norma']}</b></td>
            <td style="width: 68%;">{s['detalle']}</td>
        </tr>
        """

    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: a4 portrait;
                margin: 1.2cm;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                font-size: 9pt;
                color: #2d3748;
                line-height: 1.4;
            }}
            
            /* HEADER CORPORATIVO OFICIAL CON LOGOS */
            .header-bar {{
                background-color: #0f172a;
                padding: 16px 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .header-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .header-title-text {{
                color: #ffffff;
                font-size: 15pt;
                font-weight: bold;
                text-transform: uppercase;
                margin: 0;
                letter-spacing: 0.5px;
            }}
            .header-subtitle-text {{
                color: #f59e0b;
                font-size: 9.5pt;
                margin-top: 4px;
            }}

            /* PERFIL Y FICHA DE CLIENTE */
            .profile-card {{
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-left: 5px solid #2b6cb0;
                padding: 12px 16px;
                border-radius: 6px;
                margin-bottom: 16px;
            }}
            
            h2 {{ color: #1a365d; font-size: 11pt; border-bottom: 2px solid #2b6cb0; padding-bottom: 4px; margin-top: 18px; margin-bottom: 8px; text-transform: uppercase; }}
            
            table {{ width: 100%; border-collapse: collapse; margin-top: 6px; margin-bottom: 14px; font-size: 8.5pt; }}
            th {{ background-color: #1e293b; color: white; padding: 6px 8px; text-align: left; font-size: 8.5pt; }}
            td {{ padding: 6px 8px; border-bottom: 1px solid #e2e8f0; vertical-align: middle; }}
            
            .badge-gold {{ background-color: #fffbeb; color: #b45309; border: 1px solid #fef3c7; font-weight: bold; padding: 2px 6px; border-radius: 4px; }}
            .highlight-total {{ background-color: #ebf8ff; font-weight: bold; color: #2b6cb0; }}
            
            .legal-box {{ background-color: #f0f9ff; border-left: 4px solid #0369a1; padding: 12px; margin-top: 14px; font-size: 8.5pt; line-height: 1.45; }}
            .footer {{ text-align: center; font-size: 8pt; color: #718096; margin-top: 25px; border-top: 1px solid #e2e8f0; padding-top: 8px; }}
        </style>
    </head>
    <body>

        <!-- ENCABEZADO CORPORATIVO OFICIAL FV ASESORÍAS & ALTUS AI -->
        <div class="header-bar">
            <table class="header-table">
                <tr>
                    <td style="border:none; padding:0;">
                        {img_fv_tag}
                        {img_altus_tag}
                    </td>
                    <td style="border:none; padding:0; text-align:right;">
                        <div class="header-title-text">INFORME EXECUTIVE CONSOLIDADO 360°</div>
                        <div class="header-subtitle-text">Planificación Patrimonial, Sucesoria y Sustento Legal</div>
                    </td>
                </tr>
            </table>
        </div>

        <!-- FICHA DE DATOS PERSONALES DEL CLIENTE -->
        <div class="profile-card">
            <table style="margin:0; border:none;">
                <tr>
                    <td style="border:none; width:50%; padding:2px 0;"><b>Titular Patrimonial:</b> {nombre_cliente}</td>
                    <td style="border:none; width:50%; padding:2px 0;"><b>RUT:</b> {rut_cliente}</td>
                </tr>
                <tr>
                    <td style="border:none; padding:2px 0;"><b>Situación Laboral / Ocupación:</b> <span class="badge-gold">{estado_prev}</span></td>
                    <td style="border:none; padding:2px 0;"><b>Valor UF Referencial:</b> ${uf_val:,.2f} CLP &nbsp;|&nbsp; <b>Emisión:</b> {datetime.date.today().strftime('%d/%m/%Y')}</td>
                </tr>
            </table>
        </div>

        <!-- SECCIÓN 1: BALANCE CONSOLIDADO -->
        <h2>1. Balance Consolidado: Masa Hereditaria Imponible v/s Activos Excluidos</h2>
        <table>
            <tr>
                <th>Categoría de Activo / Pasivo</th>
                <th>Monto (UF)</th>
                <th>Monto Estimado ($ CLP)</th>
                <th>Tratamiento Legal y Tributario</th>
            </tr>
            <tr>
                <td><b>Patrimonio Inmobiliario (Bienes Raíces)</b></td>
                <td>{tot['propiedades_uf']:,.2f} UF</td>
                <td><b>${tot['propiedades_clp']:,.0f} CLP</b></td>
                <td>Ingresa a Masa Hereditaria. Impuesto a la Herencia (Ley 16.271). Deuda extinta 100% por desgravamen.</td>
            </tr>
            <tr>
                <td><b>Inversiones Previsionales (APV, Cuenta 2, AFP)</b></td>
                <td>{tot['inversiones_previsionales_uf']:,.2f} UF</td>
                <td><b>${tot['inversiones_previsionales_clp']:,.0f} CLP</b></td>
                <td>Masa Hereditaria. Beneficio especial de <b>exención de 4.000 UF</b> para Cuenta 2 AFP (Art. 72 DL 3500).</td>
            </tr>
            <tr>
                <td><b>Inversiones No Previsionales (Generales)</b></td>
                <td>{tot['inversiones_no_previsionales_uf']:,.2f} UF</td>
                <td><b>${tot['inversiones_no_previsionales_clp']:,.0f} CLP</b></td>
                <td>Masa Hereditaria General Afecta a Ley 16.271 tras exenciones generales.</td>
            </tr>
            <tr>
                <td><b>Seguros de Vida (Exentos Circular 20 SII)</b></td>
                <td>{tot['seguros_exentos_uf']:,.2f} UF</td>
                <td><b>${(tot['seguros_exentos_uf'] * uf_val):,.0f} CLP</b></td>
                <td>Fuera de Masa Hereditaria / Exentos de impuesto (Art. 20 Ley 16.271 & Circular 20 SII).</td>
            </tr>
            <tr class="highlight-total">
                <td><b>MASA HEREDITARIA IMPONIBLE NETO</b></td>
                <td><b>{tot['masa_hereditaria_imponible_uf']:,.2f} UF</b></td>
                <td><b>${tot['masa_hereditaria_imponible_clp']:,.0f} CLP</b></td>
                <td>Base imponible neta tras exención de 4.000 UF Cuenta 2 para cálculo de herencia legal.</td>
            </tr>
        </table>

        <!-- SECCIÓN 2: CARTERA INMOBILIARIA -->
        <h2>2. Cartera Inmobiliaria y Extinción por Desgravamen</h2>
        <table>
            <tr>
                <th>Propiedad / Alias</th>
                <th>Ubicación / ROL</th>
                <th>Valor Comercial</th>
                <th>Deuda Bruta Original</th>
                <th>Estado Tras Fallecimiento (Desgravamen)</th>
            </tr>
            {prop_rows}
        </table>

        <!-- SECCIÓN 3: PORTAFOLIO DE INVERSIONES -->
        <h2>3. Portafolio de Inversiones Consolidadas</h2>
        <div style="font-weight:bold; color:#2b6cb0; margin-top:6px; font-size:8.5pt;">3.1 Inversiones Previsionales (APV, Cuenta 2 AFP, Fondos Previsionales)</div>
        <table>
            <tr>
                <th>Institución</th>
                <th>Activo / Fondo</th>
                <th>Clasificación</th>
                <th>Monto (UF)</th>
                <th>Monto ($ CLP)</th>
            </tr>
            {inv_prev_rows}
        </table>

        <div style="font-weight:bold; color:#4a5568; margin-top:8px; font-size:8.5pt;">3.2 Inversiones No Previsionales (Acciones, DPF, Fondos Generales, Cripto)</div>
        <table>
            <tr>
                <th>Institución</th>
                <th>Activo / Fondo</th>
                <th>Clasificación</th>
                <th>Monto (UF)</th>
                <th>Monto ($ CLP)</th>
            </tr>
            {inv_noprev_rows}
        </table>

        <!-- SECCIÓN 4: SEGUROS DE VIDA -->
        <h2>4. Cobertura de Seguros de Vida y Evaluación Ley 21.420</h2>
        <table>
            <tr>
                <th>Aseguradora</th>
                <th>Tipo Cobertura</th>
                <th>Capital Asegurado (UF)</th>
                <th>Capital ($ CLP)</th>
                <th>Fecha Contratación</th>
                <th>APV Póliza</th>
            </tr>
            {pol_rows}
        </table>

        <!-- SECCIÓN 5: COMPROMISOS FINANCIEROS -->
        <h2>5. Compromisos Financieros CMF</h2>
        <table>
            <tr>
                <th>Institución Financiera</th>
                <th>Tipo Crédito</th>
                <th>Monto Actual ($ CLP)</th>
                <th>Monto (UF)</th>
                <th>Mora ($ CLP)</th>
            </tr>
            {debt_rows}
        </table>

        <!-- SECCIÓN 6: DISTRIBUCIÓN LEGAL DE MASA HEREDITARIA CON MONTOS PROPORCIONALES -->
        <h2>6. Distribución Legal de la Masa Hereditaria y Derechos Proporcionales</h2>
        <p style="font-size:8.5pt; color:#4a5568; margin-bottom:6px;">
            Conforme a las reglas del Código Civil y DL 3500, la masa imponible neta de <b>{tot['masa_hereditaria_imponible_uf']:,.2f} UF (${tot['masa_hereditaria_imponible_clp']:,.0f} CLP)</b> se asigna como sigue:
        </p>
        <table>
            <tr>
                <th>Heredero</th>
                <th>Parentesco</th>
                <th>Edad</th>
                <th>Estudiante</th>
                <th>% Asignación</th>
                <th>Asignación (UF)</th>
                <th>Asignación ($ CLP)</th>
                <th>Impuesto Est.</th>
                <th>Líquido a Recibir</th>
            </tr>
            {herederos_rows}
        </table>

        <!-- SECCIÓN 7: SUSTENTO LEGAL -->
        <h2>7. Matriz de Citas y Sustento Legal por Artículo</h2>
        <table>
            <tr>
                <th>Norma / Artículo</th>
                <th>Aplicación Específica al Caso</th>
            </tr>
            {sustento_rows}
        </table>

        <div class="legal-box">
            <b>💡 Opción EXCLUSIVA del Cónyuge en Póliza de APV (Régimen B):</b> Al fallecer el titular, <u>únicamente el cónyuge sobreviviente</u> cuenta con la facultad legal de elegir entre:<br>
            • <b>1. Traspasar / Sumar Ahorros a su propio APV</b>: Integrar los saldos previsionales a sus propios fondos manteniendo el diferimiento tributario (Art. 42 bis LIR).<br>
            • <b>2. Retirar el dinero en efectivo (85% Líquido)</b>: Pagar un <b>Impuesto Único del 15%</b> (retenido por la Aseguradora/AFP), quedando el capital <b>100% exento del Impuesto a la Herencia (Ley 16.271)</b>.<br>
            <i>(Derecho reservado exclusivamente para el cónyuge en pólizas APV, no aplicando a otros herederos)</i>.
        </div>

        <div class="footer">
            Documento confidencial generado por <b>FV Asesorías e Inversiones SpA</b> con tecnología <b>ALTUS AI</b>.
        </div>
    </body>
    </html>
    """

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=result)
    return result.getvalue() if not pisa_status.err else b""
