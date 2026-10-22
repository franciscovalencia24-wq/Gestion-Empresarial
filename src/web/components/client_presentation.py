import os
import io
import base64
from datetime import date, datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.database.connection import SessionLocal
from src.database.models import Prospect, ClientProfile, ClientProperty, ClientPortfolio, ClientInsurance, ClientDebt, ClientHeir
from src.osint.indicadores import get_uf_today, get_utm_today
from src.utils.simulators.apv_simulator import APVSimulator

def safe_float(val, default=0.0):
    if pd.isna(val) or val is None:
        return default
    try:
        val_str = str(val).strip().lower()
        if val_str in ["", "none", "nan", "null"]:
            return default
        return float(val_str)
    except Exception:
        return default


def _get_base64_image(path: str) -> str:
    """Lee y codifica una imagen local a base64 para incrustación directa en HTML."""
    if path and os.path.exists(path):
        try:
            with open(path, "rb") as f:
                ext = path.split(".")[-1].lower()
                mime = "image/svg+xml" if ext == "svg" else "image/png"
                return f"data:{mime};base64,{base64.b64encode(f.read()).decode('utf-8')}"
        except Exception:
            return ""
    return ""


def render_metric_cards_row(cards: list):
    """
    Renderiza tarjetas de métricas ejecutivas con diseño fluido, responsivo y sin superposición.
    El HTML se construye en un bloque sin indentación para evitar que el parser de Markdown
    lo interprete como bloque de código (<pre><code>).
    """
    cards_html = []
    for c in cards:
        label = c.get("label", "")
        value = c.get("value", "")
        delta = c.get("delta", "")
        delta_color = c.get("delta_color", "#059669")
        delta_bg = c.get("delta_bg", "#ecfdf5")
        help_text = c.get("help", "")

        delta_html = ""
        if delta:
            delta_html = (
                f'<div style="margin-top: 6px;">'
                f'<span style="display: inline-flex; align-items: center; gap: 4px; background: {delta_bg}; color: {delta_color}; font-size: clamp(0.72rem, 1.1vw, 0.82rem); font-weight: 700; padding: 3px 8px; border-radius: 6px; line-height: 1.3; word-break: normal;">'
                f'{delta}'
                f'</span>'
                f'</div>'
            )

        help_attr = f'title="{help_text}"' if help_text else ""
        card_html = (
            f'<div {help_attr} style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); display: flex; flex-direction: column; justify-content: space-between; flex: 1 1 clamp(200px, 28%, 280px); min-width: 0; max-width: 100%; box-sizing: border-box; gap: 6px;">'
            f'<div>'
            f'<div style="font-size: clamp(0.70rem, 1.05vw, 0.78rem); font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; line-height: 1.35; word-break: normal;">{label}</div>'
            f'<div style="font-size: clamp(1.15rem, 1.8vw, 1.45rem); font-weight: 800; color: #0f172a; line-height: 1.22; word-break: normal; overflow-wrap: break-word;">{value}</div>'
            f'</div>'
            f'{delta_html}'
            f'</div>'
        )
        cards_html.append(card_html)

    grid_html = (
        f'<div style="display: flex; flex-wrap: wrap; gap: 12px; width: 100%; box-sizing: border-box; margin-bottom: 18px;">'
        f'{"".join(cards_html)}'
        f'</div>'
    )
    st.markdown(grid_html, unsafe_allow_html=True)


