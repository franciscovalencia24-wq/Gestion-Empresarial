from src.utils.simulators.reliquidacion_simulator import ReliquidacionSimulator
from src.utils.pdf_generator_reliquidacion import generate_reliquidacion_pdf
import os

sim = ReliquidacionSimulator()
# Escenario 1: Pensionado con Retiro APV B
res1 = sim.simular_operacion_renta(
    sueldo_anual_bruto=0,
    afp_name='Habitat',
    pct_salud=7.0,
    honorarios_anuales=10000000,
    retencion_sueldos=0,
    retencion_honorarios=1375000,
    apv_b_anual=0,
    retiro_apvb_anual=5000000,
    es_pensionado=True
)
print('Prueba Pensionado:')
print(f"  IGC original: {res1['igc_original']}")
print(f"  IGC optimizado: {res1['igc_optimizado']}")
print(f"  Tasa Impuesto Unico: {res1['tasa_impuesto_unico']}%")
print(f"  Impuesto Unico a Pagar: {res1['impuesto_unico_retiro']}")

# Escenario 2: Activo con Retiro APV B
res2 = sim.simular_operacion_renta(
    sueldo_anual_bruto=36000000,
    afp_name='Habitat',
    pct_salud=7.0,
    honorarios_anuales=0,
    retencion_sueldos=2500000,
    retencion_honorarios=0,
    apv_b_anual=0,
    retiro_apvb_anual=10000000,
    es_pensionado=False
)
print('\nPrueba Activo (No Pensionado):')
print(f"  IGC original: {res2['igc_original']}")
print(f"  Tasa Impuesto Unico: {res2['tasa_impuesto_unico']}%")
print(f"  Impuesto Unico a Pagar: {res2['impuesto_unico_retiro']}")

# Probar exportar PDF
data_pdf = {
    'nombre': 'Juan Perez',
    'rut': '12.345.678-9',
    'renta_bruta_anual': res2['renta_bruta_anual'],
    'descuentos_legales': res2['descuentos_legales_anuales'],
    'rebaja_55bis': res2['rebaja_55bis'],
    'renta_bruta': res2['base_imponible_pre_apv'],
    'igc_original': res2['igc_original'],
    'retenciones': res2['total_retenciones'],
    'aporte_apv': 0,
    'retiro_apvb_anual': res2['retiro_apvb_anual'],
    'renta_neta': res2['base_imponible_optimizada'],
    'igc_optimizado': res2['igc_optimizado'],
    'tasa_impuesto_unico': res2['tasa_impuesto_unico'],
    'impuesto_unico_retiro': res2['impuesto_unico_retiro'],
    'saldo_final': res2['saldo_optimizado'],
    'beneficio_apv': res2['beneficio_neto_apv'],
    'holgura_mensaje': 'Todo OK',
    'holgura_monto': 1000000
}
pdf_path = 'test_pdf.pdf'
generate_reliquidacion_pdf(data_pdf, pdf_path)
if os.path.exists(pdf_path):
    print(f'\nExito: PDF Generado en {pdf_path}')
