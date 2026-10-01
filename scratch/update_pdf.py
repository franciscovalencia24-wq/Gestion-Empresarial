import re

file_path = r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\utils\pdf_generator.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace def signature
sig_pattern = r'def generate_succession_report_pdf\(prospect_id: int\) -> bytes:'
sig_replacement = 'def generate_succession_report_pdf(prospect_id: int, report_type: str = "Detallado") -> bytes:'
content = re.sub(sig_pattern, sig_replacement, content)

# Replace the HTML assembly part. We need to find where the final HTML is built.
# Let's search for "</body>" and inject the AI Recommendations before it.
recommendations_html = '''
    <!-- [HITO 3] RECOMENDACIONES ESTRATÉGICAS AI -->
    <h2>6. Motor de Recomendaciones Estratégicas AI</h2>
    <div class="summary-box">
        <ul style="margin: 0; padding-left: 20px;">
            <li style="margin-bottom: 8px;"><b>Optimización Tributaria:</b> Se recomienda revisar la estructura de las propiedades de inversión para aprovechar beneficios DFL-2 y evaluar el uso de un seguro con cuenta de inversión (APV/CUI) para diferir impuestos.</li>
            <li style="margin-bottom: 8px;"><b>Estructura Societaria:</b> Dado el patrimonio neto actual, constituir una Sociedad de Inversiones Familiar (Family Office) podría mejorar la eficiencia tributaria (VPP) en el traspaso intergeneracional.</li>
            <li style="margin-bottom: 8px;"><b>Gestión de Riesgo:</b> Las deudas actuales representan una baja carga financiera. Evaluar el uso de apalancamiento estratégico para adquirir activos con ROE superior al costo de deuda.</li>
        </ul>
    </div>
'''

html_pattern = r'(</body>\s*</html>)'
html_replacement = recommendations_html + r'\n\1'
content = re.sub(html_pattern, html_replacement, content)

# Save
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated pdf_generator.py")
