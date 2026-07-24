import os
import base64
import tempfile
from datetime import datetime
from xhtml2pdf import pisa
import pandas as pd
import matplotlib.pyplot as plt
import io
from PIL import Image, ImageDraw

def generar_pdf_apv(rut: str, nombre: str, sueldo: float, aporte: float, aporte_dc_anual: float, anos: int, 
                    rentabilidad: float, ahorro_anual: float, bono_estado: float, df_proy: pd.DataFrame) -> str:
    """Convierte los resultados de la simulación APV en un PDF corporativo con CSS elegante usando xhtml2pdf"""
    
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    logo_fv_path = os.path.join(root_dir, "src", "web", "assets", "NUEVO LOGO FV.png")
    altus_logo_path = os.path.join(root_dir, "altus_logo_minimalist_1780936005587.png")
    
    # Convertir imágenes a base64
    def get_rounded_logo(img_path, radius):
        try:
            im = Image.open(img_path).convert("RGBA")
            circle = Image.new('L', (radius * 2, radius * 2), 0)
            draw = ImageDraw.Draw(circle)
            draw.ellipse((0, 0, radius * 2 - 1, radius * 2 - 1), fill=255)
            alpha = Image.new('L', im.size, 255)
            w, h = im.size
            alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
            alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
            alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
            alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
            im.putalpha(alpha)
            
            img_byte_arr = io.BytesIO()
            im.save(img_byte_arr, format='PNG')
            return "data:image/png;base64," + base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        except:
            return ""

    try:
        with open(logo_fv_path, "rb") as f:
            fv_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')
    except:
        fv_b64 = ""
        
    altus_b64 = get_rounded_logo(altus_logo_path, radius=40)
    if not altus_b64:
        try:
            with open(altus_logo_path, "rb") as f:
                altus_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')
        except:
            altus_b64 = ""
        
    # Construir tabla HTML de proyección (solo cada 5 años para no saturar si son muchos años)
    filas_html = ""
    for idx, row in df_proy.iterrows():
        ano = int(row['Año'])
        if ano % 5 == 0 or ano == anos:
            ob = row['Ahorro Obligatorio (10%)']
            apv = row['APV Régimen A'] + row['APV Régimen B']
            dc = row['Depósito Convenido']
            filas_html += f"""
            <tr>
                <td style="text-align:center;">Año {ano}</td>
                <td style="text-align:right;">$ {ob:,.0f}</td>
                <td style="text-align:right;">$ {apv:,.0f}</td>
                <td style="text-align:right;">$ {dc:,.0f}</td>
                <td style="text-align:right; font-weight:bold;">$ {ob+apv+dc:,.0f}</td>
            </tr>
            """
            
    # Generar gráfico base64
    plt.figure(figsize=(9, 4.5))
    x = df_proy['Año']
    y1 = df_proy['Ahorro Obligatorio (10%)']
    y2 = df_proy['APV Régimen A']
    y3 = df_proy['APV Régimen B']
    y4 = df_proy['Depósito Convenido']
    
    # Paleta corporativa
    plt.stackplot(x, y1, y2, y3, y4, labels=['Ahorro Obligatorio', 'APV Reg. A', 'APV Reg. B', 'Dep. Convenido'], 
                  colors=['#2b6cb0', '#D4AF37', '#718096', '#38b2ac'], alpha=0.85)
    plt.legend(loc='upper left', frameon=False, fontsize=9)
    plt.xlabel('Años Restantes para Jubilación', fontsize=10)
    plt.ylabel('Patrimonio Acumulado (CLP)', fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.margins(x=0)
    
    # Formatear el eje Y
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f'${val:,.0f}'))
    
    plt.tight_layout()
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=200, bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    chart_b64 = "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode('utf-8')
            
    recomendacion = "Régimen B (Rebaja de Impuestos)" if ahorro_anual > bono_estado else "Régimen A (Bono del Estado)"
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        @page {{
            size: A4 portrait;
            margin: 1.5cm;
        }}
        body {{
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: 11pt;
            color: #2b3035;
            line-height: 1.5;
        }}
        .header-table {{
            width: 100%;
            margin-bottom: 20px;
            border-bottom: 3px solid #0A2342;
            padding-bottom: 10px;
        }}
        .corp-desc {{
            background-color: #f8fafc;
            border-left: 3px solid #D4AF37;
            padding: 12px;
            font-size: 9pt;
            margin-top: 30px;
            color: #374151;
        }}
        
        h1 {{
            color: #0A2342;
            font-size: 18pt;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        h2 {{
            color: #0A2342;
            font-size: 14pt;
            border-bottom: 1px solid #D4AF37;
            padding-bottom: 3px;
            margin-top: 20px;
        }}
        .metric-box {{
            background-color: #0A2342;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 5px solid #D4AF37;
        }}
        .metric-title {{ font-size: 10pt; color: #A0AEC0; }}
        .metric-value {{ font-size: 16pt; color: #D4AF37; font-weight: bold; margin-top: 5px; }}
        
        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 10pt;
        }}
        table.data-table th {{
            background-color: #0A2342;
            color: white;
            padding: 8px;
            text-align: center;
            border-bottom: 2px solid #D4AF37;
        }}
        table.data-table td {{
            padding: 8px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .footer {{
            font-size: 8pt;
            color: #718096;
            text-align: justify;
        }}
    </style>
    </head>
    <body>
    
        <table class="header-table">
            <tr>
                <td style="width: 40%; text-align: left; vertical-align: middle; border:none;">
                    <img src="{fv_b64}" width="140">
                </td>
                <td style="text-align: right; width: 60%; vertical-align: middle; border:none;">
                    <table style="width: 100%; border: none; margin: 0; padding: 0;">
                        <tr style="border: none; background-color: transparent;">
                            <td style="text-align: right; vertical-align: middle; border: none; padding-right: 12px;">
                                <span style="font-size: 11pt; color: #0A2342; font-weight: bold;">Digital Family Office Analytics</span><br>
                                <span style="font-size: 8pt; color: #6b7280;">Powered by</span>
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
        
        <h1>Reporte Cuantitativo: Estrategia Ahorros Previsionales</h1>
        <p style="color:#718096; font-size: 10pt; margin-top: -10px;">Fecha de Análisis: {datetime.now().strftime('%d/%m/%Y')}</p>
        
        <table style="width:100%; margin-bottom:15px; background-color:#f8fafc; padding:10px; border-left: 3px solid #cbd5e1;">
            <tr>
                <td width="50%" style="padding: 5px;"><strong>Cliente:</strong> {nombre if nombre else 'No especificado'}</td>
                <td width="50%" style="padding: 5px;"><strong>RUT:</strong> {rut if rut else 'No especificado'}</td>
            </tr>
            <tr>
                <td width="50%" style="padding: 5px;"><strong>Sueldo Bruto Mensual:</strong> $ {sueldo:,.0f} CLP</td>
                <td width="50%" style="padding: 5px;"><strong>Aporte APV Proyectado:</strong> $ {aporte:,.0f} CLP/mes</td>
            </tr>
            <tr>
                <td width="50%" style="padding: 5px;"><strong>Aporte DC Anual:</strong> $ {aporte_dc_anual:,.0f} CLP/año</td>
                <td width="50%" style="padding: 5px;"><strong>Horizonte de Inversión:</strong> {anos} años</td>
            </tr>
            <tr>
                <td width="50%" style="padding: 5px;"><strong>Rentabilidad Nominal Esperada:</strong> {rentabilidad * 100:.1f}% anual</td>
                <td width="50%" style="padding: 5px;"></td>
            </tr>
        </table>
        
        <h2>Impacto Tributario Inmediato</h2>
        <p>Análisis del beneficio fiscal que genera el aporte voluntario a la pensión.</p>
        
        <table style="width:100%;">
            <tr>
                <td style="width: 48%; padding-right: 10px;">
                    <div class="metric-box">
                        <div class="metric-title">Beneficio Régimen B (Rebaja de Impuestos)</div>
                        <div class="metric-value">$ {ahorro_anual:,.0f} CLP / año</div>
                    </div>
                </td>
                <td style="width: 4%;">&nbsp;</td>
                <td style="width: 48%;">
                    <div class="metric-box" style="background-color: #1A202C;">
                        <div class="metric-title">Beneficio Régimen A (Bono del Estado)</div>
                        <div class="metric-value">$ {bono_estado:,.0f} CLP / año</div>
                    </div>
                </td>
            </tr>
        </table>
        
        <div style="background-color:#e6fffa; padding: 10px; border-left: 4px solid #38b2ac; margin-top: 10px; margin-bottom:20px;">
            <strong style="color:#234e52;">Recomendación del Modelo:</strong> Basado estrictamente en la matemática de su tramo impositivo actual, se sugiere optar por <strong>{recomendacion}</strong> para maximizar el beneficio fiscal.
        </div>
        
        <pdf:nextpage />
        
        <h2>Proyección Patrimonial a Largo Plazo</h2>
        <p>Evolución estimada del saldo en la cuenta de ahorro para el retiro (Muestra quinquenal).</p>
        
        <table class="data-table">
            <thead>
                <tr>
                    <th>Período</th>
                    <th>Saldo Obligatorio</th>
                    <th>Total APV (A+B)</th>
                    <th>Depósito Convenido</th>
                    <th>Patrimonio Total Acumulado</th>
                </tr>
            </thead>
            <tbody>
                {filas_html}
            </tbody>
        </table>
        
        <div style="margin-top: 20px; text-align: center;">
            <img src="{chart_b64}" style="width: 100%;">
        </div>
        
        <div style="margin-top: 30px; margin-bottom: 30px;" class="footer">
            <strong>Aviso Legal y Descargo de Responsabilidad:</strong><br>
            Este reporte ha sido generado mediante los modelos cuantitativos de Altus AI. Esta es una simulación basada en parámetros fijos, tasas proyectadas constantes y topes imponibles vigentes. No constituye una promesa de rentabilidad futura ni garantiza resultados idénticos, ya que los mercados financieros y la legislación tributaria están sujetos a cambios. FV Asesorías e Inversiones proporciona este documento únicamente con fines informativos y de planificación estratégica.
        </div>
        
        <div class="corp-desc">
            <strong>Sobre FV Asesorías e Inversiones</strong><br>
            Somos un Multi-Family Office Digital potenciado por <strong>Altus AI</strong>, nuestro Software Cuantitativo Privado. Combinamos la precisión algorítmica de la Inteligencia Artificial con la exclusividad de la banca privada para auditar portafolios, cruzar normativas tributarias complejas, incorporar información de valor para cada cliente y diseñar estrategias patrimoniales hiper-personalizadas de grado institucional.
        </div>
        
    </body>
    </html>
    """
    
    # Generar PDF en el temp folder
    tmp_pdf_path = os.path.join(tempfile.gettempdir(), f"Reporte_APV_{rut if rut else 'Anonimo'}_{datetime.now().strftime('%H%M%S')}.pdf")
    
    with open(tmp_pdf_path, "wb") as pdf_file:
        pisa.CreatePDF(
            src=html_template,
            dest=pdf_file,
            encoding='UTF-8'
        )
        
    return tmp_pdf_path
