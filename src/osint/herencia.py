import pandas as pd
import logging
from src.osint.indicadores import get_uf_today, get_utm_today

def calculate_inheritance_chile(df, has_testament=False, patrimonio_neto_uf=0.0):
    """
    Calcula la asignación sucesoria según el Código Civil de Chile:
    - Sin testamento (Abintestato): Asigna el 100% de la masa hereditaria a los herederos forzosos.
    - Con testamento: Asigna el 50% (Legítima Rigurosa) a herederos forzosos, 25% Mejoras, 25% Libre Disposición.
    """
    if df is None or len(df) == 0:
        return df

    num_conyuges = len(df[df["Relación"].isin(["Cónyuge", "Conviviente Civil"])])
    hijos = df[df["Relación"].str.contains("Hijo/a", na=False)]
    num_hijos = len(hijos)
    
    if num_conyuges == 0 and num_hijos == 0:
        return df
        
    total_parts = 0
    conyuge_share = 0.0
    hijo_share = 0.0
    
    if num_conyuges > 0 and num_hijos == 0:
        conyuge_share = 100.0
    elif num_conyuges == 0 and num_hijos > 0:
        hijo_share = 100.0 / num_hijos
    elif num_conyuges > 0 and num_hijos == 1:
        conyuge_share = 50.0
        hijo_share = 50.0
    elif num_conyuges > 0 and num_hijos >= 2:
        if num_hijos <= 6:
            total_parts = (num_hijos * 1) + 2
            conyuge_share = (2.0 / total_parts) * 100.0
            hijo_share = (1.0 / total_parts) * 100.0
        else:
            conyuge_share = 25.0
            hijo_share = 75.0 / num_hijos

    # Multiplicador: si NO hay testamento, asigna el 100% del acervo. Si hay testamento, asigna 50% legítima.
    multiplier = 0.5 if has_testament else 1.0

    uf_val = get_uf_today()
    utm_val = get_utm_today()
    uta_val = utm_val * 12.0
    if uta_val <= 0:
        uta_val = 66000.0 * 12.0
        
    # Inicializar columnas nuevas
    df["% Asignación"] = 0.0
    df["Monto Herencia (UF)"] = 0.0
    df["Monto Herencia ($ CLP)"] = 0.0
    df["Impuesto Estimado (UF)"] = 0.0
    df["Impuesto Estimado ($ CLP)"] = 0.0
    df["Líquido a Recibir (UF)"] = 0.0
    df["Líquido a Recibir ($ CLP)"] = 0.0

    for i, row in df.iterrows():
        rel = str(row["Relación"])
        
        # Calcular Asignación %
        if rel in ["Cónyuge", "Conviviente Civil"]:
            pct = round(conyuge_share * multiplier, 2)
        elif "Hijo/a" in rel:
            pct = round(hijo_share * multiplier, 2)
        else:
            pct = 0.0
            
        df.at[i, "% Asignación"] = pct
            
        if patrimonio_neto_uf > 0:
            monto_uf = (pct / 100.0) * patrimonio_neto_uf
            monto_clp = monto_uf * uf_val
            
            df.at[i, "Monto Herencia (UF)"] = round(monto_uf, 2)
            df.at[i, "Monto Herencia ($ CLP)"] = round(monto_clp, 0)
            
            # Calcular impuesto
            monto_uta = monto_clp / uta_val if uta_val > 0 else 0.0
            
            # Exenciones y recargos según parentesco (Ley 16.271)
            exento_uta = 0
            recargo = 0.0
            if rel in ["Cónyuge", "Conviviente Civil", "Hijo/a", "Padre/Madre", "Nieto/a"]:
                exento_uta = 50
                recargo = 0.0
            elif rel in ["Hermano/a", "Sobrino/a"]:
                exento_uta = 20
                recargo = 0.20
            else:
                exento_uta = 0
                recargo = 0.40
                
            base_imponible_uta = max(0, monto_uta - exento_uta)
            
            impuesto_uta = 0.0
            if base_imponible_uta <= 80:
                impuesto_uta = base_imponible_uta * 0.012
            elif base_imponible_uta <= 160:
                impuesto_uta = base_imponible_uta * 0.024 - 0.96
            elif base_imponible_uta <= 320:
                impuesto_uta = base_imponible_uta * 0.048 - 4.8
            elif base_imponible_uta <= 480:
                impuesto_uta = base_imponible_uta * 0.072 - 12.48
            elif base_imponible_uta <= 640:
                impuesto_uta = base_imponible_uta * 0.096 - 24.0
            elif base_imponible_uta <= 800:
                impuesto_uta = base_imponible_uta * 0.12 - 39.36
            elif base_imponible_uta <= 1200:
                impuesto_uta = base_imponible_uta * 0.144 - 58.56
            elif base_imponible_uta <= 1440:
                impuesto_uta = base_imponible_uta * 0.168 - 87.36
            elif base_imponible_uta <= 1600:
                impuesto_uta = base_imponible_uta * 0.192 - 121.92
            elif base_imponible_uta <= 2000:
                impuesto_uta = base_imponible_uta * 0.216 - 160.32
            else:
                impuesto_uta = base_imponible_uta * 0.25 - 228.32
                
            impuesto_uta = impuesto_uta * (1 + recargo)
            
            impuesto_clp = max(0.0, impuesto_uta * uta_val)
            impuesto_uf = impuesto_clp / uf_val if uf_val > 0 else 0.0
            
            df.at[i, "Impuesto Estimado (UF)"] = round(impuesto_uf, 2)
            df.at[i, "Impuesto Estimado ($ CLP)"] = round(impuesto_clp, 0)
            df.at[i, "Líquido a Recibir (UF)"] = round(max(0, monto_uf - impuesto_uf), 2)
            df.at[i, "Líquido a Recibir ($ CLP)"] = round(max(0, monto_clp - impuesto_clp), 0)

    return df


