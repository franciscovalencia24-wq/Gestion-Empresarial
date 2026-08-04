from src.utils.simulators.reliquidacion_simulator import ReliquidacionSimulator
import os

sim = ReliquidacionSimulator()

print("--- TEST 1: TRABAJADOR DEPENDIENTE (NO PENSIONADO) CON GANANCIAS ---")
res1 = sim.simular_operacion_renta(
    sueldo_anual_bruto=36000000,
    afp_name='Habitat',
    pct_salud=7.0,
    honorarios_anuales=0,
    retencion_sueldos=0,
    retencion_honorarios=0,
    apv_b_anual=0,
    tipo_afiliado="No pensionado",
    ganancias_capital=20000000 # Empuja la base imponible arriba
)
print(f"Base Imponible: {res1['base_imponible_pre_apv']}")
print(f"Tope APV B Anual (UF): {600 * sim.uf_actual}")
print(f"Holgura Optima: {res1['holgura_apv']['holgura_optima_clp']}")
print(f"Mensaje: {res1['holgura_apv']['mensaje']}\n")


print("--- TEST 2: SUELDO EMPRESARIAL TOPADO ---")
res2 = sim.simular_operacion_renta(
    sueldo_anual_bruto=36000000,
    afp_name='Habitat',
    pct_salud=7.0,
    honorarios_anuales=0,
    retencion_sueldos=0,
    retencion_honorarios=0,
    apv_b_anual=0,
    tipo_afiliado="Sueldo Empresarial"
)
# The mandatory AFP contribution for 36M is roughly 36M * 10% = 3.6M. So the limit should be 3.6M instead of 600 UF (~22.8M)
print(f"Base Imponible: {res2['base_imponible_pre_apv']}")
print(f"Holgura Optima Esperada (aprox): 3.6M")
print(f"Holgura Optima Real: {res2['holgura_apv']['holgura_optima_clp']}")
print(f"Mensaje: {res2['holgura_apv']['mensaje']}\n")

print("--- TEST 3: PENSIONADO NO COTIZANTE ---")
res3 = sim.simular_operacion_renta(
    sueldo_anual_bruto=36000000,
    afp_name='Habitat',
    pct_salud=7.0,
    honorarios_anuales=0,
    retencion_sueldos=0,
    retencion_honorarios=0,
    apv_b_anual=0,
    retiro_apvb_anual=1000000,
    tipo_afiliado="Pensionado no cotizante"
)
print(f"Descuentos Legales (AFP debería ser 0): {res3['descuentos_legales_anuales']}")
print(f"Impuesto Unico Retiro (Tasa Pura): {res3['impuesto_unico_retiro']}")
