from dataclasses import dataclass
from typing import List, Dict, Optional
from src.utils.simulators.reliquidacion_simulator import ReliquidacionSimulator

@dataclass
class DepositoCuenta2:
    fecha: str
    monto_clp: float
    monto_uf: float

class Cuenta2Simulator:
    def __init__(self, uta_anual_clp: float = 793000.0, uf_actual: float = 38000.0):
        self.uf_actual = uf_actual
        # Usamos el simulador de reliquidación para los cálculos de IGC
        self.reliquidador = ReliquidacionSimulator(uta_anual_clp=uta_anual_clp, uf_actual=uf_actual)
        
    def calcular_rentabilidad_real(self, saldo_actual_clp: float, depositos: List[DepositoCuenta2]) -> dict:
        """
        Calcula la ganancia de capital real en Cuenta 2 descontando la inflación (costo corregido en UF).
        Solo tributa la rentabilidad real.
        """
        if not depositos:
            return {
                "saldo_actual_clp": saldo_actual_clp,
                "costo_historico_uf": 0,
                "costo_historico_clp_corregido": 0,
                "aporte_nominal_clp": 0,
                "inflacion_acumulada_clp": 0,
                "rentabilidad_nominal_clp": 0,
                "rentabilidad_real_clp": 0
            }
            
        total_uf_depositado = sum(d.monto_uf for d in depositos)
        aporte_nominal_clp = sum(d.monto_clp for d in depositos)
        
        costo_historico_corregido_clp = total_uf_depositado * self.uf_actual
        
        # Inflación es la diferencia entre el costo corregido y el aporte nominal
        inflacion_acumulada_clp = costo_historico_corregido_clp - aporte_nominal_clp
        
        rentabilidad_nominal_clp = saldo_actual_clp - aporte_nominal_clp
        
        # La ganancia de capital real es lo que excede al costo corregido por inflación
        rentabilidad_real_clp = max(0, saldo_actual_clp - costo_historico_corregido_clp)
        
        return {
            "saldo_actual_clp": saldo_actual_clp,
            "costo_historico_uf": total_uf_depositado,
            "costo_historico_clp_corregido": costo_historico_corregido_clp,
            "aporte_nominal_clp": aporte_nominal_clp,
            "inflacion_acumulada_clp": inflacion_acumulada_clp,
            "rentabilidad_nominal_clp": rentabilidad_nominal_clp,
            "rentabilidad_real_clp": rentabilidad_real_clp
        }
        
    def evaluar_estrategia_retiro(
        self,
        saldo_actual_clp: float,
        rentabilidad_real_clp: float,
        monto_a_retirar_clp: float,
        aplicar_exencion_herencia: bool = True
    ) -> dict:
        """
        Evalúa el impacto de retirar un monto específico y la recomendación de dejar 4.000 UF
        exentas de herencia en la AFP según el DL 3500.
        """
        # Exención de herencia es hasta 4.000 UF
        limite_exencion_uf = 4000.0
        limite_exencion_clp = limite_exencion_uf * self.uf_actual
        
        saldo_remanente = saldo_actual_clp - monto_a_retirar_clp
        
        recomendacion_herencia = ""
        if aplicar_exencion_herencia:
            if saldo_actual_clp > limite_exencion_clp:
                if saldo_remanente < limite_exencion_clp:
                    recomendacion_herencia = (
                        f"⚠️ Alerta Patrimonial: Estás retirando más de lo óptimo para efectos sucesorios. "
                        f"La ley permite dejar hasta 4.000 UF (aprox. ${limite_exencion_clp:,.0f}) libres de "
                        f"Impuesto a la Herencia. Te sugerimos dejar este monto en la AFP y retirar el excedente."
                    )
                else:
                    recomendacion_herencia = (
                        f"✅ Excelente estrategia: Estás dejando al menos 4.000 UF en la AFP, "
                        f"lo cual te asegura maximizar la exención del Impuesto a la Herencia para tus beneficiarios."
                    )
            else:
                recomendacion_herencia = (
                    "💡 Dado que tu saldo total es menor a 4.000 UF, todo el monto que dejes en la AFP "
                    "estará exento de Impuesto a la Herencia. Evalúa cuánto necesitas retirar realmente."
                )
        
        # Proporción de rentabilidad que se está retirando (FIFO o promedio)
        # Por lo general el retiro arrastra proporcionalmente la ganancia.
        if saldo_actual_clp > 0:
            porcentaje_retiro = monto_a_retirar_clp / saldo_actual_clp
        else:
            porcentaje_retiro = 0
            
        rentabilidad_retirada_tributable = rentabilidad_real_clp * porcentaje_retiro
        
        return {
            "monto_retirado": monto_a_retirar_clp,
            "saldo_remanente": max(0, saldo_remanente),
            "rentabilidad_retirada_tributable": rentabilidad_retirada_tributable,
            "limite_exencion_herencia_clp": limite_exencion_clp,
            "recomendacion_herencia": recomendacion_herencia
        }
        
    def simular_impuestos(
        self,
        sueldo_anual_bruto: float, 
        honorarios_anuales: float, 
        retencion_sueldos: float, 
        retencion_honorarios: float, 
        rentabilidad_tributable_retiro: float
    ) -> dict:
        """
        Simula el impacto de la rentabilidad del retiro en el Impuesto Global Complementario.
        """
        # Escenario 1: Sin hacer el retiro (Situación base)
        base = self.reliquidador.simular_operacion_renta(
            sueldo_anual_bruto=sueldo_anual_bruto,
            afp_name="Capital",  # Placeholder, a los pensionados no se les descuenta AFP de sueldos (asumiendo)
            pct_salud=7.0,
            honorarios_anuales=honorarios_anuales,
            retencion_sueldos=retencion_sueldos,
            retencion_honorarios=retencion_honorarios,
            apv_b_anual=0,
            tipo_afiliado="Pensionado no cotizante",
            ganancias_capital=0
        )
        
        # Escenario 2: Haciendo el retiro
        con_retiro = self.reliquidador.simular_operacion_renta(
            sueldo_anual_bruto=sueldo_anual_bruto,
            afp_name="Capital", 
            pct_salud=7.0,
            honorarios_anuales=honorarios_anuales,
            retencion_sueldos=retencion_sueldos,
            retencion_honorarios=retencion_honorarios,
            apv_b_anual=0,
            tipo_afiliado="Pensionado no cotizante",
            ganancias_capital=rentabilidad_tributable_retiro
        )
        
        # Impuesto extra atribuible puramente al retiro de Cuenta 2
        diferencia_impuesto = con_retiro["igc_original"] - base["igc_original"]
        
        return {
            "igc_base": base["igc_original"],
            "igc_con_retiro": con_retiro["igc_original"],
            "impuesto_adicional_por_retiro": max(0, diferencia_impuesto),
            "tramo_marginal_con_retiro": con_retiro["tramo_marginal_efectivo"]
        }

    def proyectar_inversion(
        self,
        monto_apertura_clp: float,
        aporte_mensual_clp: float,
        horizonte_anios: int,
        tasa_anual_esperada: float,
        utm_actual: float
    ) -> dict:
        """
        Proyecta el crecimiento de una inversión en Cuenta 2 / Fondos Mutuos.
        Evalúa también la exención de 30 UTM sobre las ganancias de capital en caso de rescate.
        """
        meses = horizonte_anios * 12
        # Tasa de interés compuesto mensual
        tasa_mensual = (1 + tasa_anual_esperada / 100) ** (1/12) - 1
        
        saldo = monto_apertura_clp
        total_aportes = monto_apertura_clp
        
        for _ in range(meses):
            saldo += aporte_mensual_clp
            total_aportes += aporte_mensual_clp
            saldo *= (1 + tasa_mensual)
            
        rentabilidad_total = max(0, saldo - total_aportes)
        limite_30_utm = 30 * utm_actual
        
        # Las 30 UTM son el límite anual de ganancia exenta en el año en que se hace el retiro (Régimen General).
        rentabilidad_exenta = min(rentabilidad_total, limite_30_utm)
        rentabilidad_afecta = max(0, rentabilidad_total - limite_30_utm)
        
        return {
            "saldo_final_esperado": saldo,
            "total_aportes": total_aportes,
            "rentabilidad_total": rentabilidad_total,
            "rentabilidad_exenta_estimada": rentabilidad_exenta,
            "rentabilidad_afecta_estimada": rentabilidad_afecta,
            "limite_30_utm": limite_30_utm,
            "horizonte_anios": horizonte_anios,
            "tasa_anual_esperada": tasa_anual_esperada
        }

