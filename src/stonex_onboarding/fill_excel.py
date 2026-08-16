import os
from openpyxl import load_workbook

TEMPLATE_PATH = "STONEX/PN - Datos apertura de cuenta Stonex (1).xlsx"

def generate_stonex_excel(data, output_filename="Onboarding_Stonex.xlsx"):
    """
    Rellena la plantilla de Stonex con los datos del formulario web.
    """
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"No se encontró la plantilla en {TEMPLATE_PATH}")

    wb = load_workbook(TEMPLATE_PATH)
    sheet = wb['Datos - solicitar a cliente']

    # Mapeo de celdas según el script de scratch (simplificado para los datos más importantes)
    # Perfilamiento de Riesgo
    sheet['B3'] = data.get('horizonte_tiempo', '')
    sheet['B5'] = data.get('experiencia', '')
    sheet['B7'] = data.get('porcentaje_activos', '')
    sheet['B9'] = data.get('objetivos_inversion', '')
    sheet['B11'] = data.get('tolerancia_riesgo', '')
    
    # Datos de Cuenta y Asesor
    sheet['B15'] = 'Individual'
    sheet['B18'] = data.get('rep_code', 'Asesor FV')
    
    # Datos Personales
    sheet['B19'] = data.get('nombre_completo', '')
    sheet['B54'] = data.get('pais_residencia', 'Chile')
    sheet['B60'] = data.get('tipo_documento', 'ID Nacional')
    sheet['B62'] = data.get('pais_emisor_doc', 'Chile')
    sheet['B66'] = data.get('nacionalidad', 'Chilena')
    sheet['B67'] = data.get('ciudadania', 'Chilena')
    sheet['B68'] = data.get('situacion_laboral', '')
    sheet['B69'] = data.get('ocupacion', '')
    sheet['B70'] = data.get('estado_civil', '')
    sheet['B72'] = data.get('pep', 'No')
    
    # Datos financieros y de Inversión
    sheet['B92'] = data.get('necesidad_liquidez', '')
    sheet['B93'] = data.get('ingresos_anuales', '')
    sheet['B95'] = data.get('activos_liquidos', '')
    sheet['B97'] = data.get('patrimonio_total', '')
    sheet['B98'] = data.get('aportes_adicionales', 'No')
    sheet['B101'] = data.get('tiempo_retiros', 'Más de 10 años')
    
    sheet['B103'] = data.get('pais_origen_fondos', 'Chile')
    sheet['B104'] = data.get('origen_fondos', '')
    sheet['B110'] = 'No Discrecional'
    sheet['B113'] = 'ACAT' # Forzado a ACAT según la estrategia
    
    # Campos de texto libre
    sheet['A109'] = data.get('monto_inversion', '')
    sheet['A111'] = data.get('fee_anual', '1.0%')
    sheet['A112'] = '0' # Dealing Fee
    
    # Guardar en la carpeta data/onboarding
    os.makedirs("data/onboarding", exist_ok=True)
    output_path = os.path.join("data/onboarding", output_filename)
    wb.save(output_path)
    
    return output_path
