import re
import json
from collections import defaultdict
from datetime import datetime

with open(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\scratch\habitat_extracted_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# find all table rows using regex on the format: ['MM/YYYY', ..., '$monto', ...]
agrupado = defaultdict(int)

# regex for ['MM/YYYY', '...', '...', '$Monto', 'B', '$Renta']
pattern = re.compile(r"\['(\d{2}/\d{4})',.*?'\$([\d\.]+)',\s*'[A-Z]',\s*'\$([\d\.]+)'\]")

for match in pattern.finditer(text):
    # Only consider 'Obligatoria' rows to prevent double counting 'Adicional' or 'SIS'
    row_text = match.group(0)
    
    # We need to find if 'Obligatoria' is near this row. Since the regex only captures part, we can search the original text
    start_idx = match.start()
    # The row in pdfplumber looks like: ['08/2026', 'Pago Electronico Cotizacion\nObligatoria', ...]
    # So we can just capture the whole list
    # Let's adjust the regex to capture the full row
    pass

# New regex to capture the whole list row
pattern_full = re.compile(r"\['(\d{2}/\d{4})',\s*'(.*?)',.*?'\$([\d\.]+)',\s*'[A-Z]',\s*'\$([\d\.]+)'\]")
for match in pattern_full.finditer(text):
    periodo = match.group(1).replace('/', '-')
    tipo_movimiento = match.group(2)
    cotizacion = match.group(3).replace('.', '')
    renta = match.group(4).replace('.', '')
    
    if "Obligatoria" in tipo_movimiento:
        agrupado[periodo] += int(renta)

print(f"Total meses encontrados en tablas: {len(agrupado)}")

# Load UF history
with open(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\data\uf_historica.json", "r", encoding="utf-8") as f:
    uf_data = json.load(f)

current_date = datetime.now()
total_devolucion = 0
meses_exceso = 0

TOPE_UF = {
    2026: 84.3, 2025: 84.3, 2024: 84.3, 2023: 81.6, 2022: 81.6,
    2021: 81.6, 2020: 80.2, 2019: 79.3, 2018: 78.3
}

print("\nCálculo matemático (Últimos 60 meses):")
for periodo, renta_total in sorted(agrupado.items(), key=lambda x: (x[0].split('-')[1], x[0].split('-')[0]), reverse=True):
    month, year = map(int, periodo.split('-'))
    
    # 60 months filter
    period_date = datetime(year, month, 1)
    months_diff = (current_date.year - period_date.year) * 12 + (current_date.month - period_date.month)
    if months_diff > 60:
        continue

    # Get UF by finding a matching YYYY-MM key
    uf_value = 0
    prefix = f"{year}-{str(month).zfill(2)}"
    for k, v in uf_data.items():
        if k.startswith(prefix):
            uf_value = float(v)
            break
            
    if uf_value == 0:
        uf_value = 38000 # fallback
        
    tope_uf = TOPE_UF.get(year, 81.6)
    tope_clp = tope_uf * uf_value
    
    if renta_total > tope_clp:
        exceso_imponible = renta_total - tope_clp
        devolucion = exceso_imponible * 0.10
        total_devolucion += devolucion
        meses_exceso += 1
        
        # Print a few months to debug
        if meses_exceso <= 5:
            print(f"[{periodo}] Renta Total: ${renta_total:,} | Tope: ${tope_clp:,.0f} | Devolución: ${devolucion:,.0f}")
        
print(f"Meses con exceso (dentro de 60 meses): {meses_exceso}")
print(f"Devolución total estimada matemática: ${int(total_devolucion):,} CLP".replace(',', '.'))
