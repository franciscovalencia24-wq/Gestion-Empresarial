import os

with open('src/web/analysis_hub_ui.py', 'rb') as f:
    text_bytes = f.read()

text = text_bytes.decode('utf-8', errors='replace')

# Basic U+FFFD replacements
text = text.replace('ltimo Precio', 'Último Precio')
text = text.replace('Anlisis', 'Análisis')
text = text.replace('Tcnico', 'Técnico')
text = text.replace('Evaluacin', 'Evaluación')
text = text.replace('Generacin', 'Generación')
text = text.replace('Recomendacin', 'Recomendación')
text = text.replace('Perodo', 'Período')
text = text.replace('Smbolo', 'Símbolo')
text = text.replace('Aos', 'Años')
text = text.replace('ltimo', 'Último')

text = text.replace('\ufffdltimo Precio', 'Último Precio')
text = text.replace('An\ufffdlisis', 'Análisis')
text = text.replace('T\ufffdcnico', 'Técnico')
text = text.replace('Evaluaci\ufffdn', 'Evaluación')
text = text.replace('Generaci\ufffdn', 'Generación')
text = text.replace('Recomendaci\ufffdn', 'Recomendación')
text = text.replace('Per\ufffdodo', 'Período')
text = text.replace('S\ufffdmbolo', 'Símbolo')
text = text.replace('A\ufffdos', 'Años')
text = text.replace('\ufffdltimo', 'Último')

# Double utf-8 replacements
text = text.replace('ðŸ“‰', '📈')
text = text.replace('Ãšltimo', 'Último')
text = text.replace('ðŸŽ¯', '🎯')
text = text.replace('AÃ±os', 'Años')
text = text.replace('PerÃ\xadodo', 'Período')
text = text.replace('AnÃ¡lisis', 'Análisis')
text = text.replace('TÃ©cnico', 'Técnico')
text = text.replace('EvaluaciÃ³n', 'Evaluación')
text = text.replace('SÃ\xadmbolo', 'Símbolo')
text = text.replace('GeneraciÃ³n', 'Generación')
text = text.replace('RecomendaciÃ³n', 'Recomendación')

# Sometimes the diamond question marks were literal '?'
text = text.replace('?? An', '🎯 An')
text = text.replace('?? Hub', '🎯 Hub')

with open('src/web/analysis_hub_ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Brute-force encoding fix applied.")
