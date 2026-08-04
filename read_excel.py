import openpyxl
wb = openpyxl.load_workbook(r'C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\PRINCIPAL\PRODUCTOS\SEGURO DE VIDA CON AHORRO PREFERENTE\Formulario_Cliente_DPS.xlsx', data_only=True)
for ws in wb.worksheets:
    print(f"\n--- {ws.title} ---")
    for row in ws.iter_rows(min_row=1, max_col=3):
        if row[0].value:
            v1 = str(row[0].value).replace("\n", " ")
            v2 = str(row[1].value).replace("\n", " ") if len(row) > 1 and row[1].value else ""
            v3 = str(row[2].value).replace("\n", " ") if len(row) > 2 and row[2].value else ""
            print(f"Row {row[0].row}: {v1} | {v2} | {v3}")
