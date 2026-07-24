class ReliquidacionSimulator:
    def __init__(self, uta_anual_clp: float = 793000.0, uf_actual: float = 38000.0):
        self.uta_anual_clp = uta_anual_clp
        self.uf_actual = uf_actual
        # Tramos IGC simplificados en base a UTA
        self.tramos_igc = [
            {"hasta": 13.5, "factor": 0.0, "rebaja_uta": 0.0},
            {"hasta": 30.0, "factor": 0.04, "rebaja_uta": 0.54},
            {"hasta": 50.0, "factor": 0.08, "rebaja_uta": 1.74},
            {"hasta": 70.0, "factor": 0.135, "rebaja_uta": 4.49},
            {"hasta": 90.0, "factor": 0.23, "rebaja_uta": 11.14},
            {"hasta": 120.0, "factor": 0.304, "rebaja_uta": 17.80},
            {"hasta": 310.0, "factor": 0.35, "rebaja_uta": 23.32},
            {"hasta": float('inf'), "factor": 0.40, "rebaja_uta": 38.82}
        ]
        
        self.comisiones_afp = {
            "Capital": 0.0144,
            "Cuprum": 0.0144,
            "Habitat": 0.0127,
            "PlanVital": 0.0116,
            "ProVida": 0.0145,
            "Modelo": 0.0058,
            "Uno": 0.0049
        }
        self.tope_imponible_uf_mensual = 84.3  # Tope legal 2024

    def calcular_renta_tributable(self, sueldo_bruto_mensual: float, afp_name: str, pct_salud: float = 7.0, descuento_cesantia: bool = True, tipo_afiliado: str = "No pensionado") -> dict:
        """Calcula el descuento legal mensual topeado y la renta imponible resultante."""
        tope_imponible_clp = self.tope_imponible_uf_mensual * self.uf_actual
        base_calculo = min(sueldo_bruto_mensual, tope_imponible_clp)
        
        # Descuentos
        afp_obligatorio = base_calculo * 0.10
        comision_afp = base_calculo * self.comisiones_afp.get(afp_name, 0.0144)
        
        # Pensionado no cotizante no paga AFP
        if tipo_afiliado == "Pensionado no cotizante":
            afp_obligatorio = 0.0
            comision_afp = 0.0
            
        salud = base_calculo * (pct_salud / 100.0)
        cesantia = base_calculo * 0.006 if descuento_cesantia else 0.0
        
        descuentos_legales = afp_obligatorio + comision_afp + salud + cesantia
        renta_tributable = max(0, sueldo_bruto_mensual - descuentos_legales)
        
        return {
            "base_tope": base_calculo,
            "afp_obligatorio": afp_obligatorio,
            "comision_afp": comision_afp,
            "salud": salud,
            "cesantia": cesantia,
            "total_descuentos": descuentos_legales,
            "renta_tributable_mensual": renta_tributable
        }

    def calcular_igc(self, base_imponible_clp: float, tasa_fija_override: float = None) -> float:
        """Calcula el Impuesto Global Complementario (IGC)."""
        base_uta = base_imponible_clp / self.uta_anual_clp if self.uta_anual_clp > 0 else 0
        if tasa_fija_override is not None:
            return base_imponible_clp * (tasa_fija_override / 100.0)

        impuesto = 0.0
        for tramo in self.tramos_igc:
            if base_uta <= tramo["hasta"]:
                impuesto = (base_imponible_clp * tramo["factor"]) - (tramo["rebaja_uta"] * self.uta_anual_clp)
                break
        return max(0.0, impuesto)

    def calcular_holgura_apv(self, base_imponible_actual: float, tope_apv_b_anual: float) -> dict:
        """Calcula cuánto APV-B conviene aportar, evalúa saltos de tramo y recomienda APV-A."""
        base_uta = base_imponible_actual / self.uta_anual_clp if self.uta_anual_clp > 0 else 0
        
        # Determinar tramo actual
        tramo_actual_idx = 0
        for i, tramo in enumerate(self.tramos_igc):
            if base_uta <= tramo["hasta"]:
                tramo_actual_idx = i
                break
                
        factor_actual = self.tramos_igc[tramo_actual_idx]["factor"]
        
        utm_valor = self.uta_anual_clp / 12 if self.uta_anual_clp > 0 else 0
        tope_apv_a_clp = utm_valor * 40 # El tope para maximizar el 15% de bonificación estatal es 6 UTM (15% de 40 UTM)
        str_apv_a = f"APV Régimen A (tope sugerido para bonificación: ${tope_apv_a_clp:,.0f} CLP)"

        if factor_actual == 0.0:
            holgura_optima = 0.0
            mensaje = f"Ya te encuentras en el tramo exento de IGC. Un APV Régimen B adicional no te generará devolución fiscal. Recomendamos destinar tu liquidez a {str_apv_a} para ganar un 15% de bonificación estatal."
        else:
            # Calcular cuánto falta para bajar al tramo anterior
            piso_tramo_actual_uta = self.tramos_igc[tramo_actual_idx - 1]["hasta"] if tramo_actual_idx > 0 else 0.0
            monto_para_bajar_tramo_clp = base_imponible_actual - (piso_tramo_actual_uta * self.uta_anual_clp)
            
            holgura_optima = min(monto_para_bajar_tramo_clp, tope_apv_b_anual)
            
            if holgura_optima == tope_apv_b_anual:
                mensaje = f"Puedes aportar el tope máximo legal permitido para tu perfil de ${tope_apv_b_anual:,.0f} CLP y seguirás obteniendo una excelente rebaja tributaria en el tramo del {factor_actual*100:.1f}%."
                if monto_para_bajar_tramo_clp > tope_apv_b_anual:
                    mensaje += f" Aunque topes el APV-B, seguirás en este tramo. Si tienes más capacidad de ahorro, te recomendamos derivarlo a {str_apv_a}."
            else:
                factor_inferior = self.tramos_igc[tramo_actual_idx - 1]["factor"]
                mensaje = f"Estás tributando en el tramo marginal del {factor_actual*100:.1f}%. El monto exacto para maximizar tu eficiencia es aportar ${holgura_optima:,.0f} CLP al año en APV Régimen B. Con esto lograrás bajar al tramo inferior del {factor_inferior*100:.1f}%. Aportar más de eso será menos eficiente, por lo que el sobrante se recomienda enviar a {str_apv_a}."
            
        return {
            "holgura_optima_clp": holgura_optima,
            "mensaje": mensaje
        }

    def simular_operacion_renta(
        self, 
        sueldo_anual_bruto: float, 
        afp_name: str,
        pct_salud: float,
        honorarios_anuales: float, 
        retencion_sueldos: float, 
        retencion_honorarios: float, 
        apv_b_anual: float,
        intereses_hipotecarios: float = 0.0,
        retiro_apvb_anual: float = 0.0,
        tipo_afiliado: str = "No pensionado",
        ganancias_capital: float = 0.0,
        tasa_override: float = None
    ) -> dict:
        
        # 1. Renta Tributable por Sueldos
        sueldo_mensual = sueldo_anual_bruto / 12 if sueldo_anual_bruto > 0 else 0
        desc = self.calcular_renta_tributable(sueldo_mensual, afp_name, pct_salud, tipo_afiliado=tipo_afiliado)
        renta_tributable_sueldos_anual = desc["renta_tributable_mensual"] * 12
        descuentos_anuales = desc["total_descuentos"] * 12
        afp_obligatoria_anual = desc["afp_obligatorio"] * 12
        
        # 2. Base Imponible Original (Sueldos netos + Honorarios presuntos + Ganancias Capital)
        renta_honorarios_presunta = honorarios_anuales * 0.7 
        ingreso_global = renta_tributable_sueldos_anual + renta_honorarios_presunta + ganancias_capital
        
        # 3. Aplicar Beneficio Art 55 Bis (Intereses Hipotecarios)
        tope_55bis = 8 * self.uta_anual_clp
        rebaja_55bis = min(intereses_hipotecarios, tope_55bis)
        
        base_imponible_pre_apv = max(0, ingreso_global - rebaja_55bis)
        igc_original = self.calcular_igc(base_imponible_pre_apv, tasa_override)
        
        # 4. Límite Legal APV Régimen B
        tope_apv_anual = 600 * self.uf_actual
        if tipo_afiliado == "Sueldo Empresarial":
            # Tope estrangulado para empresarios al 100% de sus cotizaciones obligatorias de AFP
            tope_apv_anual = min(tope_apv_anual, afp_obligatoria_anual)
            
        apv_efectivo = min(apv_b_anual, tope_apv_anual)
        
        # 5. Cálculo de Holgura
        holgura = self.calcular_holgura_apv(base_imponible_pre_apv, tope_apv_anual)
        
        # 6. Base Imponible Optimizada y Nuevo IGC
        base_imponible_optimizada = max(0, base_imponible_pre_apv - apv_efectivo)
        igc_optimizado = self.calcular_igc(base_imponible_optimizada, tasa_override)
        
        # 7. Cálculo Impuesto Único por Retiro APV B (Mecánica exacta de Hoja9)
        impuesto_unico_retiro = 0.0
        tasa_impuesto_unico = 0.0
        if retiro_apvb_anual > 0:
            # IGC con retiro sumado a la base optimizada
            base_con_retiro = base_imponible_optimizada + retiro_apvb_anual
            igc_con_retiro = self.calcular_igc(base_con_retiro, tasa_override)
            
            # Diferencia marginal generada por el retiro
            diferencia_igc = max(0, igc_con_retiro - igc_optimizado)
            tasa_marginal_retiro = diferencia_igc / retiro_apvb_anual
            
            if tipo_afiliado == "No pensionado":
                # Regla de penalización: (Tasa * 1.1) + 3% solo aplica para Trabajador Activo
                tasa_impuesto_unico = (tasa_marginal_retiro * 1.1) + 0.03
            else:
                # El resto (Pensionados, Sueldo Empresarial) usan la tasa pura
                tasa_impuesto_unico = tasa_marginal_retiro
                
            impuesto_unico_retiro = tasa_impuesto_unico * retiro_apvb_anual
        
        # 7. Saldo Final
        total_retenido = retencion_sueldos + retencion_honorarios
        saldo_original = total_retenido - igc_original
        
        # El saldo optimizado considera el IGC rebajado por el APV, pero se le descuenta el Impuesto Único a pagar por retiros
        saldo_optimizado = total_retenido - igc_optimizado - impuesto_unico_retiro
        
        beneficio_neto_apv = (total_retenido - igc_optimizado) - saldo_original
        
        tramo_marginal = 0.0
        base_uta = base_imponible_optimizada / self.uta_anual_clp if self.uta_anual_clp > 0 else 0
        for tramo in self.tramos_igc:
            if base_uta <= tramo["hasta"]:
                tramo_marginal = tramo["factor"] * 100
                break
        if tasa_override is not None:
            tramo_marginal = tasa_override

        return {
            "renta_bruta_anual": sueldo_anual_bruto,
            "descuentos_legales_anuales": descuentos_anuales,
            "renta_tributable_sueldos": renta_tributable_sueldos_anual,
            "honorarios_presuntos": renta_honorarios_presunta,
            "rebaja_55bis": rebaja_55bis,
            "base_imponible_pre_apv": base_imponible_pre_apv,
            "igc_original": igc_original,
            "saldo_original": saldo_original,
            "base_imponible_optimizada": base_imponible_optimizada,
            "igc_optimizado": igc_optimizado,
            "retiro_apvb_anual": retiro_apvb_anual,
            "tasa_impuesto_unico": tasa_impuesto_unico * 100,  # en porcentaje
            "impuesto_unico_retiro": impuesto_unico_retiro,
            "saldo_optimizado": saldo_optimizado,
            "beneficio_neto_apv": beneficio_neto_apv,
            "tramo_marginal_efectivo": tramo_marginal,
            "total_retenciones": total_retenido,
            "holgura_apv": holgura
        }
