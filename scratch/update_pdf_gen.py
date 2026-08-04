import os
import re

with open('src/utils/pdf_generator_analysis.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update ALTUS logo
text = text.replace('Logo_ALTUS AI_Principal_Fondo oscuro.png', 'Logo_ALTUS AI_Principal.png')

# 2. Add Target Price into the function signature and Markdown
if 'target_price=None' not in text:
    text = text.replace('def generar_pdf_analisis_integral(ticker, tech_opinion, fund_opinion, is_generic=True, client_rut=None):',
                        'def generar_pdf_analisis_integral(ticker, tech_opinion, fund_opinion, is_generic=True, client_rut=None, target_price=None):')

    # Inject into the Markdown
    markdown_replacement = """
## 1. Veredicto Técnico

{tech_opinion if tech_opinion else 'No se solicitó análisis técnico.'}

[SALTO]

## 2. Veredicto Fundamental

{fund_opinion if fund_opinion else 'No se solicitó análisis fundamental.'}

"""
    # Replace "1. Veredicto Cuantitativo (Análisis Técnico)"
    text = re.sub(r'## 1\. Veredicto Cuantitativo \(Análisis Técnico\).*?\[SALTO\]',
                  r'## 1. Veredicto Técnico\n\n{tech_opinion if tech_opinion else \'No se solicitó análisis técnico.\'}\n\n[SALTO]', 
                  text, flags=re.DOTALL)
    
    # Replace "2. Veredicto Corporativo (Análisis Fundamental)"
    text = re.sub(r'## 2\. Veredicto Corporativo \(Análisis Fundamental\).*?("""|\'\'\')',
                  r'## 2. Veredicto Fundamental\n\n{fund_opinion if fund_opinion else \'No se solicitó análisis fundamental.\'}\n\n' +
                  r'**Precio Objetivo (Consenso 12 Meses):** ' +
                  r'{target_price if target_price else "N/A"} ' +
                  r'*(Fuente: Consenso de Wall Street)*\n\1',
                  text, flags=re.DOTALL)

# 3. Add FV Legal disclaimer
disclaimer = """
            .disclaimer {
                font-size: 8px;
                color: #64748b;
                text-align: justify;
                border-top: 1px solid #e2e8f0;
                padding-top: 10px;
                margin-top: 30px;
                page-break-inside: avoid;
            }
"""
# Replace the footer text
text = re.sub(r'Reporte generado y certificado por.*?Altus AI.*?para uso exclusivo de FV Asesor.*?as e Inversiones',
              'Reporte generado por <strong>Altus AI</strong>. Este documento es confidencial y para uso exclusivo de FV Asesorías e Inversiones y sus clientes. No constituye una oferta vinculante ni asesoría financiera garantizada.', text, flags=re.IGNORECASE)

with open('src/utils/pdf_generator_analysis.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("PDF template updated")
