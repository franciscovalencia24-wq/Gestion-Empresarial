import os

with open('src/web/analysis_hub_ui.py', 'rb') as f:
    raw_bytes = f.read()

# We will try decoding using cp1252, then encoding back to utf-8 if the file was double encoded.
try:
    # If the file was saved as UTF-8 but contains double-encoded characters like ðŸ“‰
    text = raw_bytes.decode('utf-8')
    
    # Check if double encoded
    if 'ðŸ' in text or 'Ãš' in text or 'AÃ±os' in text:
        text = text.encode('cp1252').decode('utf-8')
    
    # Also fix some replacements if there's regular bad encoding
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

    # Fix the replacements if they are using the diamond question mark character \ufffd
    text = text.replace('?? An\ufffdlisis T\ufffdcnico', '📈 Análisis Técnico')
    text = text.replace('?? An\ufffdlisis T\ufffdcnico y Fundamental (IA)', '🎯 Análisis Técnico y Fundamental (IA)')
    text = text.replace('?? Hub de An\ufffdlisis de Activos (IA)', '🎯 Hub de Análisis de Activos (IA)')
    text = text.replace('Evaluaci\ufffdn Integral', 'Evaluación Integral')
    text = text.replace('S\ufffدمbolo (Ticker)', 'Símbolo (Ticker)')
    text = text.replace('S\ufffdmbolo (Ticker)', 'Símbolo (Ticker)')
    text = text.replace('Per\ufffdodo de An\ufffdlisis', 'Período de Análisis')
    text = text.replace('An\ufffdlisis Integral (T\ufffdcnico + Fundamental)', 'Análisis Integral (Técnico + Fundamental)')
    text = text.replace('Solo An\ufffdlisis T\ufffdcnico (Quant)', 'Solo Análisis Técnico (Quant)')
    text = text.replace('Solo An\ufffdlisis Fundamental', 'Solo Análisis Fundamental')
    text = text.replace('\ufffdltimo Precio', 'Último Precio')
    text = text.replace('Recomendaci\ufffdn', 'Recomendación')
    text = text.replace('Generaci\ufffdn de Reporte', 'Generación de Reporte')
    text = text.replace('A\ufffdos', 'Años')

    with open('src/web/analysis_hub_ui.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed encoding via python script.")
except Exception as e:
    print(f"Error: {e}")