def calculate_advanced_succession(prospect_id, db_session=None):
    """
    Calcula el mapa integral de sucesión legal y tributaria según la legislación chilena:
    - Código Civil (Art. 988, 989, 1181, 1184, 1195, 1197)
    - DL 3500 (Art. 5, 58, 62, 67, 72 - Pensión de Sobrevivencia, Herencia Previsional y Exención 4.000 UF Cuenta 2)
    - Ley 16.271 & Ley 21.420 (Circular N° 20 de 2022 del SII - Seguros de Vida Pre/Post Feb 2022)
    - Ley 20.449 & DFL 251 (Seguros de Desgravamen y extinción de créditos)
    """
    from src.database.connection import SessionLocal
    from src.database.models import Prospect
    from datetime import datetime, date

    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True

    prospect = db_session.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not prospect:
        if close_session: db_session.close()
        return None

    uf_val = get_uf_today()
    utm_val = get_utm_today()

    # 1. BIENES RAÍCES Y DESGRAVAMEN
    total_propiedades_uf = 0.0
    total_propiedades_clp = 0.0
    deuda_hipotecaria_bruta_uf = 0.0
    deuda_hipotecaria_bruta_clp = 0.0
    
    propiedades_detalle = []
    for prop in prospect.properties:
        v_uf = float(prop.valor_comercial_estimado or 0.0)
        v_clp = v_uf * uf_val
        d_uf = float(prop.hipoteca_saldo_actual or 0.0)
        d_clp = d_uf * uf_val
        
        total_propiedades_uf += v_uf
        total_propiedades_clp += v_clp
        deuda_hipotecaria_bruta_uf += d_uf
        deuda_hipotecaria_bruta_clp += d_clp
        
        propiedades_detalle.append({
            "alias": prop.observaciones or prop.direccion or f"ROL {prop.rol}",
            "comuna": prop.comuna or "",
            "rol": prop.rol or "",
            "valor_uf": v_uf,
            "valor_clp": v_clp,
            "deuda_uf": d_uf,
            "deuda_clp": d_clp,
            "banco": prop.hipoteca_institucion or ""
        })

    # 2. SEPARACIÓN DE INVERSIONES: PREVISIONALES V/S NO PREVISIONALES
    inv_previsionales_detalle = []
    inv_no_previsionales_detalle = []
    
    total_inv_prev_clp = 0.0
    total_inv_noprev_clp = 0.0

    keywords_prev = ["apv", "cuenta 2", "afp", "previsional", "ahorro previsional", "fondos mutuos previsionales"]

    for inv in prospect.portfolios:
        m_clp = float(inv.monto_clp or 0.0)
        m_uf = m_clp / uf_val if uf_val > 0 else 0.0
        
        tipo_str = f"{inv.tipo_activo or ''} {inv.activo or ''} {inv.institucion or ''}".lower()
        is_prev = any(k in tipo_str for k in keywords_prev)

        item = {
            "institucion": inv.institucion or "",
            "activo": inv.activo or "",
            "tipo": inv.tipo_activo or "Inversión Generica",
            "monto_clp": m_clp,
            "monto_uf": m_uf
        }

        if is_prev:
            inv_previsionales_detalle.append(item)
            total_inv_prev_clp += m_clp
        else:
            inv_no_previsionales_detalle.append(item)
            total_inv_noprev_clp += m_clp

    total_inversiones_clp = total_inv_prev_clp + total_inv_noprev_clp
    total_inversiones_uf = total_inversiones_clp / uf_val if uf_val > 0 else 0.0
    total_inv_prev_uf = total_inv_prev_clp / uf_val if uf_val > 0 else 0.0
    total_inv_noprev_uf = total_inv_noprev_clp / uf_val if uf_val > 0 else 0.0

    # 3. SEGUROS DE VIDA (Ley 21.420 y Circular 20 del 2022 SII)
    seguros_exentos_uf = 0.0
    seguros_afectos_uf = 0.0
    seguros_apv_uf = 0.0

    polizas_detalle = []
    for ins in prospect.insurances:
        cap_uf = float(ins.capital_asegurado or 0.0)
        cap_clp = cap_uf * uf_val
        is_apv = bool(ins.es_apv_poliza)
        f_contrato = str(ins.fecha_contratacion or "").strip()

        if is_apv:
            seguros_apv_uf += cap_uf
        elif f_contrato:
            try:
                dt_c = datetime.strptime(f_contrato, "%Y-%m-%d")
                if dt_c >= datetime(2022, 2, 4):
                    seguros_afectos_uf += cap_uf
                else:
                    seguros_exentos_uf += cap_uf
            except:
                seguros_exentos_uf += cap_uf
        else:
            seguros_exentos_uf += cap_uf

        polizas_detalle.append({
            "aseguradora": ins.compania or "",
            "tipo": ins.tipo_seguro or "",
            "monto_uf": cap_uf,
            "monto_clp": cap_clp,
            "fecha": ins.fecha_contratacion or "",
            "es_apv": is_apv
        })

    # 4. HEREDEROS Y BENEFICIARIOS
    heirs = prospect.heirs
    today = date.today()

    beneficiarios_sobrevivencia = []
    raw_herederos = []

    for h in heirs:
        rel = str(h.relacion or "")
        es_est = bool(h.es_estudiante)
        
        edad_h = 0
        if h.fecha_nacimiento:
            try:
                fn = h.fecha_nacimiento
                if isinstance(fn, str):
                    fn = datetime.strptime(fn, "%Y-%m-%d").date()
                edad_h = today.year - fn.year - ((today.month, today.day) < (fn.month, fn.day))
            except:
                edad_h = 0

        es_beneficiario_pension = False
        if rel in ["Cónyuge", "Conviviente Civil"]:
            es_beneficiario_pension = True
        elif "Hijo/a" in rel:
            if edad_h < 18:
                es_beneficiario_pension = True
            elif 18 <= edad_h <= 24 and es_est:
                es_beneficiario_pension = True

        if es_beneficiario_pension:
            beneficiarios_sobrevivencia.append({
                "nombre": h.nombre, "relacion": rel, "edad": edad_h, "es_estudiante": es_est,
                "fundamento": "DL 3500 Art. 5 y 58 (Derecho a Pensión de Sobrevivencia)"
            })
        
        raw_herederos.append({
            "Nombre": h.nombre,
            "Relación": rel,
            "Edad": edad_h,
            "Es Estudiante": es_est
        })

    # 5. MASA HEREDITARIA REAL
    # Masa = Propiedades + Inversiones + Seguros Afectos
    masa_hereditaria_uf = total_propiedades_uf + total_inversiones_uf + seguros_afectos_uf
    masa_hereditaria_clp = masa_hereditaria_uf * uf_val
    
    # Exención Especial Cuenta 2 AFP (Art. 72 DL 3500 hasta 4.000 UF)
    exencion_cuenta2_uf = min(total_inv_prev_uf, 4000.0)
    masa_imponible_neto_exencion_uf = max(0.0, masa_hereditaria_uf - exencion_cuenta2_uf)
    masa_imponible_neto_exencion_clp = masa_imponible_neto_exencion_uf * uf_val

    # 6. CALCULAR DISTRIBUCIÓN LEGAL DE HERENCIA CON VALORES PROPORCIONALES
    has_testament = False
    if prospect.profile and hasattr(prospect.profile, 'tiene_testamento'):
        has_testament = bool(prospect.profile.tiene_testamento)

    df_herederos = pd.DataFrame(raw_herederos) if raw_herederos else pd.DataFrame(columns=["Nombre", "Relación", "Edad", "Es Estudiante"])
    df_herederos_calc = calculate_inheritance_chile(df_herederos, has_testament=has_testament, patrimonio_neto_uf=masa_imponible_neto_exencion_uf)

    herederos_legales = []
    if df_herederos_calc is not None and len(df_herederos_calc) > 0:
        for _, row in df_herederos_calc.iterrows():
            herederos_legales.append({
                "nombre": row.get("Nombre", ""),
                "relacion": row.get("Relación", ""),
                "edad": row.get("Edad", 0),
                "es_estudiante": row.get("Es Estudiante", False),
                "asignacion_pct": float(row.get("% Asignación", 0.0)),
                "monto_uf": float(row.get("Monto Herencia (UF)", 0.0)),
                "monto_clp": float(row.get("Monto Herencia ($ CLP)", 0.0)),
                "impuesto_uf": float(row.get("Impuesto Estimado (UF)", 0.0)),
                "impuesto_clp": float(row.get("Impuesto Estimado ($ CLP)", 0.0)),
                "liquido_uf": float(row.get("Líquido a Recibir (UF)", 0.0)),
                "liquido_clp": float(row.get("Líquido a Recibir ($ CLP)", 0.0))
            })

    # ESTADO OCUPACIONAL & PREVISIONAL
    estado_prev = "Cotizante Activo / Boleta de Honorarios"
    if prospect.profile and hasattr(prospect.profile, 'situación_laboral') and prospect.profile.situación_laboral:
        estado_prev = prospect.profile.situación_laboral
    elif prospect.estado_previsional:
        estado_prev = prospect.estado_previsional

    rv_meses_garantizados = prospect.periodo_garantizado_rv_meses or 0

    deudas_detalle = [{
        "institucion": d.institucion or "",
        "tipo": d.tipo_credito or "",
        "monto_actual": float(d.monto_actual or 0.0),
        "mora": float(d.monto_mora or 0.0)
    } for d in prospect.debts]

    sociedades_detalle = [{
        "rut": c.rut_empresa or "",
        "razon_social": c.razon_social or "",
        "pct_capital": float(c.porcentaje_capital or 0.0)
    } for c in prospect.companies]

    resumen = {
        "prospect_id": prospect.id,
        "rut": prospect.rut,
        "nombre": prospect.nombre,
        "estado_previsional": estado_prev,
        "periodo_garantizado_rv_meses": rv_meses_garantizados,
        "totales": {
            "uf_actual": uf_val,
            "propiedades_uf": round(total_propiedades_uf, 2),
            "propiedades_clp": round(total_propiedades_clp, 0),
            "deuda_hipotecaria_bruta_uf": round(deuda_hipotecaria_bruta_uf, 2),
            "deuda_hipotecaria_bruta_clp": round(deuda_hipotecaria_bruta_clp, 0),
            "inversiones_total_uf": round(total_inversiones_uf, 2),
            "inversiones_total_clp": round(total_inversiones_clp, 0),
            "inversiones_previsionales_uf": round(total_inv_prev_uf, 2),
            "inversiones_previsionales_clp": round(total_inv_prev_clp, 0),
            "inversiones_no_previsionales_uf": round(total_inv_noprev_uf, 2),
            "inversiones_no_previsionales_clp": round(total_inv_noprev_clp, 0),
            "seguros_exentos_uf": round(seguros_exentos_uf, 2),
            "seguros_afectos_uf": round(seguros_afectos_uf, 2),
            "seguros_apv_uf": round(seguros_apv_uf, 2),
            "masa_hereditaria_bruta_uf": round(masa_hereditaria_uf, 2),
            "masa_hereditaria_bruta_clp": round(masa_hereditaria_clp, 0),
            "exencion_cuenta2_art72_uf": round(exencion_cuenta2_uf, 2),
            "masa_hereditaria_imponible_uf": round(masa_imponible_neto_exencion_uf, 2),
            "masa_hereditaria_imponible_clp": round(masa_imponible_neto_exencion_clp, 0)
        },
        "detalles": {
            "propiedades": propiedades_detalle,
            "polizas": polizas_detalle,
            "inversiones_previsionales": inv_previsionales_detalle,
            "inversiones_no_previsionales": inv_no_previsionales_detalle,
            "deudas": deudas_detalle,
            "sociedades": sociedades_detalle
        },
        "beneficiarios_sobrevivencia": beneficiarios_sobrevivencia,
        "herederos_legales": herederos_legales,
        "sustento_legal": [
            {"norma": "Código Civil Art. 988 y 989", "detalle": "Orden de Sucesión Abintestato (Cónyuge e Hijos)."},
            {"norma": "Código Civil Art. 1184, 1195, 1197", "detalle": "Distribución del Acervo Hereditario: 50% Legítimas Rigurosas, 25% Mejoras, 25% Libre Disposición."},
            {"norma": "DL 3500 Art. 5 y 58", "detalle": "Pensión de Sobrevivencia para Cónyuge e Hijos <18 años o Hijos Estudiantes 18-24 años."},
            {"norma": "DL 3500 Art. 67", "detalle": "Herencia Previsional de saldos de AFP en ausencia de beneficiarios directos de pensión."},
            {"norma": "DL 3500 Art. 72 & Ley 16.271 Art. 55", "detalle": "Exención tributaria especial de hasta 4.000 UF de Impuesto a la Herencia para saldos de Cuenta 2 / Ahorro Voluntario."},
            {"norma": "Ley 21.420 & Circular N° 20 de 2022 del SII", "detalle": "Tratamiento tributario de Seguros de Vida con Ahorro contratados Post-04/02/2022 (Afectos) v/s Pre-04/02/2022 (Exentos)."},
            {"norma": "Ley de Impuesto a la Renta Art. 42 bis N° 4 & DL 3500 Art. 20 L", "detalle": "APV en Póliza de Seguro (Régimen B): Facultad EXCLUSIVA del cónyuge sobreviviente para optar entre: (1) Traspasar ahorros a su propia AFP sin impuesto, o (2) Retirar capital pagando Impuesto Único del 15% (85% líquido), 100% exento del Impuesto a la Herencia."},
            {"norma": "Ley N° 20.449 & DFL 251", "detalle": "Extinción del 100% de pasivos hipotecarios y consumo por Seguro de Desgravamen al fallecer el deudor."}
        ]
    }

    if close_session: db_session.close()
    return resumen
