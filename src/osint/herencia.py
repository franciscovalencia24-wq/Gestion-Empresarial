import pandas as pd
from src.osint.indicadores import get_uf_today, get_utm_today

def calculate_inheritance_chile(df, has_testament, patrimonio_neto_uf=0.0):
    num_conyuges = len(df[df["Relación"] == "Cónyuge"])
    hijos = df[df["Relación"].str.contains("Hijo/a", na=False)]
    num_hijos = len(hijos)
    
    if num_conyuges == 0 and num_hijos == 0:
        return df
        
    total_parts = 0
    conyuge_share = 0
    hijo_share = 0
    
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
            conyuge_share = (2 / total_parts) * 100
            hijo_share = (1 / total_parts) * 100
        else:
            conyuge_share = 25.0
            hijo_share = 75.0 / num_hijos

    multiplier = 0.5 if has_testament else 1.0

    uf_val = get_uf_today()
    utm_val = get_utm_today()
    uta_val = utm_val * 12.0
    if uta_val <= 0:
        uta_val = 66000.0 * 12.0
        
    # Inicializar columnas nuevas
    df["Monto Herencia (UF)"] = 0.0
    df["Impuesto Estimado (UF)"] = 0.0
    df["Líquido a Recibir (UF)"] = 0.0

    for i, row in df.iterrows():
        rel = str(row["Relación"])
        
        # Calcular Asignación %
        if rel == "Cónyuge":
            pct = round(conyuge_share * multiplier, 2)
        elif "Hijo/a" in rel:
            pct = round(hijo_share * multiplier, 2)
        else:
            pct = 0.0
            
        df.at[i, "% Asignación"] = pct
            
        if patrimonio_neto_uf > 0:
            monto_uf = (pct / 100.0) * patrimonio_neto_uf
            df.at[i, "Monto Herencia (UF)"] = round(monto_uf, 2)
            
            # Calcular impuesto
            monto_clp = monto_uf * uf_val
            monto_uta = monto_clp / uta_val
            
            # Exenciones y recargos según parentesco
            exento_uta = 0
            recargo = 0.0
            if rel in ["Cónyuge", "Hijo/a", "Padre/Madre", "Nieto/a"]:
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
            
            impuesto_clp = impuesto_uta * uta_val
            impuesto_uf = impuesto_clp / uf_val
            
            df.at[i, "Impuesto Estimado (UF)"] = round(impuesto_uf, 2)
            df.at[i, "Líquido a Recibir (UF)"] = round(max(0, monto_uf - impuesto_uf), 2)

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
    from src.database.models import Prospect, ClientProfile, ClientHeir, ClientProperty, ClientInsurance, ClientDebt, ClientPortfolio
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
    uta_val = utm_val * 12.0 if utm_val > 0 else 66000.0 * 12.0

    # 1. BIENES RAÍCES Y DESGRAVAMEN
    total_propiedades_uf = 0.0
    deuda_hipotecaria_bruta_uf = 0.0
    deuda_hipotecaria_neto_desgravamen_uf = 0.0
    
    for prop in prospect.properties:
        total_propiedades_uf += float(prop.valor_comercial_estimado or 0.0)
        deuda_hipotecaria_bruta_uf += float(prop.hipoteca_saldo_actual or 0.0)
        # La hipoteca con seguro de desgravamen se extingue al 100% (Ley 20.449)
        # Pasivo real tras fallecimiento = 0.0

    # 2. INVERSIONES TRADICIONALES
    total_inversiones_clp = sum(float(inv.monto_clp or 0.0) for inv in prospect.portfolios)
    total_inversiones_uf = total_inversiones_clp / uf_val if uf_val > 0 else 0.0

    # 3. SEGUROS DE VIDA (Ley 21.420 y Circular 20 del 2022 SII)
    seguros_exentos_uf = 0.0
    seguros_afectos_uf = 0.0
    seguros_apv_uf = 0.0

    for ins in prospect.insurances:
        cap_uf = float(ins.capital_asegurado or 0.0)
        is_apv = bool(ins.es_apv_poliza)
        f_contrato = str(ins.fecha_contratacion or "").strip()

        if is_apv:
            seguros_apv_uf += cap_uf
        elif f_contrato:
            # Evaluar si es post 04/02/2022 (Ley 21.420)
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

    # 4. TRATAMIENTO PREVISIONAL & HEREDEROS (DL 3500)
    heirs = prospect.heirs
    today = date.today()

    beneficiarios_sobrevivencia = []
    herederos_legales = []

    for h in heirs:
        rel = str(h.relacion or "")
        es_est = bool(h.es_estudiante)
        
        # Calcular edad del heredero
        edad_h = 0
        if h.fecha_nacimiento:
            try:
                fn = h.fecha_nacimiento
                if isinstance(fn, str):
                    fn = datetime.strptime(fn, "%Y-%m-%d").date()
                edad_h = today.year - fn.year - ((today.month, today.day) < (fn.month, fn.day))
            except:
                edad_h = 0

        # Regla DL 3500 Art. 5: Cónyuge, Hijos < 18, o Hijos Estudiantes 18-24
        es_beneficiario_pension = False
        if rel == "Cónyuge" or rel == "Conviviente Civil":
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
        
        herederos_legales.append({
            "nombre": h.nombre, "relacion": rel, "edad": edad_h, "es_estudiante": es_est,
            "asignacion_pct": float(h.porcentaje_asignacion or 0.0)
        })

    # 5. MASA HEREDITARIA REAL
    # Masa = Propiedades (sin deuda desgravada) + Inversiones + Seguros Afectos (post 2022)
    masa_hereditaria_uf = total_propiedades_uf + total_inversiones_uf + seguros_afectos_uf
    
    # Aplicar Exención Especial Cuenta 2 AFP (Art. 72 DL 3500 hasta 4.000 UF)
    # Asumimos que parte de las inversiones corresponden a ahorro previsional voluntario / Cuenta 2 si aplica
    exencion_cuenta2_uf = min(total_inversiones_uf, 4000.0)
    masa_imponible_neto_exencion_uf = max(0.0, masa_hereditaria_uf - exencion_cuenta2_uf)

    # 6. ESQUEMA DE ESTADO PREVISIONAL & RENTA VITALICIA
    estado_prev = prospect.estado_previsional or "Cotizante Activo / Sueldo Empresarial"
    rv_meses_garantizados = prospect.periodo_garantizado_rv_meses or 0

    # Details
    propiedades_detalle = [{
        "alias": p.observaciones or p.direccion or f"ROL {p.rol}",
        "comuna": p.comuna or "",
        "rol": p.rol or "",
        "valor_uf": float(p.valor_comercial_estimado or 0.0),
        "deuda_uf": float(p.hipoteca_saldo_actual or 0.0),
        "banco": p.hipoteca_institucion or ""
    } for p in prospect.properties]

    polizas_detalle = [{
        "aseguradora": i.compania or "",
        "tipo": i.tipo_seguro or "",
        "monto_uf": float(i.capital_asegurado or 0.0),
        "fecha": i.fecha_contratacion or "",
        "es_apv": bool(i.es_apv_poliza)
    } for i in prospect.insurances]

    inversiones_detalle = [{
        "institucion": inv.institucion or "",
        "activo": inv.activo or "",
        "tipo": inv.tipo_activo or "",
        "monto_clp": float(inv.monto_clp or 0.0)
    } for inv in prospect.portfolios]

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
            "propiedades_uf": round(total_propiedades_uf, 2),
            "deuda_hipotecaria_bruta_uf": round(deuda_hipotecaria_bruta_uf, 2),
            "deuda_post_desgravamen_uf": 0.0, # Extinguida por seguro de desgravamen
            "inversiones_uf": round(total_inversiones_uf, 2),
            "seguros_exentos_uf": round(seguros_exentos_uf, 2), # Pre 04/02/2022 Art 20 Ley 16.271
            "seguros_afectos_uf": round(seguros_afectos_uf, 2), # Post 04/02/2022 Ley 21.420 / Circ 20 SII
            "seguros_apv_uf": round(seguros_apv_uf, 2),
            "masa_hereditaria_bruta_uf": round(masa_hereditaria_uf, 2),
            "exencion_cuenta2_art72_uf": round(exencion_cuenta2_uf, 2),
            "masa_hereditaria_imponible_uf": round(masa_imponible_neto_exencion_uf, 2)
        },
        "detalles": {
            "propiedades": propiedades_detalle,
            "polizas": polizas_detalle,
            "inversiones": inversiones_detalle,
            "deudas": deudas_detalle,
            "sociedades": sociedades_detalle
        },
        "beneficiarios_sobrevivencia": beneficiarios_sobrevivencia,
        "herederos_legales": herederos_legales,
        "sustento_legal": [
            {"norma": "Código Civil Art. 988 y 989", "detalle": "Orden de Sucesión Abintestato (Cónyuge e Hijos)."},
            {"norma": "Código Civil Art. 1184, 1195, 1197", "detalle": "Distribución del Acervo: 50% Legítimas, 25% Mejoras, 25% Libre Disposición."},
            {"norma": "DL 3500 Art. 5 y 58", "detalle": "Pensión de Sobrevivencia para Cónyuge e Hijos <18 o Hijos Estudiantes 18-24 años."},
            {"norma": "DL 3500 Art. 67", "detalle": "Herencia Previsional de saldos AFP si no existen beneficiarios de pensión."},
            {"norma": "DL 3500 Art. 72 & Ley 16.271 Art. 55", "detalle": "Exención de hasta 4.000 UF de Impuesto a la Herencia para saldos de Cuenta 2 / Ahorro Voluntario."},
            {"norma": "Ley 21.420 & Circular N° 20 de 2022 del SII", "detalle": "Tratamiento de Seguros de Vida con Ahorro contratados Post-04/02/2022 (Afectos) v/s Pre-04/02/2022 (Exentos)."},
            {"norma": "Ley de Impuesto a la Renta Art. 42 bis N° 4 & DL 3500 Art. 20 L", "detalle": "APV en Póliza de Seguro (Régimen B): Facultad EXCLUSIVA del cónyuge sobreviviente para optar entre: (1) Traspasar/sumar los ahorros a sus propios fondos previsionales sin impuesto, o (2) Retirar los ahorros pagando el Impuesto Único del 15% (recibiendo el 85% líquido), quedando 100% exento del Impuesto a la Herencia (Ley 16.271)."},
            {"norma": "Ley N° 20.449 & DFL 251", "detalle": "Extinción del 100% de pasivos hipotecarios y consumo por Seguro de Desgravamen al fallecer el deudor."}
        ]
    }

    if close_session: db_session.close()
    return resumen

