import sys
import os
sys.path.append(os.path.abspath("."))

from src.osint.indicadores import get_utm_today, get_uf_today
from src.utils.simulators.reliquidacion_simulator import ReliquidacionSimulator

utm = get_utm_today()
uf = get_uf_today()
print(f'UTM actual: {utm}')
print(f'UF actual: {uf}')

sim = ReliquidacionSimulator(uta_anual_clp=utm * 12, uf_actual=uf)
sueldo_anual = 112953114
sueldo_mensual = sueldo_anual / 12

afp_name = list(sim.comisiones_afp.keys())[0]
print(f'AFP por defecto: {afp_name} ({sim.comisiones_afp[afp_name]*100}%)')

desc = sim.calcular_renta_tributable(sueldo_mensual, afp_name, 7.0, tipo_afiliado='No pensionado', descuento_cesantia=True)

print(f'Sueldo Bruto Mensual: {sueldo_mensual:,.0f}')
print(f'AFP: {desc["afp_obligatorio"]:,.0f}')
print(f'Comision AFP: {desc["comision_afp"]:,.0f}')
print(f'Salud: {desc["salud"]:,.0f}')
print(f'Cesantia: {desc["cesantia"]:,.0f}')
print(f'Total Descuentos: {desc["total_descuentos"]:,.0f}')
print(f'Renta Tributable Mensual: {desc["renta_tributable_mensual"]:,.0f}')

base_anual = desc['renta_tributable_mensual'] * 12
print(f'Base Imponible Anual: {base_anual:,.0f}')

estimated_tax = sim.calcular_igc(base_anual)
print(f'Impuesto Estimado: {estimated_tax:,.0f}')
