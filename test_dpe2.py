import re
import ast

rows = [
    "['09/2025', 'Pago Electronico Cotizacion Adicional', '13/10/2025', '$43.195', 'A', '$3.401.197', '79.578.8', '80-8']",
    "['09/2025', 'Pago Electronico Prima de Seguro de\\nInvalidez y Sobrevivencia (SIS)', '13/10/2025', '$63.943', 'A', '$3.401.197', '79.578.8', '80-8']",
    "['09/2025', 'Pago Electronico Cotizacion\\nObligatoria', '13/10/2025', '$343.521', 'A', '$3.401.197', '79.578.8', '80-8']",
    "['09/2025', 'Cotizaciones de comisiones de\\nAfiliados Independientes TGR', '29/05/2026', '$733', 'A', '$57.688', '16.188.8', '21-4']",
    "['09/2025', 'Cotizacion obligatoria pago\\nindependiente por transferencia TGR', '29/05/2026', '$5.769', 'A', '$57.688', '16.188.8', '21-4']",
]

# We can parse them using ast.literal_eval if they are valid python lists
for row_str in rows:
    try:
        row = ast.literal_eval(row_str)
        if len(row) >= 7 and row[0] and re.match(r"\d{2}/\d{4}", row[0]):
            periodo = row[0].replace('/', '-')
            tipo = str(row[1]).replace('\n', ' ')
            monto_str = str(row[3]).replace('$', '').replace('.', '')
            renta_str = str(row[5]).replace('$', '').replace('.', '')
            rut1 = str(row[6]).replace('.', '')
            rut2 = str(row[7]).replace('-', '')
            rut = f"{rut1}-{rut2}"
            
            if 'obligatoria' in tipo.lower() or 'cotizacion' in tipo.lower():
                print(f"Periodo: {periodo}, Renta: {renta_str}, Monto: {monto_str}, RUT: {rut}, Tipo: {tipo}")
    except Exception as e:
        print(e)