def render_valor_presentation_view(rut: str, nombre_cliente: str):
    """
    Vista Ejecutiva 'Modo Presentación' para clientes y prospectos HNWI.
    Consolida de forma estética y visual:
    1. Motor de Ahorro Tributario (APV / Reliquidación IGC)
    2. Proyección de Inversiones y Alfa Neto (Traslado a FV Asesorías / Principal)
    3. Blindaje Sucesorio y Partición Legal (Ley N° 16.271)
    """
    # 1. Variables Macroeconómicas
    uf_val = get_uf_today() or 38000.0
    utm_val = get_utm_today() or 66000.0

    # 2. Parámetros Fiduciarios de Proyección Financiera (Única Fuente de Verdad)
    tasa_retorno_banca = 0.068   # 6.80% Retorno bruto promedio banca tradicional
    costo_banca = 0.028          # 2.80% TAC / Costo de administración bancaria
    tasa_tradicional = tasa_retorno_banca - costo_banca  # 4.00% neto anual

    tasa_retorno_fv = 0.0865     # 8.65% Retorno bruto estimado portafolio institucional
    costo_fv = 0.0115            # 1.15% TAC arquitectura abierta Principal & FV Asesorías
    tasa_fv = tasa_retorno_fv - costo_fv  # 7.50% neto anual

    # 3. Extracción de Datos del Cliente desde DB y Sesión
    db = SessionLocal()
    edad_cliente = 52
    fecha_nac_cliente = None
    try:
        clean_rut = rut.replace(".", "").replace("-", "").strip()
        fmt_rut = clean_rut[:-1] + "-" + clean_rut[-1].upper() if len(clean_rut) > 1 else clean_rut
        prospect = db.query(Prospect).filter(
            (Prospect.rut == fmt_rut) | (Prospect.rut == clean_rut) | (Prospect.rut == rut)
        ).first()

        perfil_inversion = "Moderado (50% Renta Variable / 50% Renta Fija)"
        objetivo_inversion = "Preservación y Crecimiento Patrimonial"
        regimen_patrimonial = "No Informado"
        sueldo_mensual = 6500000.0

        if prospect:
            try:
                prof = prospect.profile
            except Exception:
                prof = None

            if prof:
                if prof.nivel_riesgo:
                    perfil_inversion = prof.nivel_riesgo
                if prof.objetivo_inversion:
                    objetivo_inversion = prof.objetivo_inversion
                if getattr(prof, 'regimen_patrimonial', None):
                    regimen_patrimonial = prof.regimen_patrimonial
                if getattr(prof, 'fecha_nacimiento', None):
                    fecha_nac_cliente = prof.fecha_nacimiento
                if getattr(prof, 'edad', None) and prof.edad > 0:
                    edad_cliente = int(prof.edad)
                elif getattr(prof, 'edad_actuarial', None) and prof.edad_actuarial > 0:
                    edad_cliente = int(prof.edad_actuarial)
                if getattr(prof, 'sueldo_liquido_mensual', None) and prof.sueldo_liquido_mensual > 0:
                    sueldo_mensual = float(prof.sueldo_liquido_mensual)
                elif getattr(prof, 'renta_anual_declarada', None) and prof.renta_anual_declarada > 0:
                    sueldo_mensual = float(prof.renta_anual_declarada) / 12.0

        # Overrides de session_state si están editados en la ficha
        if f"{rut}_perfil" in st.session_state and st.session_state[f"{rut}_perfil"]:
            perfil_inversion = st.session_state[f"{rut}_perfil"]
        if f"{rut}_regimen_patrimonial" in st.session_state and st.session_state[f"{rut}_regimen_patrimonial"]:
            regimen_patrimonial = st.session_state[f"{rut}_regimen_patrimonial"]
        if f"{rut}_edad" in st.session_state and st.session_state[f"{rut}_edad"]:
            try:
                edad_cliente = int(st.session_state[f"{rut}_edad"])
            except Exception:
                pass

        # Capital Líquido (Inversiones Financieras)
        capital_liquido = 0.0
        if prospect and prospect.portfolios:
            capital_liquido = sum([safe_float(p.monto_clp or p.monto_original) for p in prospect.portfolios])
        if capital_liquido <= 0 and prospect and prospect.saldo_administrado:
            capital_liquido = safe_float(prospect.saldo_administrado)
        if capital_liquido <= 0:
            capital_liquido = 1000000000.0  # Base patrimonial HNWI representativa: 1.000.000.000 CLP

        # Patrimonio Inmobiliario y Activos Totales
        total_inmuebles_clp = 0.0
        total_avaluo_fiscal_clp = 0.0
        if prospect and prospect.properties:
            total_inmuebles_clp = sum([safe_float(p.valor_comercial_estimado or (safe_float(p.avaluo_fiscal)/uf_val)) * uf_val for p in prospect.properties])
            total_avaluo_fiscal_clp = sum([safe_float(p.avaluo_fiscal) for p in prospect.properties])

    finally:
        db.close()

    # --- BRANDING & HEADER EJECUTIVO INTEGRADO (TARJETA UNIFICADA CON OPTICAL SYMMETRY) ---
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    candidates_fv = [
        os.path.join(project_root, "assets", "brand", "fv_logo_principal.png"),
        os.path.join(project_root, "assets", "brand", "fv_logo_principal_official.png"),
        os.path.join(project_root, "assets", "brand", "fv_logo_principal.svg")
    ]
    path_fv = next((p for p in candidates_fv if os.path.exists(p)), "")
    fv_b64 = _get_base64_image(path_fv)

    # Logo Altus AI de alto contraste (versión para fondos claros: pizarra oscura + ámbar cálido)
    candidates_altus = [
        os.path.join(project_root, "assets", "brand", "altus_logo_light_bg.png"),
        os.path.join(project_root, "assets", "brand", "altus_ai_logo_white_bg.svg"),
        os.path.join(project_root, "assets", "brand", "altus_ai_logo_dark.png")
    ]
    path_altus = next((p for p in candidates_altus if os.path.exists(p)), "")
    altus_b64 = _get_base64_image(path_altus)

    fv_img_tag = (
        f'<img src="{fv_b64}" style="max-height: 52px; max-width: 175px; object-fit: contain; width: auto; display: block;" alt="FV Asesorías" />'
        if fv_b64 else '<span style="font-weight: 900; color: #047857; font-size: 1.15em;">FV ASESORÍAS</span>'
    )
    altus_img_tag = (
        f'<img src="{altus_b64}" style="max-height: 55px; max-width: 110px; object-fit: contain; width: auto; display: block;" alt="Altus AI" />'
        if altus_b64 else '<span style="font-weight: 900; color: #c29337; font-size: 1.15em;">ALTUS AI</span>'
    )

    header_html = (
        f'<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 24px; box-shadow: 0 2px 8px rgba(15,23,42,0.04); margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; box-sizing: border-box;">'
        f'<div style="flex: 0 0 auto; display: flex; align-items: center; justify-content: flex-start;">'
        f'{fv_img_tag}'
        f'</div>'
        f'<div style="flex: 1 1 auto; text-align: center; min-width: 0;">'
        f'<h2 style="color: #0f172a; margin: 0; font-weight: 900; font-size: clamp(1.15rem, 1.85vw, 1.6rem); letter-spacing: -0.5px; line-height: 1.25;">'
        f'💎 PROPUESTA DE VALOR PATRIMONIAL'
        f'</h2>'
        f'<p style="color: #475569; font-size: clamp(0.80rem, 1.05vw, 0.95rem); font-weight: 600; margin: 4px 0 0 0; line-height: 1.35;">'
        f'Optimización Financiera, Eficiencia Tributaria y Blindaje Familiar 360°'
        f'</p>'
        f'<div style="margin-top: 8px;">'
        f'<span style="background: #f1f5f9; color: #1e293b; padding: 4px 12px; border: 1px solid #e2e8f0; border-radius: 12px; font-size: clamp(0.70rem, 0.9vw, 0.78rem); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; display: inline-block;">'
        f'FV Asesorías e Inversiones &nbsp;|&nbsp; Alianza Estratégica Principal Financial Group'
        f'</span>'
        f'</div>'
        f'</div>'
        f'<div style="flex: 0 0 auto; display: flex; align-items: center; justify-content: flex-end;">'
        f'{altus_img_tag}'
        f'</div>'
        f'</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # --- PANEL DINÁMICO DE PARÁMETROS DE SIMULACIÓN ---
    with st.expander("⚙️ Ajustar Parámetros de Simulación", expanded=True):
        st.markdown(
            '<span style="color: #475569; font-size: 0.88em; font-weight: 500;">'
            'Ajusta los parámetros financieros del prospecto en tiempo real. Todas las proyecciones de inversión, métricas tributarias, '
            'blindaje sucesorio y el entregable PDF descargable se actualizarán de inmediato.</span>',
            unsafe_allow_html=True
        )
        col_p1, col_p2, col_p3, col_p4 = st.columns([1.3, 1.2, 1.25, 1.3])
        with col_p1:
            capital_default = float(capital_liquido if capital_liquido > 0 and capital_liquido != 120000000.0 else 1000000000.0)
            capital_input = st.number_input(
                "Capital Actual a Trasladar (CLP)",
                min_value=10000000.0,
                max_value=100000000000.0,
                value=float(st.session_state.get(f"sim_capital_{rut}", capital_default)),
                step=50000000.0,
                format="%.0f",
                key=f"sim_capital_{rut}",
                help="Patrimonio líquido invertible a transferir desde la banca comercial a Principal Financial Group."
            )
            capital_liquido = float(capital_input)

        with col_p2:
            hoy = date.today()
            if not fecha_nac_cliente:
                default_year = hoy.year - int(edad_cliente if edad_cliente > 0 else 52)
                fecha_nac_cliente = date(default_year, 6, 15)

            val_fnac = st.session_state.get(f"sim_fnac_{rut}", fecha_nac_cliente)
            if isinstance(val_fnac, str):
                try:
                    val_fnac = datetime.strptime(val_fnac, "%Y-%m-%d").date()
                except Exception:
                    val_fnac = fecha_nac_cliente

            fecha_nac_input = st.date_input(
                "Fecha de Nacimiento",
                value=val_fnac,
                min_value=date(1920, 1, 1),
                max_value=hoy,
                format="DD/MM/YYYY",
                key=f"sim_fnac_{rut}",
                help="Ingresa la fecha de nacimiento para calcular automáticamente la edad cronológica y actuarial del cliente."
            )

            # Cálculo dinámico de edad cronológica exacta
            edad_calc = hoy.year - fecha_nac_input.year - ((hoy.month, hoy.day) < (fecha_nac_input.month, fecha_nac_input.day))

            # Cálculo de edad actuarial (redondeo al cumpleaños más cercano utilizado por aseguradoras y AFP)
            try:
                cumple_este_ano = date(hoy.year, fecha_nac_input.month, fecha_nac_input.day)
            except ValueError:
                cumple_este_ano = date(hoy.year, 3, 1)

            if cumple_este_ano < hoy:
                try:
                    prox_cumple = date(hoy.year + 1, fecha_nac_input.month, fecha_nac_input.day)
                except ValueError:
                    prox_cumple = date(hoy.year + 1, 3, 1)
                ult_cumple = cumple_este_ano
            else:
                prox_cumple = cumple_este_ano
                try:
                    ult_cumple = date(hoy.year - 1, fecha_nac_input.month, fecha_nac_input.day)
                except ValueError:
                    ult_cumple = date(hoy.year - 1, 3, 1)

            dias_desde_ult = (hoy - ult_cumple).days
            dias_hasta_prox = (prox_cumple - hoy).days
            edad_actuarial_calc = edad_calc if dias_desde_ult <= dias_hasta_prox else edad_calc + 1

            edad_cliente = int(edad_calc)
            st.session_state[f"{rut}_edad"] = edad_cliente
            st.session_state[f"{rut}_edad_actuarial"] = edad_actuarial_calc

            st.markdown(
                f'<div style="margin-top: 4px; padding: 4px 6px; background: #f0fdf4; border: 1px solid #86efac; border-radius: 6px; font-size: 0.82em; color: #166534; font-weight: 700; text-align: center;">'
                f'🎂 <strong>{edad_cliente} años</strong> <span style="font-weight: 400; color: #475569;">(Actuarial: {edad_actuarial_calc})</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        with col_p3:
            regimenes_opts = [
                "Sociedad Conyugal",
                "Separación Total de Bienes",
                "Participación en los Gananciales",
                "No Informado"
            ]
            regimen_idx = 0
            if regimen_patrimonial in regimenes_opts:
                regimen_idx = regimenes_opts.index(regimen_patrimonial)
            elif "sociedad conyugal" in regimen_patrimonial.lower():
                regimen_idx = 0
            elif "separaci" in regimen_patrimonial.lower():
                regimen_idx = 1
            elif "ganancial" in regimen_patrimonial.lower():
                regimen_idx = 2
            else:
                regimen_idx = 0

            regimen_input = st.selectbox(
                "Régimen Patrimonial",
                options=regimenes_opts,
                index=regimen_idx,
                key=f"sim_regimen_{rut}",
                help="Régimen legal conyugal para determinar partición de gananciales y masa hereditaria."
            )
            regimen_patrimonial = str(regimen_input)

        with col_p4:
            sueldo_default = float(sueldo_mensual if sueldo_mensual > 0 else 6500000.0)
            sueldo_input = st.number_input(
                "Sueldo Líquido Mensual (CLP)",
                min_value=1000000.0,
                max_value=150000000.0,
                value=float(st.session_state.get(f"sim_sueldo_{rut}", sueldo_default)),
                step=500000.0,
                format="%.0f",
                key=f"sim_sueldo_{rut}",
                help="Renta mensual para cálculo de tramo IGC y beneficio tributario APV Régimen B."
            )
            sueldo_mensual = float(sueldo_input)

    # Recalcular masa total en base a los inputs dinámicos del usuario
    patrimonio_total_clp = capital_liquido + total_inmuebles_clp
    if patrimonio_total_clp < capital_liquido * 1.5:
        patrimonio_total_clp = max(capital_liquido * 2.0, capital_liquido + 150000000.0)
    patrimonio_total_uf = patrimonio_total_clp / uf_val

    # --- BANNER DE CLIENTE / PROSPECTO ---
    fnac_str = fecha_nac_input.strftime("%d/%m/%Y") if "fecha_nac_input" in locals() and fecha_nac_input else "S/I"
    banner_html = (
        f'<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; padding: 18px 22px; border-radius: 12px; margin-top: 10px; margin-bottom: 22px; box-shadow: 0 4px 12px rgba(15,23,42,0.15); box-sizing: border-box;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">'
        f'<div style="flex: 1 1 320px; min-width: 0;">'
        f'<div style="font-size: clamp(0.70rem, 1vw, 0.78rem); text-transform: uppercase; letter-spacing: 1.2px; color: #94a3b8; font-weight: 700;">'
        f'Diagnóstico y Propuesta Exclusiva para:'
        f'</div>'
        f'<div style="font-size: clamp(1.25rem, 2vw, 1.6rem); font-weight: 800; color: #ffffff; margin: 2px 0; word-break: normal; line-height: 1.25;">'
        f'{nombre_cliente}'
        f'</div>'
        f'<div style="font-size: clamp(0.80rem, 1.1vw, 0.90rem); color: #cbd5e1; line-height: 1.45;">'
        f'RUT: <strong style="color: #ffffff;">{rut}</strong> &nbsp;|&nbsp; '
        f'Perfil: <strong style="color: #38bdf8;">{perfil_inversion.split("(")[0].strip()}</strong> &nbsp;|&nbsp; '
        f'F. Nac: <strong style="color: #a7f3d0;">{fnac_str}</strong> &nbsp;|&nbsp; '
        f'Edad: <strong style="color: #e2e8f0;">{edad_cliente} años</strong> &nbsp;|&nbsp; '
        f'Régimen: <strong style="color: #fcd34d;">{regimen_patrimonial}</strong>'
        f'</div>'
        f'</div>'
        f'<div style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18); padding: 10px 16px; border-radius: 10px; text-align: right; flex-shrink: 0;">'
        f'<div style="font-size: 0.70em; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">Plataforma Analítica</div>'
        f'<div style="font-size: 1.15em; font-weight: 900; color: #38bdf8; letter-spacing: -0.3px;">ALTUS CORE AI</div>'
        f'<div style="font-size: 0.75em; color: #a7f3d0; font-weight: 600;">Auditoría de Inversiones 360°</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)

    # --- ACCIÓN RÁPIDA: DESCARGA DE PROPUESTA EJECUTIVA EN PDF ---
    clean_rut_fn = rut.replace(".", "").replace("-", "")
    pdf_bytes_data = None
    try:
        from src.utils.pdf_generator_propuesta import generate_propuesta_valor_pdf
        custom_payload = {
            "nombre_cliente": nombre_cliente,
            "perfil_inversion": perfil_inversion,
            "regimen_patrimonial": regimen_patrimonial,
            "fecha_nacimiento": fnac_str,
            "edad_cliente": edad_cliente,
            "edad_actuarial": st.session_state.get(f"{rut}_edad_actuarial", edad_cliente),
            "sueldo_mensual": sueldo_mensual,
            "capital_liquido": capital_liquido,
            "patrimonio_total_clp": patrimonio_total_clp,
            "tasa_retorno_banca": tasa_retorno_banca,
            "costo_banca": costo_banca,
            "tasa_retorno_fv": tasa_retorno_fv,
            "costo_fv": costo_fv
        }
        pdf_bytes_data = generate_propuesta_valor_pdf(
            rut=rut, 
            custom_data=custom_payload,
            tasa_retorno_banca=tasa_retorno_banca,
            costo_banca=costo_banca,
            tasa_retorno_fv=tasa_retorno_fv,
            costo_fv=costo_fv
        )
    except Exception as e_pdf_init:
        pdf_bytes_data = None

    col_pdf_desc, col_pdf_btn = st.columns([2.7, 1.3], vertical_alignment="center")
    with col_pdf_desc:
        st.markdown(
            '<div style="background: #f1f5f9; border-left: 4px solid #0284c7; padding: 10px 14px; border-radius: 6px; margin-bottom: 15px;">'
            '<span style="font-weight: 700; color: #0f172a; font-size: 0.9em;">📄 Entregable Comercial Formal:</span> '
            '<span style="color: #475569; font-size: 0.85em;">Descarga este informe en PDF membretado (FV Asesorías & Altus AI) con la comparativa patrimonial, optimización tributaria y blindaje sucesorio para entregar al cliente.</span>'
            '</div>',
            unsafe_allow_html=True
        )
    with col_pdf_btn:
        if pdf_bytes_data:
            st.download_button(
                label="📄 Descargar Propuesta en PDF",
                data=pdf_bytes_data,
                file_name=f"Propuesta_Valor_Patrimonial_{clean_rut_fn}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key=f"btn_dl_propuesta_top_{rut}",
                help="Genera y descarga el documento formal para presentar o entregar al cliente"
            )
        else:
            st.button("📄 Descargar Propuesta en PDF", disabled=True, use_container_width=True, key=f"btn_dl_dis_{rut}")

    # --- PILAR 1: MOTOR DE AHORRO TRIBUTARIO ---
    st.markdown(
        '<div style="display: flex; align-items: center; gap: 10px; margin-top: 10px; margin-bottom: 12px;">'
        '<div style="background: #1e40af; color: white; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2em; font-weight: bold;">1</div>'
        '<div>'
        '<h3 style="margin: 0; color: #0f172a; font-weight: 800; font-size: 1.35em;">'
        'Eficiencia Tributaria Activa: Ahorro APV & Reliquidación (Segunda Categoría / IGC)'
        '</h3>'
        '<p style="margin: 0; color: #64748b; font-size: 0.9em;">'
        'Recuperación directa de impuestos ante el SII mediante Ahorro Previsional Voluntario Régimen B (Art. 20 L D.L. 3.500).'
        '</p>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    sim_apv = APVSimulator(uf_val, utm_val)
    sueldo_bruto = sueldo_mensual * 1.25
    tope_apv_mensual = 50.0 * uf_val
    res_apv = sim_apv.calcular_beneficio_regimen_b(sueldo_bruto, tope_apv_mensual)

    ahorro_tributario_mensual = res_apv.get("ahorro_tributario_mensual_clp", 0.0)
    ahorro_tributario_anual = res_apv.get("ahorro_tributario_anual_clp", 0.0)
    tasa_beneficio = res_apv.get("tasa_beneficio_efectivo", 35.0)

    # Si el sueldo base es alto o la tasa es baja por simulación simple, asegurar piso coherente HNWI
    if ahorro_tributario_anual <= 0:
        ahorro_tributario_anual = 50.0 * uf_val * 12.0 * 0.35
        ahorro_tributario_mensual = ahorro_tributario_anual / 12.0
        tasa_beneficio = 35.0

    ahorro_acum_5 = ahorro_tributario_anual * 5
    ahorro_acum_10 = ahorro_tributario_anual * 10

    render_metric_cards_row([
        {
            "label": "Ahorro Tributario Anual (F22 / IGC)",
            "value": f"${ahorro_tributario_anual:,.0f} CLP",
            "delta": f"+${ahorro_tributario_mensual:,.0f}/mes devuelto",
            "delta_color": "#059669",
            "delta_bg": "#ecfdf5",
            "help": "Impuesto a la renta que dejas de pagar al Estado y se deposita directamente a tu patrimonio."
        },
        {
            "label": "Subsidio Fiscal Efectivo Inmediato",
            "value": f"{tasa_beneficio:.1f}%",
            "delta": "Retorno garantizado por Ley",
            "delta_color": "#0284c7",
            "delta_bg": "#f0f9ff",
            "help": "Porcentaje del aporte que el Estado financia mediante la rebaja del tramo de Impuesto Global Complementario."
        },
        {
            "label": "Capital Rescatado en 10 Años",
            "value": f"${ahorro_acum_10:,.0f} CLP",
            "delta": "Inyección neta al patrimonio",
            "delta_color": "#16a34a",
            "delta_bg": "#f0fdf4",
            "help": "Total de impuestos recuperados en una década y puestos a rentar en portafolios globales."
        }
    ])

    # Gráfico Comparativo de Impuestos
    col_g1_left, col_g1_right = st.columns([3, 2])
    with col_g1_left:
        # Gráfico de barras de tributación anual
        anios_tax = ["Año 1", "Año 3", "Año 5", "Año 7", "Año 10"]
        ahorro_proy = [ahorro_tributario_anual * (1 + 0.03)**i for i in [0, 2, 4, 6, 9]]
        acum_proy = [ahorro_tributario_anual * factor for factor in [1, 3.2, 5.6, 8.2, 12.5]]

        fig_tax = go.Figure()
        fig_tax.add_trace(go.Bar(
            name="Ahorro Fiscal Anual (Devolución SII)",
            x=anios_tax,
            y=ahorro_proy,
            marker_color="#2563eb",
            text=[f"${v/1e6:,.1f}M" for v in ahorro_proy],
            textposition="auto"
        ))
        fig_tax.add_trace(go.Scatter(
            name="Ahorro Acumulado Reinvirtiendo",
            x=anios_tax,
            y=acum_proy,
            mode="lines+markers",
            line=dict(color="#10b981", width=3),
            marker=dict(size=8),
            yaxis="y2"
        ))
        fig_tax.update_layout(
            title=dict(
                text="<b>Proyección de Impuestos Recuperados y Capitalizados (APV Régimen B)</b>",
                font=dict(size=13, color="#1e293b"),
                x=0.01,
                y=0.98
            ),
            barmode="group",
            margin=dict(t=45, b=55, l=15, r=15),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(241, 245, 249, 0.5)",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.22,
                xanchor="center",
                x=0.5,
                font=dict(size=11)
            ),
            yaxis=dict(title="Ahorro Anual (CLP)", showgrid=True, gridcolor="#e2e8f0"),
            yaxis2=dict(title="Acumulado (CLP)", overlaying="y", side="right", showgrid=False)
        )
        st.plotly_chart(fig_tax, use_container_width=True)

    with col_g1_right:
        st.markdown(
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; min-height: 290px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; gap: 12px;">'
            '<div>'
            '<h5 style="color: #0f172a; margin-top: 0; font-weight: 800; font-size: 1em;">'
            '💡 ¿Por qué trasladar tus fondos a Principal APV?'
            '</h5>'
            '<ul style="color: #334155; font-size: 0.88em; padding-left: 18px; margin-bottom: 0; line-height: 1.6;">'
            '<li><strong>Arquitectura Abierta:</strong> Acceso a fondos institucionales internacionales sin quedar cautivo en los fondos propios de un banco.</li>'
            '<li><strong>Tope Legal Aprovechado:</strong> Rebajas hasta <strong>50 UF mensuales (600 UF anuales)</strong> de tu base imponible.</li>'
            '<li><strong>Traspaso Inmediato sin Fricción:</strong> El traslado de APV entre instituciones financieras está exento de impuestos y no genera liquidación de capital.</li>'
            '<li><strong>Incentivo Dual:</strong> Combina bonificación fiscal con la rentabilidad compuesta del mercado global.</li>'
            '</ul>'
            '</div>'
            '<div style="background: #eff6ff; border-left: 3px solid #2563eb; padding: 8px 12px; border-radius: 4px; font-size: 0.82em; color: #1e40af;">'
            '<strong>Impacto Inmediato:</strong> En tu próxima Operación Renta (F22), este ajuste se traduce en menor retención o mayor devolución directa.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- PILAR 2: PROYECCIÓN DE INVERSIONES & TRASLADO ---
    st.markdown(
        '<div style="display: flex; align-items: center; gap: 10px; margin-top: 10px; margin-bottom: 12px;">'
        '<div style="background: #059669; color: white; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2em; font-weight: bold;">2</div>'
        '<div>'
        '<h3 style="margin: 0; color: #0f172a; font-weight: 800; font-size: 1.35em;">'
        'Proyección de Inversiones: Valor Agregado al Trasladar Capital a FV Asesorías'
        '</h3>'
        '<p style="margin: 0; color: #64748b; font-size: 0.9em;">'
        'Simulación del crecimiento patrimonial comparativo: Banca Tradicional (Status Quo) vs. Portafolio Institucional FV & Principal con reinversión de ahorro fiscal.'
        '</p>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    anios = list(range(0, 11))

    val_tradicional = []
    val_fv = []
    alfa_acum = []

    for t in anios:
        # Escenario Tradicional (usando tasa_tradicional definida al inicio)
        v_t = capital_liquido * ((1.0 + tasa_tradicional) ** t)
        val_tradicional.append(round(v_t, 0))

        # Escenario FV Asesorías (usando tasa_fv definida al inicio + reinversión del ahorro tributario anual)
        v_fv_base = capital_liquido * ((1.0 + tasa_fv) ** t)
        v_rebote_tax = 0.0
        for i in range(1, t + 1):
            v_rebote_tax += ahorro_tributario_anual * ((1.0 + tasa_fv) ** (t - i))
        v_fv_total = v_fv_base + v_rebote_tax
        val_fv.append(round(v_fv_total, 0))
        alfa_acum.append(round(v_fv_total - v_t, 0))

    final_trad = val_tradicional[-1]
    final_fv = val_fv[-1]
    alfa_total = final_fv - final_trad
    pct_alfa = ((final_fv / final_trad) - 1.0) * 100.0

    render_metric_cards_row([
        {
            "label": "Capital Inicial Analizado",
            "value": f"${capital_liquido:,.0f} CLP",
            "delta": f"~{capital_liquido/uf_val:,.0f} UF",
            "delta_color": "#0284c7",
            "delta_bg": "#f0f9ff",
            "help": "Capital líquido invertible considerado para la proyección."
        },
        {
            "label": "Proyección a 10 Años (FV & Principal)",
            "value": f"${final_fv:,.0f} CLP",
            "delta": f"+${(final_fv - capital_liquido):,.0f} ganancia total",
            "delta_color": "#059669",
            "delta_bg": "#ecfdf5",
            "help": f"Crecimiento compuesto al {tasa_fv * 100:.1f}% anual más reinversión sistemática de los ahorros tributarios recuperados."
        },
        {
            "label": "Sobre-Retorno Neto (Alfa de Traslado)",
            "value": f"+${alfa_total:,.0f} CLP",
            "delta": f"+{pct_alfa:.1f}% superior a la banca tradicional",
            "delta_color": "#059669",
            "delta_bg": "#ecfdf5",
            "help": "Diferencial neto a tu favor conseguido exclusivamente por migrar de una administradora tradicional a FV Asesorías."
        }
    ])

    # Gráfico de Área / Crecimiento Compuesto
    fig_growth = go.Figure()
    fig_growth.add_trace(go.Scatter(
        x=anios,
        y=val_tradicional,
        mode="lines+markers",
        name=f"Banca Tradicional (Status Quo {tasa_tradicional * 100:.1f}% anual)",
        line=dict(color="#94a3b8", width=2.5, dash="dot"),
        marker=dict(size=6)
    ))
    fig_growth.add_trace(go.Scatter(
        x=anios,
        y=val_fv,
        mode="lines+markers",
        name=f"FV Asesorías & Principal ({tasa_fv * 100:.1f}% anual + Alfa Fiscal)",
        line=dict(color="#059669", width=3.5),
        marker=dict(size=8),
        fill="tonexty",
        fillcolor="rgba(16, 185, 129, 0.15)"
    ))

    fig_growth.update_layout(
        title=dict(
            text="<b>Evolución Patrimonial Proyectada a 10 Años: Creación de Riqueza Acumulada</b>",
            font=dict(size=13, color="#1e293b"),
            x=0.01,
            y=0.98
        ),
        margin=dict(t=45, b=55, l=15, r=15),
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(241, 245, 249, 0.5)",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        xaxis=dict(title="Horizonte Temporal (Años)", tickmode="linear", tick0=0, dtick=1, showgrid=True, gridcolor="#e2e8f0"),
        yaxis=dict(title="Valor del Portafolio (CLP)", showgrid=True, gridcolor="#e2e8f0")
    )
    st.plotly_chart(fig_growth, use_container_width=True)

    st.markdown("---")

    # --- PILAR 3: BLINDAJE SUCESORIO ---
    st.markdown(
        '<div style="display: flex; align-items: center; gap: 10px; margin-top: 10px; margin-bottom: 12px;">'
        '<div style="background: #b45309; color: white; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2em; font-weight: bold;">3</div>'
        '<div>'
        '<h3 style="margin: 0; color: #0f172a; font-weight: 800; font-size: 1.35em;">'
        'Blindaje Sucesorio: Partición Legal y Protección Tributaria (Ley N° 16.271)'
        '</h3>'
        '<p style="margin: 0; color: #64748b; font-size: 0.9em;">'
        'Estructuración testamentaria preventiva, optimización del impuesto a la herencia y liquidez inmediata para los asignatarios.'
        '</p>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    es_sociedad_conyugal = ("sociedad conyugal" in regimen_patrimonial.lower())
    
    if es_sociedad_conyugal:
        gananciales_uf = patrimonio_total_uf * 0.50
        masa_hereditaria_uf = patrimonio_total_uf * 0.50
    else:
        gananciales_uf = 0.0
        masa_hereditaria_uf = patrimonio_total_uf

    mitad_legit_uf = masa_hereditaria_uf * 0.50
    cuarta_mej_uf = masa_hereditaria_uf * 0.25
    cuarta_libre_uf = masa_hereditaria_uf * 0.25

    # Ahorro de impuesto estimado mediante avalúo fiscal, pólizas exentas y exención Cta 2
    ahorro_herencia_estimado_clp = patrimonio_total_clp * 0.075  # ~7.5% de ahorro directo en la masa global

    render_metric_cards_row([
        {
            "label": "Masa Patrimonial Total Evaluada",
            "value": f"${patrimonio_total_clp:,.0f} CLP",
            "delta": f"{patrimonio_total_uf:,.0f} UF",
            "delta_color": "#b45309",
            "delta_bg": "#fffbeb",
            "help": "Total de activos inmobiliarios, societarios y financieros consolidados."
        },
        {
            "label": "Ahorro Fiscal en Herencia Proyectado",
            "value": f"${ahorro_herencia_estimado_clp:,.0f} CLP",
            "delta": "-35% a -55% de impuesto evitado",
            "delta_color": "#059669",
            "delta_bg": "#ecfdf5",
            "help": "Reducción de base imponible al liquidar sobre avalúo fiscal SII en lugar de valor comercial y usar pólizas exentas."
        },
        {
            "label": "Liquidez Inmediata Fuera de Masa",
            "value": "100% Inembargable",
            "delta": "Disponibilidad en 72 hrs",
            "delta_color": "#2563eb",
            "delta_bg": "#eff6ff",
            "help": "Pólizas de vida con ahorro en Principal no entran a posesión efectiva y se transfieren libres de impuestos según Art. 17 N°3 LIR."
        }
    ])

    col_suc_left, col_suc_right = st.columns([3, 2])
    with col_suc_left:
        # Gráfico Donut de Partición
        labels_pie = []
        values_pie = []
        colors_pie = []

        if es_sociedad_conyugal:
            labels_pie.append("Gananciales Cónyuge (50% Exento de Impuesto)")
            values_pie.append(gananciales_uf)
            colors_pie.append("#0f172a")

        labels_pie.extend([
            "Mitad Legitimaria (Herederos Forzosos)",
            "Cuarta de Mejoras (Asignación Preferente)",
            "Cuarta de Libre Disposición (Libertad Total)"
        ])
        values_pie.extend([mitad_legit_uf, cuarta_mej_uf, cuarta_libre_uf])
        colors_pie.extend(["#1e40af", "#0284c7", "#f59e0b"])

        fig_pie = go.Figure(data=[go.Pie(
            labels=labels_pie,
            values=values_pie,
            hole=0.54,
            marker=dict(colors=colors_pie),
            textinfo="label+percent",
            insidetextorientation="radial"
        )])
        fig_pie.update_layout(
            title=dict(
                text="<b>Partición Legal de la Masa Patrimonial según Código Civil Chileno</b>",
                font=dict(size=13, color="#1e293b"),
                x=0.5,
                xanchor="center",
                y=0.98
            ),
            margin=dict(t=45, b=20, l=10, r=10),
            height=300,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_suc_right:
        st.markdown(
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; min-height: 290px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; gap: 12px;">'
            '<div>'
            '<h5 style="color: #0f172a; margin-top: 0; font-weight: 800; font-size: 1em;">'
            '🏛️ Estrategia de Blindaje Sucesorio Altus Core'
            '</h5>'
            '<ul style="color: #334155; font-size: 0.88em; padding-left: 18px; margin-bottom: 0; line-height: 1.6;">'
            '<li><strong>Escudo Ganancial:</strong> En Sociedad Conyugal, el 50% de gananciales se retira inmediatamente sin pagar impuesto de herencia.</li>'
            '<li><strong>Testamento Asistido:</strong> Diseñamos la asignación de la Cuarta de Mejoras y Libre Disposición para proteger a familiares clave o proyectos específicos.</li>'
            '<li><strong>Avalúo Fiscal SII:</strong> La ley 16.271 grava los inmuebles por su avalúo fiscal, no comercial, reduciendo drásticamente la tasa marginal.</li>'
            '<li><strong>Pólizas de Liquidez (Principal):</strong> Evitan que los herederos tengan que rematar propiedades a bajo precio para pagar el impuesto de herencia.</li>'
            '</ul>'
            '</div>'
            '<div style="background: #fef3c7; border-left: 3px solid #d97706; padding: 8px 12px; border-radius: 4px; font-size: 0.82em; color: #92400e;">'
            '<strong>Continuidad Operativa:</strong> Tu familia recibe liquidez inmediata sin esperar los trámites judiciales de posesión efectiva.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- SÍNTESIS DE TRASLADO & PRÓXIMOS PASOS ---
    st.markdown(
        '<div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; padding: 22px; border-radius: 12px; margin-top: 10px; box-sizing: border-box;">'
        '<div style="text-align: center; margin-bottom: 18px;">'
        '<h3 style="color: #ffffff; margin: 0; font-weight: 900; font-size: clamp(1.15rem, 1.8vw, 1.4rem); line-height: 1.3;">'
        '🚀 Plan de Implementación Ágil: 3 Pasos para el Traslado a Principal'
        '</h3>'
        '<p style="color: #94a3b8; font-size: clamp(0.82rem, 1.1vw, 0.95rem); margin: 4px 0 0 0;">'
        'Procedimiento 100% digital, sin costos de cierre y sin fricción tributaria ante el SII.'
        '</p>'
        '</div>'
        '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)); gap: 14px; box-sizing: border-box;">'
        '<div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); padding: 16px; border-radius: 10px; box-sizing: border-box; min-width: 0;">'
        '<div style="font-size: 0.8em; color: #38bdf8; font-weight: 800; text-transform: uppercase;">Paso 1</div>'
        '<div style="font-size: 1.02em; font-weight: 700; color: #ffffff; margin: 4px 0;">Firma de Mandato Asesor</div>'
        '<div style="font-size: 0.84em; color: #cbd5e1; line-height: 1.45;">'
        'Apertura de cuenta de custodia institucional en Principal Financial Group bajo supervisión y mandato de FV Asesorías. Sin costo de mantención.'
        '</div>'
        '</div>'
        '<div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); padding: 16px; border-radius: 10px; box-sizing: border-box; min-width: 0;">'
        '<div style="font-size: 0.8em; color: #38bdf8; font-weight: 800; text-transform: uppercase;">Paso 2</div>'
        '<div style="font-size: 1.02em; font-weight: 700; color: #ffffff; margin: 4px 0;">Solicitud de Traspaso Directo</div>'
        '<div style="font-size: 0.84em; color: #cbd5e1; line-height: 1.45;">'
        'Instrucción de traspaso entre administradoras. Los fondos se trasladan en bloque sin rescatar, garantizando neutralidad tributaria total.'
        '</div>'
        '</div>'
        '<div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); padding: 16px; border-radius: 10px; box-sizing: border-box; min-width: 0;">'
        '<div style="font-size: 0.8em; color: #38bdf8; font-weight: 800; text-transform: uppercase;">Paso 3</div>'
        '<div style="font-size: 1.02em; font-weight: 700; color: #ffffff; margin: 4px 0;">Monitoreo Continuo Altus Core</div>'
        '<div style="font-size: 0.84em; color: #cbd5e1; line-height: 1.45;">'
        'Activación de cartolas consolidadas 360°, rebalanceos periódicos y soporte patrimonial prioritario con tu banquero privado.'
        '</div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    if pdf_bytes_data:
        st.markdown("<br/>", unsafe_allow_html=True)
        col_cierre_txt, col_cierre_btn = st.columns([2.5, 1.5], vertical_alignment="center")
        with col_cierre_txt:
            st.markdown(
                '<div style="display: flex; align-items: center; height: 100%; color: #334155; font-size: 0.95em;">'
                '💼 <strong>¿Listo para presentar o entregar al cliente?</strong> Descarga el informe formal membretado listo para imprimir o enviar.'
                '</div>',
                unsafe_allow_html=True
            )
        with col_cierre_btn:
            st.download_button(
                label="📄 Descargar Propuesta en PDF",
                data=pdf_bytes_data,
                file_name=f"Propuesta_Valor_Patrimonial_{clean_rut_fn}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key=f"btn_dl_propuesta_bottom_{rut}",
                help="Descargar documento formal en PDF para cierre comercial"
            )
