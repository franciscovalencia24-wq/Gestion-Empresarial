import os

with open('src/web/analysis_hub_ui.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('?? Anlisis Tcnico', '📈 Análisis Técnico')
text = text.replace('?? Anlisis Tcnico y Fundamental (IA)', '🎯 Análisis Técnico y Fundamental (IA)')
text = text.replace('?? Hub de Anlisis de Activos (IA)', '🎯 Hub de Análisis de Activos (IA)')
text = text.replace('Evaluacin Integral', 'Evaluación Integral')
text = text.replace('Smbolo (Ticker)', 'Símbolo (Ticker)')
text = text.replace('Perodo de Anlisis', 'Período de Análisis')
text = text.replace('Anlisis Integral (Tcnico + Fundamental)', 'Análisis Integral (Técnico + Fundamental)')
text = text.replace('Solo Anlisis Tcnico (Quant)', 'Solo Análisis Técnico (Quant)')
text = text.replace('Solo Anlisis Fundamental', 'Solo Análisis Fundamental')
text = text.replace('ltimo Precio', 'Último Precio')
text = text.replace('Recomendacin', 'Recomendación')
text = text.replace('Generacin de Reporte', 'Generación de Reporte')
text = text.replace('Aos', 'Años')

# Handle the case where characters are actually Ãšltimo or ðŸ“‰ or others shown in the screenshot
text = text.replace('Ãšltimo Precio', 'Último Precio')
text = text.replace('ðŸ“‰ Análisis Técnico', '📈 Análisis Técnico')
text = text.replace('ðŸŽ¯ Hub de Análisis', '🎯 Hub de Análisis')
text = text.replace('ðŸŽ¯ Análisis Técnico', '🎯 Análisis Técnico')
text = text.replace('AÃ±os', 'Años')
text = text.replace('PerÃ\xadodo', 'Período')
text = text.replace('AnÃ¡lisis', 'Análisis')
text = text.replace('TÃ©cnico', 'Técnico')
text = text.replace('EvaluaciÃ³n', 'Evaluación')
text = text.replace('SÃ\xadmbolo', 'Símbolo')
text = text.replace('GeneraciÃ³n', 'Generación')
text = text.replace('RecomendaciÃ³n', 'Recomendación')

with open('src/web/analysis_hub_ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Text replaced!")
