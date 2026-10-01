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

    def calcular_holgura_apv(self, base_imponible_actual: float, tope_apv_b_anual: float, apv_b_anual: float, total_retenido: float = 0.0, impuesto_unico_retiro: float = 0.0, tasa_override: float = None) -> dict:
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
        str_apv_a = f"APV Régimen A (tope sugerido para bonificación: CLP {tope_apv_a_clp:,.0f})"

        piso_tramo_actual_uta = self.tramos_igc[tramo_actual_idx - 1]["hasta"] if tramo_actual_idx > 0 else 0.0
        monto_para_bajar_tramo_clp = base_imponible_actual - (piso_tramo_actual_uta * self.uta_anual_clp)
        apv_adicional_para_bajar = max(0, monto_para_bajar_tramo_clp - apv_b_anual)

        txt_devolucion = ""
        if monto_para_bajar_tramo_clp > 0:
            base_con_bajada = max(0, base_imponible_actual - monto_para_bajar_tramo_clp)
            igc_con_bajada = self.calcular_igc(base_con_bajada, tasa_override)
            devolucion_nueva = total_retenido - igc_con_bajada - impuesto_unico_retiro
            
            if devolucion_nueva > 0:
                txt_devolucion = f", logrando una devolución de impuestos estimada de **CLP {devolucion_nueva:,.0f}**"
            else:
                txt_devolucion = f", reduciendo tu pago de impuestos a **CLP {abs(devolucion_nueva):,.0f}**"

        if factor_actual >= 0.135:
            tope_apv_b_anual = 600 * self.uf_actual
            holgura_faltante = max(0.0, tope_apv_b_anual - apv_b_anual)
            holgura_optima = tope_apv_b_anual
            
            txt_bajar_tramo = ""
            if apv_adicional_para_bajar > 0 and apv_adicional_para_bajar <= holgura_faltante:
                txt_bajar_tramo = f" Como dato estratégico, si aportas **CLP {apv_adicional_para_bajar:,.0f}** adicionales a tu APV-B actual (alcanzando CLP {monto_para_bajar_tramo_clp:,.0f} en total), lograrás bajar al tramo de impuestos inferior{txt_devolucion}."
            elif monto_para_bajar_tramo_clp > 0 and apv_b_anual == 0 and monto_para_bajar_tramo_clp <= tope_apv_b_anual:
                txt_bajar_tramo = f" Como dato estratégico, un aporte de **CLP {monto_para_bajar_tramo_clp:,.0f}** te permitiría bajar al tramo de impuestos inferior{txt_devolucion}."
            
            if holgura_faltante > 0 and apv_b_anual > 0:
                mensaje = f"Estás tributando en el **tramo marginal del {factor_actual*100:.1f}%**. Has aportado **CLP {apv_b_anual:,.0f} en APV-B**. Para optimizar al 100% tu carga tributaria, te sugerimos aportar los **CLP {holgura_faltante:,.0f}** restantes para alcanzar el **tope máximo legal de 600 UF** (CLP {tope_apv_b_anual:,.0f}).{txt_bajar_tramo} Incluso si bajas de tramo, la devolución de impuestos del Régimen B será muy superior al Régimen A. Cabe destacar que el **APV-A no genera devolución de impuestos**, sino un aporte fiscal (bonificación estatal) topado a 6 UTM anuales. Si a estas alturas del año no es posible gestionar el tope de APV por descuento por planilla con tu empleador, puedes realizar un **aporte directo desde tu cuenta corriente**."
            elif holgura_faltante == 0 and apv_b_anual > 0:
                mensaje = f"¡Excelente! Estás tributando en un tramo alto (**{factor_actual*100:.1f}%**) y ya has alcanzado el **tope máximo legal de 600 UF en APV-B** (CLP {tope_apv_b_anual:,.0f}), maximizando tu eficiencia fiscal. Si tu capacidad de ahorrar e invertir en instrumentos previsionales voluntarios es mayor al tope de 600 UF en APV-B, deriva el excedente a **{str_apv_a}**. Cabe destacar que el **APV-A no genera devolución de impuestos**, sino un aporte fiscal (bonificación estatal) topado a 6 UTM anuales."
            else:
                mensaje = f"Estás tributando en el **tramo marginal del {factor_actual*100:.1f}%**. Te conviene realizar el **tope máximo legal de APV-B de 600 UF** (CLP {tope_apv_b_anual:,.0f}).{txt_bajar_tramo} Incluso si bajas de tramo, la devolución de impuestos del Régimen B será muy superior al Régimen A. Cabe destacar que el **APV-A no genera devolución de impuestos**, sino un aporte fiscal (bonificación estatal) topado a 6 UTM anuales. Si tu capacidad de ahorrar e invertir en instrumentos previsionales voluntarios es mayor al tope de 600 UF en APV-B, deriva el excedente a **{str_apv_a}**. Si a estas alturas del año no es posible gestionar el descuento por planilla con tu empleador, puedes realizar un **aporte directo desde tu cuenta corriente**."
        elif factor_actual > 0.0:
            holgura_optima = min(monto_para_bajar_tramo_clp, 600 * self.uf_actual)
            
            txt_bajar_tramo = ""
            if apv_adicional_para_bajar > 0:
                if apv_b_anual > 0:
                    txt_bajar_tramo = f" Como dato estratégico, si aportas **CLP {apv_adicional_para_bajar:,.0f}** adicionales a tu APV-B actual (alcanzando CLP {monto_para_bajar_tramo_clp:,.0f} en total), lograrás bajar al tramo de impuestos inferior{txt_devolucion}."
                else:
                    txt_bajar_tramo = f" Aporta **CLP {holgura_optima:,.0f} a APV Régimen B** para bajar de tramo{txt_devolucion}."

            mensaje = f"Estás en el **tramo del {factor_actual*100:.1f}%**.{txt_bajar_tramo} Recuerda que el **tope máximo legal** para beneficios en APV-B es de 600 UF. Para ahorros menores, cabe destacar que el **APV-A no genera devolución de impuestos**, sino un aporte fiscal (15%) topado a 6 UTM. Por ello, para montos grandes siempre conviene el Régimen B. Si a estas alturas del año no puedes gestionar el descuento por planilla, haz un **aporte directo desde tu cuenta corriente**."
        else:
            holgura_optima = 0.0
            mensaje = f"Ya te encuentras en el **tramo exento de IGC**. Un APV Régimen B (aunque su tope legal sea 600 UF) **no te generará devolución fiscal**. Recomendamos destinar tu liquidez a **{str_apv_a}**. Cabe destacar que el APV-A no genera devolución de impuestos, sino un aporte fiscal directo a tu cuenta del 15%. Puedes realizar **aportes directos desde tu cuenta corriente**."
            
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
        gastos_educacion: float = 0.0,
        retiro_apvb_anual: float = 0.0,
        tipo_afiliado: str = "No pensionado",
        ganancias_capital: float = 0.0,
        tasa_override: float = None,
        deposito_convenido_anual: float = 0.0
    ) -> dict:
        
        # 0. Rebajar Depósito Convenido del Sueldo Bruto Anual
        # El Depósito Convenido se descuenta directamente de los haberes imponibles.
        sueldo_anual_bruto = max(0, sueldo_anual_bruto - deposito_convenido_anual)
        
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
        igc_original_bruto = self.calcular_igc(base_imponible_pre_apv, tasa_override)
        igc_original = max(0.0, igc_original_bruto - gastos_educacion)
        
        # 4. Límite Legal APV Régimen B
        tope_apv_anual = 600 * self.uf_actual
        if tipo_afiliado == "Sueldo Empresarial":
            # Tope estrangulado para empresarios al 100% de sus cotizaciones obligatorias de AFP
            tope_apv_anual = min(tope_apv_anual, afp_obligatoria_anual)
            
        apv_efectivo = min(apv_b_anual, tope_apv_anual)
        
        # 6. Base Imponible Optimizada y Nuevo IGC
        base_imponible_optimizada = max(0, base_imponible_pre_apv - apv_efectivo)
        igc_optimizado_bruto = self.calcular_igc(base_imponible_optimizada, tasa_override)
        igc_optimizado = max(0.0, igc_optimizado_bruto - gastos_educacion)
        
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
        
        # 8. Saldo Final
        total_retenido = retencion_sueldos + retencion_honorarios
        saldo_original = total_retenido - igc_original
        
        # 9. Cálculo de Holgura Estratégica (Usamos el retenido y el impuesto único para predecir la devolución si baja de tramo)
        holgura = self.calcular_holgura_apv(base_imponible_pre_apv, tope_apv_anual, apv_b_anual, total_retenido, impuesto_unico_retiro, tasa_override)
        
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
            "credito_55ter": gastos_educacion,
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
