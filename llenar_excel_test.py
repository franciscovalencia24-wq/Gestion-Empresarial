import openpyxl

wb = openpyxl.load_workbook(r'C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\PRINCIPAL\PRODUCTOS\SEGURO DE VIDA CON AHORRO PREFERENTE\Formulario_Cliente_DPS.xlsx')

# Llenar Sheet 1
ws1 = wb["1. Datos Personales"]
ws1['B3'] = "Gonzalo"
ws1['B4'] = "Bremer"
ws1['B5'] = "Gómez"
ws1['B6'] = "7012917-5"
ws1['B7'] = "22/12/1955"
ws1['B8'] = "Contador Auditor"
ws1['B9'] = "ARANDA & BREMER EST SPA"
ws1['B10'] = "Servicios Contables"
ws1['B11'] = "Socio"
ws1['B12'] = "Oficina"
ws1['B13'] = "Santiago"
ws1['B14'] = "MASVIDA"

# Llenar Sheet 2
ws2 = wb["2. Hábitos y Actividades"]
ws2['B4'] = "Sí"
ws2['C4'] = "Enfermedades Catastróficas"
ws2['B5'] = "No"
ws2['B6'] = "No"
ws2['B7'] = "No"
ws2['B8'] = "Sí"
ws2['C8'] = "Vino, muy esporádico"
ws2['B9'] = "No"
ws2['B10'] = "No"
ws2['B11'] = "No"

# Llenar Sheet 3
ws3 = wb["3. Antecedentes Médicos"]
ws3['B4'] = "180"
ws3['B5'] = "80"
ws3['B6'] = "No"
ws3['B7'] = "Normal"

for i in range(11, 16):
    ws3[f'B{i}'] = "No"

for i in range(20, 31):
    ws3[f'B{i}'] = "No"

out_file = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\PRINCIPAL\PRODUCTOS\SEGURO DE VIDA CON AHORRO PREFERENTE\Formulario_Cliente_DPS_test.xlsx"
wb.save(out_file)
print(f"Excel de prueba guardado en: {out_file}")
