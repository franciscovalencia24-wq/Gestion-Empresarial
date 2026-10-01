import pdfplumber
import re
import json

tmp_path = r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\certificado.pdf'
with pdfplumber.open(tmp_path) as pdf:
    full_text = ''
    for page in pdf.pages:
        tables = page.extract_tables()
        if tables:
            for table in tables:
                for row in table:
                    full_text += str(row) + '\n'

pattern_full = re.compile(r"\['(\d{2}/\d{4})',\s*'(.*?)',.*?'\$([\d\.]+)',\s*'[A-Z]',\s*'\$([\d\.]+)'\]")
native_filas = []
for match in pattern_full.finditer(full_text):
    periodo = match.group(1).replace('/', '-')
    tipo_mov = match.group(2)
    cotizacion_str = match.group(3).replace('.', '')
    renta_str = match.group(4).replace('.', '')
    
    if 'Obligatoria' in tipo_mov:
        native_filas.append({
            'periodo': periodo,
            'rut_pagador': 'Math-Parser',
            'renta_imponible': int(renta_str),
            'monto_cotizacion_obligatoria': int(cotizacion_str)
        })

print('Found matches:', len(native_filas))
if len(native_filas) > 0:
    print(native_filas[:5])
else:
    print('No native matches, printing some extracted text:')
    print(full_text[:1000])
