import os
import re

with open('src/web/analysis_hub_ui.py', 'rb') as f:
    raw_bytes = f.read()

text = raw_bytes.decode('utf-8', errors='replace')

text = re.sub(r'.\ufffdltimo Precio', 'Último Precio', text)
text = re.sub(r'T\ufffdcnico y Fundamental', 'Técnico y Fundamental', text)
text = re.sub(r'An\ufffdlisis', 'Análisis', text)
text = re.sub(r'T\ufffdcnico', 'Técnico', text)
text = re.sub(r'S\ufffdmbolo', 'Símbolo', text)
text = re.sub(r'S\ufffدمbolo', 'Símbolo', text)
text = re.sub(r'Evaluaci\ufffdn', 'Evaluación', text)
text = re.sub(r'Generaci\ufffdn', 'Generación', text)
text = re.sub(r'Recomendaci\ufffdn', 'Recomendación', text)
text = re.sub(r'Per\ufffdodo', 'Período', text)
text = re.sub(r'A\ufffdos', 'Años', text)
text = re.sub(r'A\ufffdo', 'Año', text)

text = text.replace('??', '🎯')
text = text.replace('Y"% ', '📈 ')
text = text.replace('Y"S ', '📊 ')
text = text.replace('ðŸ“‰', '📈')
text = text.replace('Ãšltimo', 'Último')
text = text.replace('AÃ±os', 'Años')
text = text.replace('SÃ\xadmbolo', 'Símbolo')
text = text.replace('AnÃ¡lisis', 'Análisis')
text = text.replace('TÃ©cnico', 'Técnico')
text = text.replace('EvaluaciÃ³n', 'Evaluación')

with open('src/web/analysis_hub_ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced all with regex!")
