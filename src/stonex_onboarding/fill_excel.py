import os
from openpyxl import load_workbook

TEMPLATE_PATH = "STONEX/PN - Datos apertura de cuenta Stonex (1).xlsx"

def safe_write(sheet, coord, value):
    """Escribe un valor en la celda, manejando el caso de que sea un MergedCell."""
    cell = sheet[coord]
    if type(cell).__name__ == 'MergedCell':
        for merged_range in sheet.merged_cells.ranges:
            if coord in merged_range:
                top_left = sheet.cell(row=merged_range.min_row, column=merged_range.min_col)
                top_left.value = value
                return
    else:
        cell.value = value

def generate_stonex_excel(data, output_filename="Onboarding_Stonex.xlsx"):
    """
    Rellena la plantilla de Stonex con los datos del formulario web.
    """
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"No se encontró la plantilla en {TEMPLATE_PATH}")

    wb = load_workbook(TEMPLATE_PATH)
    sheet = wb['Datos - solicitar a cliente']

    # Mapeo de celdas según el script de scratch
    # Perfilamiento de Riesgo
    safe_write(sheet, 'B3', data.get('horizonte_tiempo', ''))
    safe_write(sheet, 'B5', data.get('experiencia', ''))
    safe_write(sheet, 'B7', data.get('porcentaje_activos', ''))
    safe_write(sheet, 'B9', data.get('objetivos_inversion', ''))
    safe_write(sheet, 'B11', data.get('tolerancia_riesgo', ''))
    
    # Datos de Cuenta y Asesor
    safe_write(sheet, 'B15', 'Individual')
    safe_write(sheet, 'B18', data.get('rep_code', 'Asesor FV'))
    
    # Datos Personales
    safe_write(sheet, 'B19', data.get('nombre_completo', ''))
    safe_write(sheet, 'B54', data.get('pais_residencia', 'Chile'))
    safe_write(sheet, 'B60', data.get('tipo_documento', 'ID Nacional'))
    safe_write(sheet, 'B62', data.get('pais_emisor_doc', 'Chile'))
    safe_write(sheet, 'B66', data.get('nacionalidad', 'Chilena'))
    safe_write(sheet, 'B67', data.get('ciudadania', 'Chilena'))
    safe_write(sheet, 'B68', data.get('situacion_laboral', ''))
    safe_write(sheet, 'B69', data.get('ocupacion', ''))
    safe_write(sheet, 'B70', data.get('estado_civil', ''))
    safe_write(sheet, 'B72', data.get('pep', 'No'))
    
    # Datos financieros y de Inversión
    safe_write(sheet, 'B92', data.get('necesidad_liquidez', ''))
    safe_write(sheet, 'B93', data.get('ingresos_anuales', ''))
    safe_write(sheet, 'B95', data.get('activos_liquidos', ''))
    safe_write(sheet, 'B97', data.get('patrimonio_total', ''))
    safe_write(sheet, 'B98', data.get('aportes_adicionales', 'No'))
    safe_write(sheet, 'B101', data.get('tiempo_retiros', 'Más de 10 años'))
    
    safe_write(sheet, 'B103', data.get('pais_origen_fondos', 'Chile'))
    safe_write(sheet, 'B104', data.get('origen_fondos', ''))
    safe_write(sheet, 'B110', 'No Discrecional')
    safe_write(sheet, 'B113', 'ACAT')
    
    # Campos de texto libre
    safe_write(sheet, 'A109', data.get('monto_inversion', ''))
    safe_write(sheet, 'A111', data.get('fee_anual', '1.0%'))
    safe_write(sheet, 'A112', '0')
    
    # Guardar en la carpeta data/onboarding
    os.makedirs("data/onboarding", exist_ok=True)
    output_path = os.path.join("data/onboarding", output_filename)
    wb.save(output_path)
    
    return output_path
