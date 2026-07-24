import tempfile
import io
from datetime import datetime
from xhtml2pdf import pisa
import matplotlib.pyplot as plt

def generate_reliquidacion_pdf(data: dict, output_path: str):
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    
    # --- GENERAR GRÁFICO DE CASCADA (WATERFALL) ---
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7, 4), facecolor='#1A202C')
    ax.set_facecolor('#1A202C')
    
    ingresos_brutos = data["renta_bruta_anual"]
    ganancias_cap = data.get("ganancias_capital", 0)
    descuentos = data["descuentos_legales"]
    rebaja_55bis = data["rebaja_55bis"]
    retiro_apv = data.get("retiro_apvb_anual", 0)
    apv_anual = data["aporte_apv"]
    base_final = data["renta_neta"]
    
    # Categorías y valores para el Waterfall
    categories = ['Sueldo Bruto', 'Ganancias Cap.', 'Desc. Legales', 'Hipotecario (55 Bis)', 'Retiro APV', 'Aporte APV', 'Base Imponible']
    values = [ingresos_brutos, ganancias_cap, -descuentos, -rebaja_55bis, retiro_apv, -apv_anual, base_final]
    
    # Barras
    bottom = 0
    colors = ['#38A169', '#38A169', '#E53E3E', '#DD6B20', '#38A169', '#E53E3E', '#3182CE']
    
    for i, (cat, val) in enumerate(zip(categories, values)):
        if val < 0:
            ax.bar(cat, val, bottom=bottom, color=colors[i], edgecolor='white', linewidth=1)
            bottom += val
        else:
            if i == 6: # Última barra desde cero
                bottom = 0
            ax.bar(cat, val, bottom=bottom, color=colors[i], edgecolor='white', linewidth=1)
            bottom += val if i != 6 else 0

    ax.set_ylabel('Monto (CLP)', color='white')
    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='x', colors='white', rotation=25)
    for spine in ax.spines.values():
        spine.set_edgecolor('#4A5568')
        
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"${x:,.0f}"))
    plt.title('Impacto de Rebajas y APV en la Base Imponible', color='white', pad=20)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
    buf.seek(0)
    import base64
    grafico_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    import os
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    logo_fv_path = os.path.join(root_dir, "src", "web", "assets", "NUEVO LOGO FV.png")
    altus_logo_path = os.path.join(root_dir, "altus_logo_minimalist_1780936005587.png")
    
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

    # HTML TEMPLATE
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
                @frame footer_frame {{
                    -pdf-frame-content: footer_content;
                    left: 50pt; width: 512pt; top: 772pt; height: 20pt;
                }}
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                color: #333333;
                line-height: 1.5;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
                border-bottom: 2px solid #104b3c;
                padding-bottom: 10px;
            }}
            .header img {{
                width: 200px;
            }}
            h1 {{
                color: #104b3c;
                font-size: 20px;
                text-align: center;
                margin-top: 20px;
            }}
            h2 {{
                color: #1a202c;
                font-size: 16px;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 5px;
                margin-top: 25px;
            }}
            .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                font-size: 12px;
            }}
            .info-table th, .info-table td {{
                border: 1px solid #cbd5e1;
                padding: 8px;
                text-align: left;
            }}
            .info-table th {{
                background-color: #f8fafc;
                color: #475569;
                width: 50%;
            }}
            .highlight-box {{
                background-color: #f0fdf4;
                border-left: 5px solid #22c55e;
                padding: 15px;
                margin: 20px 0;
            }}
            .highlight-box h3 {{
                color: #166534;
                margin: 0 0 10px 0;
                font-size: 16px;
            }}
            .chart-container {{
                text-align: center;
                margin: 20px 0;
                background-color: #1A202C;
                padding: 10px;
                border-radius: 8px;
            }}
            .chart-container img {{
                width: 100%;
                max-width: 500px;
            }}
            .disclaimer {{
                font-size: 10px;
                color: #64748b;
                text-align: justify;
                border-top: 1px solid #e2e8f0;
                padding-top: 10px;
            }}
            .corp-desc {{
                background-color: #f8fafc;
                border-left: 3px solid #D4AF37; /* Altus Gold */
                padding: 12px;
                font-size: 9pt;
                margin-top: 20px;
                color: #374151;
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
            Análisis procesado cuantitativamente por <strong>Altus AI</strong> para uso exclusivo de FV Asesorías e Inversiones
        </div>

        <h1>Reporte Cuantitativo: Simulador de Reliquidación Anual</h1>

        <table style="width:100%; margin-bottom:15px; background-color:#f8fafc; padding:10px; border-left: 3px solid #cbd5e1;">
            <tr>
                <td width="50%" style="padding: 5px;"><strong>Cliente:</strong> {data.get("nombre", "No especificado")}</td>
                <td width="50%" style="padding: 5px;"><strong>Fecha:</strong> {fecha_actual}</td>
            </tr>
            <tr>
                <td width="50%" style="padding: 5px;"><strong>RUT:</strong> {data.get("rut", "No especificado")}</td>
                <td width="50%" style="padding: 5px;"><strong>Holgura APV Max.:</strong> ${data.get("holgura_monto", 0):,.0f} CLP</td>
            </tr>
        </table>

        <h2>1. Resumen de Ingresos e Impuestos</h2>
        <table class="info-table">
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
            <tr>
                <th>Base Imponible (Pre-APV)</th>
                <td>${data.get("renta_bruta", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>Retiro APV Régimen B (Suma a la base)</th>
                <td>${data.get("retiro_apvb_anual", 0):,.0f} CLP</td>
            </tr>
            <tr>
                <th>Total Retenciones e Impuestos Pagados</th>
                <td>${data.get("retenciones", 0):,.0f} CLP</td>
            </tr>
        </table>

        <pdf:nextpage />
        <h2>2. Optimización Tributaria</h2>
        <div class="highlight-box">
            <h3>Resultado Operación Renta</h3>
            <p><strong>Aporte APV Realizado (Régimen B):</strong> ${data.get("aporte_apv", 0):,.0f} CLP</p>
            <p><strong>Base Imponible Optimizada Final:</strong> ${data.get("renta_neta", 0):,.0f} CLP</p>
            <p><strong>Impuesto Global Complementario (IGC):</strong> ${data.get("igc_optimizado", 0):,.0f} CLP</p>
            <p><strong>(-) Impuesto Único Retiro APV B ({data.get("tasa_impuesto_unico", 0):.1f}%):</strong> ${data.get("impuesto_unico_retiro", 0):,.0f} CLP</p>
            <p style="font-size: 16px; margin-top: 10px;">
                <strong>{'Devolución a favor' if data.get("saldo_final", 0) > 0 else 'Monto a Pagar'}:</strong> 
                <span style="color: {'#15803d' if data.get("saldo_final", 0) > 0 else '#b91c1c'}; font-weight: bold;">
                    ${abs(data.get("saldo_final", 0)):,.0f} CLP
                </span>
            </p>
            <p style="margin-top: 5px; font-size: 13px; color: #166534;">
                <em>El APV Régimen B generó un beneficio tributario neto de ${data.get("beneficio_apv", 0):,.0f} CLP.</em>
            </p>
        </div>
        
        <h2>3. Recomendación Algorítmica (Altus AI)</h2>
        <p style="font-size: 13px; color: #334155; padding: 10px; border-left: 3px solid #3b82f6; background-color: #eff6ff;">
            <strong>Análisis de Eficiencia Tributaria:</strong> {data.get("holgura_mensaje", "")}
        </p>

        <pdf:nextpage />
        <h2>4. Análisis Visual de la Base Imponible</h2>
        <div class="chart-container">
            <img src="data:image/png;base64,{grafico_base64}">
        </div>

        <div class="disclaimer">
            <strong>Aviso Legal:</strong> Este documento es una simulación proyectada generada mediante algoritmos matemáticos e inteligencia artificial (Altus AI) basada en los tramos de Impuesto Global Complementario y UTM/UTA referenciales. No constituye asesoría tributaria vinculante, ni una declaración formal ante el Servicio de Impuestos Internos (SII). Los valores finales pueden variar por fluctuaciones inflacionarias (UF), ajustes legales o cambios en la normativa tributaria chilena. FV Asesorías e Inversiones limita su responsabilidad al cálculo matemático proyectado.
        </div>
        
        <div class="corp-desc">
            <strong>Sobre FV Asesorías e Inversiones</strong><br>
            Somos un Multi-Family Office Digital potenciado por <b>Altus AI</b>, nuestro Software Cuantitativo Privado. Combinamos la precisión algorítmica de la Inteligencia Artificial con la exclusividad de la banca privada para auditar portafolios, cruzar normativas tributarias complejas, incorporar información de valor para cada cliente y diseñar estrategias patrimoniales hiper-personalizadas de grado institucional.
        </div>

        <div id="footer_content" style="text-align: right; font-size: 9px; color: #94a3b8;">
            Generado por Altus AI - FV Asesorías e Inversiones - Página <pdf:pagenumber>
        </div>

    </body>
    </html>
    """
    
    with open(output_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)

    if pisa_status.err:
        raise Exception("Error al generar el PDF de reliquidación.")

    return output_path
