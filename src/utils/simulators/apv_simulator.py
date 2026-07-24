import numpy_financial as npf

class APVSimulator:
    """
    Simulador de Ahorro Previsional Voluntario (APV).
    Basado en la lógica matemática de las cartolas de la AFP y cálculos tributarios del SII.
    """
    
    def __init__(self, uf_actual: float, utm_actual: float = None):
        """
        Inicializa el simulador con las variables macroeconómicas actuales.
        :param uf_actual: Valor de la Unidad de Fomento en CLP.
        :param utm_actual: Valor de la Unidad Tributaria Mensual en CLP (Opcional, se puede estimar desde la UF si no se provee).
        """
        self.uf = uf_actual
        # Estimación rough si no se entrega UTM (UTM es usualmente ~1.75 UF, pero varía)
        self.utm = utm_actual if utm_actual else self.uf * 1.76  
        
        # Tabla del Impuesto de Segunda Categoría (IGC mensual aproximado en UTM)
        # Factor y Cantidad a Rebajar (Valores referenciales SII)
        self.tramos_igc = [
            {"desde": 0, "hasta": 13.5, "factor": 0.0, "rebaja": 0},
            {"desde": 13.5, "hasta": 30, "factor": 0.04, "rebaja": 0.54},
            {"desde": 30, "hasta": 50, "factor": 0.08, "rebaja": 1.74},
            {"desde": 50, "hasta": 70, "factor": 0.135, "rebaja": 4.49},
            {"desde": 70, "hasta": 90, "factor": 0.23, "rebaja": 11.14},
            {"desde": 90, "hasta": 120, "factor": 0.304, "rebaja": 17.80},
            {"desde": 120, "hasta": 310, "factor": 0.35, "rebaja": 23.32},
            {"desde": 310, "hasta": 999999, "factor": 0.40, "rebaja": 38.82}
        ]
        
    def _calcular_impuesto_mensual(self, sueldo_tributable_clp: float) -> float:
        """Calcula el impuesto mensual según la tabla de Segunda Categoría"""
        sueldo_utm = sueldo_tributable_clp / self.utm
        
        for tramo in self.tramos_igc:
            if tramo["desde"] < sueldo_utm <= tramo["hasta"]:
                impuesto_utm = (sueldo_utm * tramo["factor"]) - tramo["rebaja"]
                return max(0, impuesto_utm * self.utm)
        return 0.0

    def calcular_beneficio_regimen_a(self, aporte_mensual_clp: float, meses: int = 12) -> dict:
        """
        Régimen A: El Estado bonifica el 15% de lo ahorrado en el año,
        con un tope de 6 UTM anuales.
        """
        ahorro_anual = aporte_mensual_clp * meses
        bonificacion_teorica = ahorro_anual * 0.15
        tope_anual = 6 * self.utm
        
        bonificacion_real = min(bonificacion_teorica, tope_anual)
        
        return {
            "regimen": "A",
            "ahorro_anual_clp": ahorro_anual,
            "bonificacion_estado_clp": bonificacion_real,
            "rentabilidad_garantizada_por_bono": (bonificacion_real / ahorro_anual) * 100 if ahorro_anual > 0 else 0
        }

    def calcular_beneficio_regimen_b(self, sueldo_bruto_clp: float, aporte_mensual_clp: float) -> dict:
        """
        Régimen B: El aporte se rebaja de la base imponible. El beneficio es el impuesto que se deja de pagar.
        Tope anual de APV Régimen B: 600 UF (50 UF mensuales).
        """
        # Topes Imponibles (Aprox 84.3 UF para AFP/Salud y 126.6 UF para AFC)
        tope_afp_clp = 84.3 * self.uf
        sueldo_imponible = min(sueldo_bruto_clp, tope_afp_clp)
        
        # Descuentos legales base (aprox 20% total: 10% AFP + 7% Salud + Seguro Cesantía etc)
        descuentos_legales = sueldo_imponible * 0.20
        
        # 1. Sueldo sin APV
        sueldo_tributable_sin_apv = sueldo_bruto_clp - descuentos_legales
        impuesto_sin_apv = self._calcular_impuesto_mensual(sueldo_tributable_sin_apv)
        
        # 2. Sueldo con APV (El aporte APV tiene tope de 50 UF mensuales para beneficio tributario)
        aporte_valido_beneficio = min(aporte_mensual_clp, 50 * self.uf)
        sueldo_tributable_con_apv = sueldo_tributable_sin_apv - aporte_valido_beneficio
        impuesto_con_apv = self._calcular_impuesto_mensual(sueldo_tributable_con_apv)
        
        # Ahorro Tributario
        ahorro_impuesto_mensual = impuesto_sin_apv - impuesto_con_apv
        ahorro_anual = ahorro_impuesto_mensual * 12
        
        return {
            "regimen": "B",
            "aporte_mensual_clp": aporte_mensual_clp,
            "impuesto_original_clp": impuesto_sin_apv,
            "nuevo_impuesto_clp": impuesto_con_apv,
            "ahorro_tributario_mensual_clp": ahorro_impuesto_mensual,
            "ahorro_tributario_anual_clp": ahorro_anual,
            "tasa_beneficio_efectivo": (ahorro_impuesto_mensual / aporte_mensual_clp) * 100 if aporte_mensual_clp > 0 else 0
        }

    def proyectar_pension(self, saldo_actual: float, aporte_mensual: float, anos_restantes: int, rentabilidad_anual: float = 0.05) -> float:
        """
        Proyecta el saldo acumulado (Interés compuesto).
        Retorna el saldo futuro.
        """
        tasa_mensual = (1 + rentabilidad_anual) ** (1/12) - 1
        meses = anos_restantes * 12
        
        saldo_futuro = npf.fv(tasa_mensual, meses, -aporte_mensual, -saldo_actual)
        return float(saldo_futuro)

    def proyectar_pension_detallada(self, saldo_obligatorio_actual: float, 
                                    saldo_apva_actual: float, saldo_apvb_actual: float, saldo_dc_actual: float,
                                    sueldo_bruto_clp: float, aporte_apv_mensual: float, aporte_dc_anual: float, 
                                    anos_restantes: int, rentabilidad_anual: float = 0.05):
        """
        Proyecta mes a mes el saldo, separando Cotización Obligatoria, APV-A, APV-B y DC.
        Retorna un DataFrame de Pandas agrupado por años.
        """
        import pandas as pd
        tasa_mensual = (1 + rentabilidad_anual) ** (1/12) - 1
        meses = anos_restantes * 12
        
        # Calcular el 10% obligatorio usando el tope imponible
        tope_afp_clp = 84.3 * self.uf
        sueldo_imponible = min(sueldo_bruto_clp, tope_afp_clp)
        aporte_obligatorio_mensual = sueldo_imponible * 0.10
        
        # Tope DC Anual (900 UF)
        aporte_dc_valido = min(aporte_dc_anual, 900 * self.uf)
        
        anos_list = []
        saldo_ob_list = []
        saldo_apv_a_list = []
        saldo_apv_b_list = []
        saldo_dc_list = []
        
        curr_ob = saldo_obligatorio_actual
        curr_apva = saldo_apva_actual
        curr_apvb = saldo_apvb_actual
        curr_dc = saldo_dc_actual
        
        # El año 0 es hoy
        anos_list.append(0)
        saldo_ob_list.append(curr_ob)
        saldo_apv_a_list.append(curr_apva)
        saldo_apv_b_list.append(curr_apvb)
        saldo_dc_list.append(curr_dc)
        
        for m in range(1, meses + 1):
            curr_ob *= (1 + tasa_mensual)
            curr_apva *= (1 + tasa_mensual)
            curr_apvb *= (1 + tasa_mensual)
            curr_dc *= (1 + tasa_mensual)
            
            curr_ob += aporte_obligatorio_mensual
            # Asumimos que el aporte nuevo va al APV-B por defecto, pero dejémoslo como APV general (lo sumaremos al B o lo creamos como columna "Aporte APV Nuevo"). 
            # Mejor sumarlo a APV-B asumiendo que el simulador actual modela régimen óptimo y el B es el que crece exento. 
            # O simplemente sumarlo a la bolsa de APV general. Para simplicidad, si es nuevo lo sumaremos al B.
            curr_apvb += aporte_apv_mensual 
            
            # Aporte DC anual en el mes 12 del año
            if m % 12 == 0:
                curr_dc += aporte_dc_valido
            
            # Guardar foto anual
            if m % 12 == 0:
                anos_list.append(m // 12)
                saldo_ob_list.append(curr_ob)
                saldo_apv_a_list.append(curr_apva)
                saldo_apv_b_list.append(curr_apvb)
                saldo_dc_list.append(curr_dc)
                
        df = pd.DataFrame({
            "Año": anos_list,
            "Ahorro Obligatorio (10%)": saldo_ob_list,
            "APV Régimen A": saldo_apv_a_list,
            "APV Régimen B": saldo_apv_b_list,
            "Depósito Convenido": saldo_dc_list
        })
        return df
        return df
