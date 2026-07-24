import os
import io
import base64
from datetime import datetime
from xhtml2pdf import pisa
import markdown

try:
    from src.database.connection import SessionLocal
    from src.database.models import Prospect
    def get_client_name(rut):
        if not rut: return "N/A"
        db = SessionLocal()
        try:
            # Match the exact rut format or allow some flexibility
            rut_clean = rut.replace('.', '').replace('-', '').lower()
            clientes = db.query(Prospect).all()
            for c in clientes:
                if c.rut and c.rut.replace('.', '').replace('-', '').lower() == rut_clean:
                    return c.nombre if c.nombre else f"RUT: {rut}"
            return f"RUT: {rut}"
        except:
            return f"RUT: {rut}"
        finally:
            db.close()
except ImportError:
    def get_client_name(rut):
        return f"RUT: {rut}"

def generar_pdf_analisis_integral(ticker, tech_opinion, fund_opinion, integral_opinion=None, market_consensus="N/A", is_generic=True, client_rut=None, target_price=None, chart_bytes=None):
    fecha_actual = datetime.now().strftime("%d-%m-%Y")
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Logos vectoriales (Regla de oro: usar SVG)
    logo_fv_path = os.path.join(root_dir, "assets", "NUEVO LOGO FV.svg")
    altus_logo_path = os.path.join(root_dir, "assets", "Logo_ALTUS AI_Principal_Fondo oscuro.svg")
    
    try:
        with open(logo_fv_path, "rb") as f:
            fv_b64 = "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode('utf-8')
    except:
        fv_b64 = ""
        
    try:
        with open(altus_logo_path, "rb") as f:
            altus_b64 = "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode('utf-8')
    except:
        altus_b64 = ""
    
    # Resolver nombre de destinatario
    if is_generic:
        destinatario = "Reporte de Mercado (Carácter General)"
    else:
        nombre_cliente = get_client_name(client_rut)
        destinatario = nombre_cliente
    
    import re
    if tech_opinion:
        tech_opinion = re.sub(r'## .*', '', tech_opinion)
    if fund_opinion:
        fund_opinion = re.sub(r'## .*', '', fund_opinion)

    # Manejar integral_opinion que ahora es un diccionario
    integral_html = ""
    recom_html = ""
    if integral_opinion and isinstance(integral_opinion, dict):
        conclusion = markdown.markdown(integral_opinion.get("conclusion", ""))
        recomendacion = integral_opinion.get("recomendacion", "N/A")
        conviccion = integral_opinion.get("conviccion", "N/A")
        justificacion = markdown.markdown(integral_opinion.get("justificacion", ""))
        
        # Color segun recomendacion
        color_rec = "#333"
        bg_rec = "#f1f5f9"
        if "COMPRAR" in recomendacion.upper():
            color_rec = "#15803d" # verde
            bg_rec = "#f0fdf4"
        elif "VENDER" in recomendacion.upper():
            color_rec = "#b91c1c" # rojo
            bg_rec = "#fef2f2"
        elif "MANTENER" in recomendacion.upper():
            color_rec = "#b45309" # naranjo
            bg_rec = "#fffbeb"
            
        recom_html = f'''
          <table style="width: 100%; margin-bottom: 10px; border: none;">
              <tr>
                  <td style="width: 48%; vertical-align: top; background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 10px;">
                      <h3 style="color: #475569; margin-top: 0; margin-bottom: 4px; font-size: 10pt; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px;">Consenso de Mercado</h3>
                      <div style="font-size: 8.5pt; color: #334155; margin-top: 4px; line-height: 1.3;">
                          {market_consensus}
                      </div>
                  </td>
                  <td style="width: 4%; border: none; padding: 0; margin: 0;"></td>
                  <td style="width: 48%; vertical-align: top; background-color: {bg_rec}; border: 1px solid {color_rec}; padding: 12px;">
                      <h3 style="color: {color_rec}; margin-top: 0; margin-bottom: 4px; font-size: 10.5pt; border-bottom: 1px solid {color_rec}; padding-bottom: 4px;">Posición Altus AI</h3>
                      <div style="font-size: 10pt; margin-top: 4px; line-height: 1.5;">
                          <strong style="font-size: 13pt; color: {color_rec};">{recomendacion}</strong><br>
                          <strong>Convicción:</strong> {conviccion}<br>
                          <div style="margin-top: 8px; color: #334155;">{justificacion}</div>
                      </div>
                  </td>
              </tr>
          </table>
          
          <div style="margin-bottom: 10px; background-color: #f0f9ff; padding: 15px; border-left: 4px solid #0369a1; page-break-inside: avoid;">
            <h2 style="color: #0369a1; margin-top: 0; margin-bottom: 8px; font-size: 12.5pt;">Conclusión Integral (Técnico + Fundamental)</h2>
            <div style="font-size: 11pt; line-height: 1.55; color: #1e293b;">{conclusion}</div>
        </div>
        '''
    elif integral_opinion and isinstance(integral_opinion, str):
        # Fallback si por alguna razon llega un string
        integral_html = f'''
          <div style="margin-bottom: 10px; background-color: #f0f9ff; padding: 15px; border-left: 4px solid #0369a1; page-break-inside: avoid;">
              <h2 style="color: #0369a1; margin-top: 0; margin-bottom: 8px; font-size: 12.5pt;">Conclusión Integral (Técnico + Fundamental)</h2>
              <div style="font-size: 11pt; line-height: 1.55; color: #1e293b;">{markdown.markdown(integral_opinion)}</div>
          </div>
          '''
        recom_html = ""

    # Convertir opiniones independientemente a HTML
    tech_html = markdown.markdown(tech_opinion if tech_opinion else "No se solicitó análisis técnico.", extensions=['extra', 'nl2br'])
    fund_html = markdown.markdown(fund_opinion if fund_opinion else "No se solicitó análisis fundamental.", extensions=['extra', 'nl2br'])

    target_html = ""
    if target_price and target_price != "N/A":
        target_html = f"""
        <div style="background-color: #104b3c; color: white; padding: 8px; text-align: center; font-size: 13pt; font-weight: bold; margin-bottom: 10px; border-radius: 5px;">
            Precio Objetivo (Consenso 12 Meses): {target_price}
        </div>"""

    chart_b64 = ""
    if chart_bytes:
        chart_b64 = "data:image/png;base64," + base64.b64encode(chart_bytes).decode('utf-8')

    contenido_html = f"""
    {target_html}
    
    {recom_html}
    {integral_html if not recom_html else ""}

    <div style="margin-bottom: 15px; page-break-before: always;">
        <h2 style="color: #104b3c; border-bottom: 2px solid #D4AF37; margin-bottom: 8px; font-size: 16pt;">Análisis Cuantitativo (Técnico)</h2>
        <div style="background-color: transparent; padding: 0;">
            {tech_html}
        </div>
    </div>

    <div style="margin-bottom: 15px; page-break-before: always;">
        <h2 style="color: #104b3c; border-bottom: 2px solid #D4AF37; margin-bottom: 8px; font-size: 16pt;">Análisis Corporativo (Fundamental)</h2>
        <div style="background-color: transparent; padding: 0;">
            {fund_html}
        </div>
    </div>
    
    <pdf:nextpage />
    
    <div style="margin-bottom: 25px;">
        <h1 style="color: #104b3c; border-bottom: 2px solid #D4AF37; margin-bottom: 20px; font-size: 20pt; text-align: left;">Anexos: Gráficos y Metodología</h1>
        
        {f'<div style="text-align: center; margin-bottom: 20px;"><img src="{chart_b64}" style="width: 100%; border: 1px solid #e2e8f0; border-radius: 5px;"></div>' if chart_b64 else ""}
        
        <div style="background-color: #f8fafc; padding: 15px; margin-bottom: 20px;">
            <h3 style="color: #104b3c; font-size: 14pt; margin-top: 0; margin-bottom: 10px;">Descripción de la Metodología</h3>
            <p><strong>Análisis Cuantitativo (Técnico):</strong> Examina el comportamiento histórico del precio y el volumen de un activo utilizando modelos matemáticos y estadísticos. Nuestro sistema emplea Inteligencia Artificial para identificar patrones algorítmicos, fuerza de tendencia y momentum, lo cual permite anticipar posibles puntos de entrada o salida con precisión probabilística.</p>
            <p><strong>Análisis Corporativo (Fundamental):</strong> Evalúa el valor intrínseco de una empresa analizando sus estados financieros, ventajas competitivas, márgenes operativos y entorno macroeconómico. La IA procesa y pondera esta información para determinar si el activo está subvaluado o sobrevaluado frente a sus perspectivas de crecimiento a largo plazo.</p>
        </div>

        <div style="background-color: #f8fafc; padding: 15px;">
            <h3 style="color: #104b3c; font-size: 14pt; margin-top: 0; margin-bottom: 10px;">Justificación de Indicadores Utilizados</h3>
            <p style="margin-bottom: 10px;">Nuestro modelo cuantitativo selecciona rigurosamente estos indicadores por las siguientes razones:</p>
            <ul>
                <li style="margin-bottom: 5px;"><strong>MACD (Moving Average Convergence Divergence):</strong> Es esencial para medir la fuerza subyacente y la dirección de la tendencia. Permite detectar divergencias y confirmar si el momentum está acelerando o agotándose.</li>
                <li style="margin-bottom: 5px;"><strong>RSI (Relative Strength Index):</strong> Cuantifica la magnitud de los cambios recientes en el precio para identificar condiciones de sobrecompra o sobreventa. Es crítico para evitar entradas tardías en el ciclo del mercado.</li>
                <li style="margin-bottom: 5px;"><strong>Bandas de Bollinger:</strong> Miden la volatilidad extrema. Cuando el precio perfora estas bandas, indica estadísticamente un evento atípico, ofreciendo señales claras de compresión o reversión inminente.</li>
            </ul>
        </div>
    </div>
    """

    # HTML TEMPLATE
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4 portrait;
                margin-top: 2cm;
                margin-bottom: 1.5cm;
                margin-left: 2cm;
                margin-right: 2cm;
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
                page-break-after: avoid;
            }}
            h3 {{
                color: #1a202c;
                font-size: 14px;
                margin-top: 20px;
                page-break-after: avoid;
            }}
            blockquote {{
                border-left: 3px solid #D4AF37;
                margin: 0;
                color: #475569;
                background-color: #f8fafc;
                padding: 10px 14px;
                margin-bottom: 12px;
                font-size: 10pt;
                line-height: 1.45;
            }}
            p {{
                margin-bottom: 10px;
                margin-top: 0;
                line-height: 1.45;
                text-align: justify;
                page-break-inside: avoid;
            }}
            ul, ol {{
                margin-top: 4px;
                margin-bottom: 10px;
                padding-left: 20px;
                line-height: 1.45;
            }}
            li {{
                margin-bottom: 4px;
                text-align: justify;
            }}
            .disclaimer {{
                font-size: 10px;
                color: #64748b;
                text-align: justify;
                border-top: 1px solid #e2e8f0;
                padding-top: 10px;
                margin-top: 30px;
                page-break-inside: avoid;
            }}
            .corp-desc {{
                background-color: #f8fafc;
                border-left: 3px solid #D4AF37; /* Altus Gold */
                padding: 12px;
                font-size: 9pt;
                margin-top: 20px;
                color: #374151;
                page-break-inside: avoid;
            }}
            strong, b {{
                color: #0f172a;
            }}
            .info-box {{
                background-color: #f8fafc;
                border-left: 4px solid #D4AF37;
                padding: 15px;
                margin-top: 20px;
                margin-bottom: 25px;
            }}
            p, li, div.metric {{
                page-break-inside: avoid;
            }}
        </style>
    </head>
    <body>
  
          <table style="width: 100%; border-bottom: 2px solid #0A2342; margin-bottom: 5px; padding-bottom: 2px;">
              <tr>
                  <td style="text-align: left; width: 40%; vertical-align: middle; border:none;">
                      <img src="{fv_b64}" width="190">
                  </td>
                  <td style="text-align: right; width: 60%; vertical-align: middle; border:none;">
                      <table style="width: 100%; border: none; margin: 0; padding: 0;">
                          <tr style="border: none; background-color: transparent;">
                              <td style="text-align: right; vertical-align: middle; border: none; padding-right: 12px;">
                                  <span style="font-size: 11pt; color: #0A2342; font-weight: bold;">Digital Family Office Analytics</span><br>
                                  <span style="font-size: 8pt; color: #6b7280;">Fecha de Emisión: {fecha_actual}</span>
                              </td>
                              <td style="text-align: right; width: 80px; vertical-align: middle; border: none; padding: 0;">
                                  <img src="{altus_b64}" width="65">
                              </td>
                          </tr>
                      </table>
                  </td>
              </tr>
          </table>
          
          <div style="text-align: right; font-size: 8pt; color: #6b7280; margin-bottom: 5px;">
              Reporte generado por <strong>Altus AI</strong>. Este documento es confidencial y para uso exclusivo de FV Asesorías e Inversiones y sus clientes. No constituye una oferta vinculante ni asesoría financiera garantizada.
          </div>
  
          <table style="width: 100%; background-color: #f8fafc; padding: 4px; margin-bottom: 5px;">
              <tr>
                  <td style="width: 50%; border-left: 3px solid #cbd5e1; padding-left: 10px;">
                      <strong>Atención a:</strong> {destinatario} <br>
                      <strong>Instrumento Analizado:</strong> {ticker}
                  </td>
                  <td style="width: 50%; border-left: 3px solid #cbd5e1; padding-left: 10px; vertical-align: top;">
                      <strong>Fecha:</strong> {fecha_actual} <br>
                  </td>
              </tr>
          </table>

        {contenido_html}

        <div class="disclaimer">
            <strong>Aviso Legal:</strong> Las visiones y proyecciones presentadas en este documento han sido procesadas mediante inteligencia artificial cuantitativa (Altus AI) cruzando múltiples visiones de mercado. Este documento no constituye una recomendación de inversión vinculante, sino una herramienta de información estratégica basada en cálculos algorítmicos. Los mercados son volátiles y las rentabilidades pasadas no garantizan retornos futuros. FV Asesorías e Inversiones limita su responsabilidad al análisis puramente matemático.
        </div>
        
        <div class="corp-desc">
            <strong>Sobre FV Asesorías e Inversiones</strong><br>
            Somos un Multi-Family Office Digital potenciado por <strong>Altus AI</strong>, nuestro Software Cuantitativo Privado. Combinamos la precisión algorítmica de la Inteligencia Artificial con la exclusividad de la banca privada para auditar portafolios, cruzar normativas tributarias complejas, incorporar información de valor para cada cliente y diseñar estrategias patrimoniales hiper-personalizadas de grado institucional.
        </div>
        
    </body>
    </html>
    """
    
    result_bytes = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content.encode('utf-8'), dest=result_bytes, encoding='utf-8')
    
    if pisa_status.err:
        return None
    return result_bytes.getvalue()
