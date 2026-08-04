import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import sys
import datetime
import asyncio
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Reparación del motor interno de Windows para evitar el colapso de Playwright en subprocesos
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

# Asegurar que el directorio raíz esté en el path para las importaciones
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

from src.database.connection import engine
from sqlalchemy import text
from src.database.models import Prospect
from src.analytics.monte_carlo import MonteCarloSimulator

# PARCHE SQL EN CALIENTE: Migramos la base automáticamente sin perder datos.
for query in [
    "ALTER TABLE prospects ADD COLUMN es_cliente INTEGER DEFAULT 0",
    "ALTER TABLE prospects ADD COLUMN nombre_rrll VARCHAR(200)",
    "ALTER TABLE prospects ADD COLUMN rut_rrll VARCHAR(30)",
    "ALTER TABLE prospects ADD COLUMN score_liquidez INTEGER DEFAULT 0",
    "ALTER TABLE prospects ADD COLUMN ultimo_evento VARCHAR(500)",
    "ALTER TABLE prospects ADD COLUMN fecha_hallazgo VARCHAR(50)",
    "ALTER TABLE prospects ADD COLUMN link_fuente VARCHAR(500)",
    "ALTER TABLE prospects ADD COLUMN origen_web INTEGER DEFAULT 0",
    "ALTER TABLE client_insurances ADD COLUMN asegurado VARCHAR(200)",
    "ALTER TABLE client_insurances ADD COLUMN contratante VARCHAR(200)",
    "ALTER TABLE client_insurances ADD COLUMN colectivo_individual VARCHAR(50)",
    "ALTER TABLE client_insurances ADD COLUMN bien_asegurado_tipo VARCHAR(100)",
    "ALTER TABLE client_insurances ADD COLUMN alias_patente VARCHAR(100)",
    "ALTER TABLE client_profiles ADD COLUMN nombres VARCHAR(150)",
    "ALTER TABLE client_profiles ADD COLUMN apellido_paterno VARCHAR(100)",
    "ALTER TABLE client_profiles ADD COLUMN apellido_materno VARCHAR(100)",
    "ALTER TABLE client_profiles ADD COLUMN renta_anual_declarada FLOAT DEFAULT 0.0",
    "ALTER TABLE client_profiles ADD COLUMN tipo_persona VARCHAR(20) DEFAULT 'PN'",
    "ALTER TABLE client_profiles ADD COLUMN audio_path VARCHAR(500)",
    "ALTER TABLE client_profiles ADD COLUMN fecha_constitucion DATE",
    "ALTER TABLE client_profiles ADD COLUMN notaria_constitucion VARCHAR(200)",
    "ALTER TABLE client_profiles ADD COLUMN repertorio_constitucion VARCHAR(100)",
    "ALTER TABLE client_profiles ADD COLUMN fecha_ultima_vigencia DATE",
    "ALTER TABLE client_profiles ADD COLUMN documentos_legales_path VARCHAR(500)"
]:
    try:
        with engine.connect() as con:
            con.execute(text(query))
            con.commit()
    except Exception:
        pass 

from src.messaging.spintax import format_message
from src.messaging.anti_ban import AntiBanManager
from src.messaging.whatsapp_web import WhatsAppBot
from src.utils.finance.external_fetcher import fetch_external_asset
from src.database.models import Base

Base.metadata.create_all(bind=engine)

st.set_page_config(page_title="Altus AI - FV Asesorías", layout="wide", initial_sidebar_state="expanded")

# --- IDENTIDAD VISUAL Y DISEÑO PREMIUM ---
LOGO_PATH = os.path.join(root_path, "assets", "brand", "fv_logo_vector_pure.svg")
ALTUS_LOGO_PATH = os.path.join(root_path, "assets", "brand", "altus_ai_logo_dark.svg")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    /* Fuente solo para texto, no para iconos de sistema */
    .main, .sidebar-content, div[data-testid="stMarkdownContainer"] p {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stDeployButton {display:none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    /* Títulos Principales */
    .main h1, .main h2, .main h3 {
        font-weight: 900 !important;
        color: #1f2937 !important;
        letter-spacing: -0.03em !important;
        margin-top: 2rem !important;
    }
    
    /* Contenedores de Métricas Pro */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        white-space: normal !important;
        word-break: break-all !important;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e5e7eb !important;
    }
</style>
""", unsafe_allow_html=True)

def get_prospects() -> List[Dict]:
    """Trae prospectos listos de la BD SQLite e ignora los incompletos"""
    # Esta función se mantiene para compatibilidad, pero ahora usamos el flujo de lectura de SQL directo
    return []

def mark_contacted(prospect_id: int, status: str = "Contactado"):
    """Sella un contacto que fue visitado u omitido."""
    try:
        with engine.connect() as con:
            con.execute(text("UPDATE prospects SET status_contacto = :status WHERE id = :pid"), 
                        {"status": status, "pid": prospect_id})
            con.commit()
    except Exception as e:
        import traceback
        print("Error en mark_contacted:", e)

import re

# --- CARGA DINÁMICA DE INDICADORES (API) ---
@st.cache_data(ttl=3600)
def fetch_indicators():
    import requests
    from datetime import datetime, timedelta
    try:
        data = requests.get("https://mindicador.cl/api").json()
        uf_today = data.get('uf', {}).get('valor', 40013.88)
        
        # --- CÁLCULO DE INFLACIÓN HISTÓRICA REAL (BASADO EN UF) ---
        def get_hist_uf(target_date):
            try:
                # Cache local para no re-pedir el mismo año
                url_hist = f"https://mindicador.cl/api/uf/{target_date.year}"
                serie = requests.get(url_hist).json().get('serie', [])
                target_s = target_date.strftime("%Y-%m-%d")
                # Buscamos el valor más cercano (la serie viene desc.)
                for item in serie:
                    if item['fecha'][:10] <= target_s:
                        return item['valor']
                return serie[-1]['valor'] if serie else None
            except:
                return None

        today = datetime.now()
        uf_1y = get_hist_uf(today - timedelta(days=365))
        uf_3y = get_hist_uf(today - timedelta(days=1095))
        uf_5y = get_hist_uf(today - timedelta(days=1825))

        return {
            "UF": uf_today,
            "UTM": data.get('utm', {}).get('valor', 71500),
            "IPC": data.get('ipc', {}).get('valor', -0.2),
            "USD": data.get('dolar', {}).get('valor', 985.40),
            "TPM": data.get('tpm', {}).get('valor', 5.25),
            "uf_1y": uf_1y,
            "uf_3y": uf_3y,
            "uf_5y": uf_5y,
            "infl_1y": (uf_today / uf_1y - 1) * 100 if uf_1y else 4.5,
            "infl_3y": (uf_today / uf_3y - 1) * 100 if uf_3y else 43.75,
            "infl_5y": (uf_today / uf_5y - 1) * 100 if uf_5y else 73.86,
            "last_sync": today.strftime("%d/%m/%Y %H:%M")
        }
    except:
        return {
            "UF": 40013.88, "UTM": 71500, "IPC": 4.5, "USD": 985.40, "TPM": 5.25, 
            "uf_1y": 38290, "uf_3y": 28000, "uf_5y": 27500,
            "infl_1y": 4.5, "infl_3y": 43.75, "infl_5y": 73.86,
            "last_sync": "Modo Offline"
        }

indicators = fetch_indicators()
UF_VALOR = indicators['UF']
UTM_VALOR = indicators['UTM']
IPC_VALOR = indicators['IPC']
TPM_VALOR = indicators['TPM']
USD_CLP = indicators['USD']
UF_1Y = indicators['uf_1y']
UF_3Y = indicators['uf_3y']
UF_5Y = indicators['uf_5y']
INFL_1Y = indicators['infl_1y']
INFL_3Y = indicators['infl_3y']
INFL_5Y = indicators['infl_5y']
LAST_SYNC = indicators['last_sync']

def fmt_clp(v):
    """Formatea valores monetarios CLP.
    Si el valor es None, devuelve una cadena placeholder "N/D" para evitar errores de formato.
    """
    if v is None:
        return "N/D"
    return f"$ {v:,.0f}".replace(",", ".")

def fmt_uf(v):
    """Formatea valores de UF con dos decimales.
    Maneja None devolviendo "N/D".
    """
    if v is None:
        return "N/D"
    return f"UF {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(v):
    """Formatea valores porcentuales.
    Maneja None devolviendo "N/D".
    """
    if v is None:
        return "N/D"
    return f"{v:.2f}%".replace(".", ",")

# ----------------- INTELIGENCIA TRIBUTARIA (CHILE PRO) -----------------
def calcular_tax_alpha(monto, regimen, tasa_igc, vehiculo, pesos, fondos_info, años_vigencia=5):
    beneficio = 0
    desc_ahorro = ""
    
    # 1. Beneficios Previsionales (APV)
    if "Regimen Previsional" in regimen:
        beneficio = monto * (tasa_igc / 100)
        desc_ahorro = f"Ahorro tributario APV (Devolución): {fmt_clp(beneficio)}"
    
    # 2. Seguro de Vida (Art. 18 Bis / 17 N°3)
    if "Seguro" in vehiculo:
        # A. Beneficio No Renta (85 UTM total)
        exencion_max = 85 * UTM_VALOR
        beneficio += exencion_max * 0.10 # Impacto estimado
        desc_ahorro += f"\nIngreso No Renta (Exención 85 UTM): {fmt_clp(exencion_max)}"
        
        # B. Diferimiento y Capital Primero
        # En seguros, el rescate es Capital (UF) primero = $0 Impuesto inicial
        beneficio_dif = monto * 0.015 # Mayor eficiencia por orden de retiro
        beneficio += beneficio_dif
        desc_ahorro += f"\nEficiencia Desacumulación (Capital Primero): {fmt_clp(beneficio_dif)}"
    
    # 3. Art. 107 LIR (Presencia Bursátil) - QUIRÚRGICO POR VEHÍCULO
    ahorro_107_total = 0
    # NOTA: Según Circular 21 del SII, si el activo está dentro de un Seguro, 
    # prima la tributación del seguro (IGC) sobre el Art 107 (10%).
    if "Seguro" not in vehiculo: 
        for f_name, peso in pesos.items():
            info = fondos_info[fondos_info['fondo_display'] == f_name].iloc[0]
            if "ACCIONES CHILE" in str(info['nombre_fondo']).upper() or "IPSA" in str(info['nombre_fondo']).upper():
                monto_f = monto * (peso/100)
                ganancia_est = monto_f * 0.08
                ahorro_107_total += ganancia_est * 0.10
    
    if ahorro_107_total > 0:
        beneficio += ahorro_107_total
        desc_ahorro += f"\nExención Art. 107 (Tasa 10% Directa): {fmt_clp(ahorro_107_total)}"
        
    return beneficio, desc_ahorro

# --- AGENTE IA: MEMORIA TÁCTICA ---
def save_client_context(rut, notas):
    import json
    mem_dir = "intelligence/memory"
    if not os.path.exists(mem_dir): os.makedirs(mem_dir)
    file_path = f"{mem_dir}/{rut.replace('.', '')}.json"
    data = {"last_update": str(datetime.now()), "insights": notas}
    with open(file_path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_all_chars=True) if hasattr(json, 'ensure_all_chars') else json.dump(data, f, indent=4)

def get_client_context(rut):
    import json
    file_path = f"intelligence/memory/{rut.replace('.', '')}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding='utf-8') as f:
            return json.load(f)
    return None

# ----------------- MÓDULO: AUDITOR FINANCIERO (MAESTRO) -----------------
def get_risk_level(tipo):
    # Lógica de Riesgo CMF (1 a 7)
    t = str(tipo).upper()
    if "ACCION" in t: return 6
    if "BALANCEADO" in t: return 4
    if "INTERNACIONAL" in t: return 5
    if "ESTRUCTURADO" in t: return 4
    if "DEUDA" in t and "CORTO" in t: return 1
    if "DEUDA" in t: return 2
    return 3

def limpiar_agf_master(txt):
    if not isinstance(txt, str): return txt
    t = txt.upper().strip()
    for s in ['ADMINISTRADORA GENERAL DE FONDOS', 'S.A.', 'SPA', 'ASSET MANAGEMENT', 'CHILE']:
        t = t.replace(s, '')
    return "BANCHILE" if "BAN" in t.strip() else t.strip()

def limpiar_fondo_master(nombre, admin, serie):
    n = str(nombre).upper()
    n = n.replace("FONDO MUTUO", "").replace("F.M.", "").replace("(2)", "").strip()
    n = n.replace("[GLB]", "").strip()
    a = str(admin).upper()
    n = n.replace(f"({a})", "").replace(a, "").strip()
    # Estandarización comercial: Mantenemos original si son distintas en costos (G vs PAT)
    series_map = {"P": "PREVISIONAL", "PAT": "PATRIMONIAL", "G": "GENERAL"}
    serie_clean = series_map.get(serie.upper(), serie.upper())
    return f"{n} FFMM [{serie_clean}]"

def render_portfolio_auditor():
    st.markdown("""
        <div style='background: #ffffff; padding: 25px; border-radius: 12px; margin-bottom: 25px; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);'>
            <h1 style='color: #111827; margin: 0; font-size: 2.2em; font-weight: 900;'>💼 Auditor de Estrategias Financieras</h1>
            <p style='color: #6b7280; margin: 5px 0 0 0; font-size: 1.1em;'>Análisis Multi-Fondo y Eficiencia de Costos Patrimoniales</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Carga de datos
    try:
        df_m = pd.read_sql("SELECT * FROM fondos_mutuos", con=engine)
        df_m['admin_limpia'] = df_m['administradora'].apply(limpiar_agf_master)
        df_m['fondo_display'] = df_m.apply(lambda r: limpiar_fondo_master(r['nombre_fondo'], r['admin_limpia'], r['serie']), axis=1)
        df_m['nivel_riesgo'] = df_m['tipo_fondo'].apply(get_risk_level)
    except:
        st.error("⚠️ Base de datos no sincronizada.")
        return

    admins = sorted(df_m['admin_limpia'].unique().tolist())

    # --- CONFIGURACION DE ESCENARIOS Y HIPÓTESIS ---
    st.markdown("<h3 style='font-size: 1.2em; color: #374151;'>⚙️ Parámetros de Escenario y Referencias Macro</h3>", unsafe_allow_html=True)
    c_cfg1, c_cfg2, c_cfg3 = st.columns([1, 1, 1.5])
    with c_cfg1:
        inflacion_anual = st.number_input("Inflación Objetivo (%)", -5.0, 15.0, 3.0, step=0.1, help="Usado para la línea de referencia de poder adquisitivo.")
    with c_cfg2:
        periodo_ref = st.selectbox("Base Histórica de Referencia", [1, 3, 5], format_func=lambda x: f"Últimos {x} Años")
    with c_cfg3:
        rent_manual = st.number_input("Rent. Nominal de la Propuesta (%)", 0.0, 30.0, 7.0, help="Escribe aquí el retorno nominal que esperas para tu propuesta patrimonial.")

    with st.expander(f"📡 Status de Datos Económicos (Sincronizado: {LAST_SYNC})", expanded=False):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("UF Hoy", fmt_clp(UF_VALOR))
        m2.metric("UTM Hoy", fmt_clp(UTM_VALOR))
        m3.metric("Dólar", f"${USD_CLP}")
        m4.metric("IPC", f"{IPC_VALOR}%")
    
    st.markdown("---")
    
    # Toggle CLP / UF
    col_v1, col_v2 = st.columns([2, 1])
    with col_v2:
        moneda = st.radio("Unidad de Medida", ["Pesos (CLP)", "UF"], horizontal=True)
    
    with col_v1:
        st.write(f"💸 **Valor UF Hoy:** {fmt_clp(UF_VALOR)}")

    def fmt_m_din(v): return fmt_clp(v) if moneda == "Pesos (CLP)" else fmt_uf(v/UF_VALOR)

    col1, col2 = st.columns(2)
    with col1:
        opciones = st.session_state.get('opciones_auditor', {"Regimen General": 100000000, "Regimen Previsional (APV/DC)": 100000000})
        reg_t = st.selectbox("Régimen de Inversión / Cartera", list(opciones.keys()), key="reg_t")
    with col2:
        # Ajustamos min_value dinámicamente para evitar error al cambiar a UF (Pesos 100k, UF 250)
        min_v = 100000 if moneda=="Pesos (CLP)" else 250
        max_v = 100000000000 if moneda=="Pesos (CLP)" else 5000000
        # Asignar el capital consolidado dependiendo del régimen seleccionado
        default_capital = int(opciones.get(reg_t, 100000000))
            
        val_ini = default_capital if moneda=="Pesos (CLP)" else int(default_capital / UF_VALOR)
        
        # Limitar val_ini dentro del rango permitido
        val_ini = max(min_v, min(val_ini, max_v))
        
        step_v = 1000000 if moneda=="Pesos (CLP)" else 100
        
        capa = st.number_input(f"Capital a Auditar ({moneda})", min_v, max_v, val_ini, step=step_v)
        # Etiqueta dinámica de ayuda visual
        if moneda == "Pesos (CLP)":
             st.markdown(f"<p style='color: #059669; font-size: 1.1em; font-weight: bold;'>💵 Formato: {fmt_clp(capa)}</p>", unsafe_allow_html=True)
        else:
             st.markdown(f"<p style='color: #059669; font-size: 1.1em; font-weight: bold;'>📝 Formato: {fmt_uf(capa)}</p>", unsafe_allow_html=True)
        if moneda == "UF": capa *= UF_VALOR # Internamente operamos en Pesos

    c_g3 = st.columns(1)[0]
    with c_g3:
        plazo_proj = st.slider("Plazo de Proyección (Años)", 1, 20, 10, help="Simulación de interés compuesto y eficiencia de costos a largo plazo.")
        horizonte = st.selectbox("Rentabilidad Escenario (Histórica)", ["Último Año", "Últimos 3 Años", "Últimos 5 Años"])
        map_rent = {"Último Año": "rentabilidad_1a", "Últimos 3 Años": "rentabilidad_3a", "Últimos 5 Años": "rentabilidad_5a"}
        col_rent = map_rent[horizonte]

    st.markdown("---")
    
    st.markdown("<h3 style='font-size: 1.2em; color: #374151;'>🧠 Tesis de Reestructuración & Condicionantes Estratégicos</h3>", unsafe_allow_html=True)
    notas_estrategicas = st.text_area(
        "Contexto cualitativo que será impreso en el Reporte PDF (Ej: Preferencias del cliente, motivos tributarios, activos en Hold).", 
        value="Estrategia de Transición: Se mantendrán posiciones directas por preferencia del mandante (ej. acciones), al igual que vehículos alternativos a la espera de resolución normativa tributaria (Art. 107 LIR). El capital restante se consolidará en una matriz más eficiente.",
        key="notas_estrategicas_auditor", 
        height=100
    )

    st.markdown("---")

    # --- PORTAFOLIO ACTUAL ---
    st.markdown("### 🔴 Portafolio Actual (Competencia)")
    
    # Intentar autocompletar desde la fase de Valuación
    carteras_rec = st.session_state.get('carteras_recalculadas', {})
    df_rec = None
    pesos_c = {}
    
    for key, df in carteras_rec.items():
        if key.replace("_", " ").title() == reg_t:
            df_rec = df
            break
            
    if df_rec is not None and not df_rec.empty:
        st.info("💡 Portafolio detectado automáticamente desde el Excel procesado.")
        total_aum = df_rec['NUEVO_TOTAL'].sum()
        if total_aum > 0:
            for idx, row in df_rec.iterrows():
                prod = row['PRODUCTO']
                peso = (row['NUEVO_TOTAL'] / total_aum) * 100
                if prod in pesos_c:
                    pesos_c[prod] += peso
                else:
                    pesos_c[prod] = peso
                
            with st.expander("Ver composición importada"):
                for p, w in pesos_c.items():
                    st.write(f"- {p}: {w:.1f}%")
            
            st.success("✅ Portafolio actual ponderado al 100% automáticamente.")
            portafolio_c = list(pesos_c.keys()) # Para validaciones futuras
    else:
        # Fallback a manual si no viene de valuación
        sel_adms_c = st.multiselect("1. Selecciona las Administradoras", admins, key="ms_adm_c")
        fondos_disp_c = df_m[df_m['admin_limpia'].isin(sel_adms_c)]['fondo_display'].unique().tolist()
        portafolio_c = st.multiselect("2. Selecciona y busca los fondos que ya tiene el cliente:", fondos_disp_c, key="ms_fondos_c")
        
        if portafolio_c:
            st.markdown("#### ⚖️ Ponderación de Pesos Actuales (%)")
            col_pesos_c = st.columns(len(portafolio_c))
            for i, f in enumerate(portafolio_c):
                with col_pesos_c[i]:
                    pesos_c[f] = st.number_input(f"% {f[:15]}...", 0, 100, 100//len(portafolio_c), step=5, key=f"wc_{f}")
            
            t_pc = sum(pesos_c.values())
            if t_pc != 100: st.warning(f"Suma actual: {t_pc}% (Debe ser 100%)")
            else: st.success("✅ Portafolio Competencia equilibrado.")

    st.markdown("---")

    # --- CARTERA PRINCIPAL ---
    st.markdown("### 🟢 Propuesta de Estrategia (Principal)")
    
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        vehiculo = st.selectbox("Vehículo de Inversión", ["Regimen General (FFMM Directo)", "Seguro de Vida Patrimonial Preferente"], key="veh_p")
    
    if vehiculo == "Seguro de Vida Patrimonial Preferente":
        st.markdown("#### 👥 Designación de Beneficiarios")
        n_ben = st.number_input("¿Cuántos beneficiarios desea designar?", 1, 10, 1)
        
        beneficiarios_list = []
        opciones_parentesco = [
            "Cónyuge", "Hijo (a) 1", "Hijo (a) 2", "Hijo (a) 3", "Nieto (a) 1", "Nieto (a) 2",
            "Padre", "Madre", "Abuelo", "Abuela", "Hermano (a) 1", "Persona No Relacionada"
        ]
        
        sum_porc = 0
        b_cols = st.columns(min(n_ben, 3))
        for i in range(n_ben):
            idx_col = i % 3
            with b_cols[idx_col]:
                rel = st.selectbox(f"Relación {i+1}", opciones_parentesco, key=f"rel_fin_{i}")
                p_ben = st.number_input(f"% Capital {i+1}", 0, 100, 100//n_ben if i==0 else 0, key=f"p_fin_{i}")
                sum_porc += p_ben
            beneficiarios_list.append({"Relación": rel, "%": p_ben})
        
        if sum_porc != 100:
            st.warning(f"⚠️ Distribución incompleta: {sum_porc}% de 100%")
        else:
            st.success("✅ Distribución de Capital Validada")

    # Definición de Serie Optimizada
    serie_target = "G" if "Seguro" in vehiculo else ""
    if "Previsional" in reg_t: serie_target = "P" if "Seguro" in vehiculo else ""
    
    fondos_disp_p = df_m[df_m['admin_limpia'].str.contains("PRINCIPAL", na=False)]
    
    # Filtrado inteligente por serie preferente
    if serie_target:
        fondos_disp_p = fondos_disp_p[fondos_disp_p['serie'].str.contains(serie_target, na=False)]
    
    list_p = fondos_disp_p['fondo_display'].unique().tolist()
    portafolio_p = st.multiselect("Busca y añade las estrategias de Principal (Serie PATRIMONIAL sugerida):", list_p, key="ms_fondos_p")
    
    pesos_p = {}
    if portafolio_p:
        st.markdown("#### ⚖️ Ponderación de pesos Propuesta (%)")
        col_pesos_p = st.columns(len(portafolio_p))
        for i, f in enumerate(portafolio_p):
            with col_pesos_p[i]:
                pesos_p[f] = st.number_input(f"% {f[:15]}...", 0, 100, 100//len(portafolio_p), step=5, key=f"wp_{f}")
        
        t_pp = sum(pesos_p.values())
        if t_pp != 100: st.warning(f"Suma propuesta: {t_pp}% (Debe ser 100%)")
        else: st.success("✅ Propuesta Principal equilibrada.")

    st.markdown("---")
    st.markdown("### 🏛️ Optimización Tributaria (Tax-Alpha)")
    t1, t2 = st.columns(2)
    with t1:
        tasa_igc = st.slider("Tramo Impositivo del Cliente (IGC %)", 0.0, 40.0, 13.5, step=4.5, help="Tasa marginal según sus ingresos anuales.")
    with t2:
        if "Seguro" not in vehiculo:
            bursatil = st.checkbox("Simular Fondos con Presencia Bursátil (Art. 107)", value=True)
        else:
            bursatil = False
            st.info("🛡️ Beneficios de Póliza Activos")

    if "audit_data" not in st.session_state:
        st.session_state.audit_data = None

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📊 GENERAR AUDITORÍA COMPARATIVA", help="Inicia un análisis exhaustivo cruzando la cartera actual del cliente contra el mercado (TAC y retornos oficiales).", type="primary", use_container_width=True):
        sum_c = sum(pesos_c.values()) if pesos_c else 0
        sum_p = sum(pesos_p.values()) if pesos_p else 0
        
        if not portafolio_c or not portafolio_p or abs(sum_c - 100) > 1.0 or abs(sum_p - 100) > 1.0:
            st.error(f"Asegúrate de configurar ambas carteras al 100% para generar la comparativa. (Actual: {sum_c:.1f}%, Propuesta: {sum_p:.1f}%)")
        else:
            # Marcamos que hay datos para persistir
            st.session_state.audit_data = {
                "pesos_c": pesos_c, "pesos_p": pesos_p,
                "capa": capa, "reg_t": reg_t, "tasa_igc": tasa_igc, 
                "vehiculo": vehiculo, "plazo_proj": plazo_proj, "horizonte": horizonte
            }

    if st.session_state.audit_data:
        # Recuperamos variables
        ad = st.session_state.audit_data
        pesos_c, pesos_p = ad["pesos_c"], ad["pesos_p"]
        capa, reg_t, tasa_igc = ad["capa"], ad["reg_t"], ad["tasa_igc"]
        vehiculo, plazo_proj, horizonte = ad["vehiculo"], ad["plazo_proj"], ad["horizonte"]
        
        # --- MOTOR DE CÁLCULO PATRIMONIAL ---
        inflacion_avg = 4.5 # IPC/UF promedio
        
        import difflib
        @st.cache_data
        def map_cmf_name(f_raw, available_names):
            if f_raw in available_names:
                return f_raw
            f_clean = str(f_raw).upper()
            # Si es internacional o acción local directa, ignoramos para no mezclar con fondos mutuos chilenos
            if any(x in f_clean for x in ["JP MORGAN", "PERSHING", "RIPLEY", "FALCOM", "LTM", "COLBUN", "ENJOY", "QUIÑENCO"]):
                return None
            
            f_clean = f_clean.replace("SURA", "").replace("F. I.", "").replace("FONDO MUTUO", "").strip()
            matches = difflib.get_close_matches(f_clean, available_names, n=1, cutoff=0.4)
            return matches[0] if matches else None
        
        available_cmf_names = df_m['fondo_display'].tolist()
        
        def _map_col_to_years(col):
            if '1a' in col: return "Rentabilidad_1Y"
            if '3a' in col: return "Rentabilidad_3Y"
            if '5a' in col: return "Rentabilidad_5Y"
            return "Rentabilidad_1Y"

        def get_wg_rent(pesos, col, regimen=""):
            total = 0
            for f, p in pesos.items():
                mapped_f = map_cmf_name(f, available_cmf_names)
                if mapped_f:
                    match = df_m[df_m['fondo_display']==mapped_f]
                    if not match.empty:
                        val = match.iloc[0][col]
                        clean_val = 0 if pd.isna(val) else val
                        total += clean_val * (p/100)
                else:
                    ext = fetch_external_asset(f, regimen)
                    if ext:
                        ext_col = _map_col_to_years(col)
                        val = ext.get(ext_col, 0)
                        clean_val = 0 if pd.isna(val) else val
                        total += clean_val * (p/100)
            return total

        def get_wg_tac(pesos, regimen=""):
            total = 0
            for f, p in pesos.items():
                mapped_f = map_cmf_name(f, available_cmf_names)
                if mapped_f:
                    match = df_m[df_m['fondo_display']==mapped_f]
                    if not match.empty:
                        val = match.iloc[0]['tac_anual']
                        clean_val = 0 if pd.isna(val) else val
                        total += clean_val * (p/100)
                else:
                    ext = fetch_external_asset(f, regimen)
                    if ext:
                        val = ext.get("TAC", 0)
                        clean_val = 0 if pd.isna(val) else val
                        total += clean_val * (p/100)
            return total

        # Rentabilidades Nominales Anualizadas
        r_c_1, r_c_3, r_c_5 = get_wg_rent(pesos_c, 'rentabilidad_1a', reg_t), get_wg_rent(pesos_c, 'rentabilidad_3a', reg_t), get_wg_rent(pesos_c, 'rentabilidad_5a', reg_t)
        r_p_1, r_p_3, r_p_5 = get_wg_rent(pesos_p, 'rentabilidad_1a', reg_t), get_wg_rent(pesos_p, 'rentabilidad_3a', reg_t), get_wg_rent(pesos_p, 'rentabilidad_5a', reg_t)

        # Avisar si faltan historiales en Competencia
        missing_history = [f for f in pesos_c.keys() if not map_cmf_name(f, available_cmf_names) and not fetch_external_asset(f, reg_t)]
        if missing_history:
            st.warning(f"⚠️ Algunos activos de tu cartera actual no tienen historial público o son externos ({', '.join(missing_history)}). Su rentabilidad histórica y TAC se asumirá 0% para la comparativa.")

        # Rentabilidad ACUMULADA (Total en el periodo)
        def calc_acc(r_anual, years):
            return ((1 + r_anual/100)**years - 1) * 100
            
        # Escenario 1: Referencia Histórica (Basada en periodo elegido)
        r_hist_map = {1: (r_c_1, r_p_1), 3: (r_c_3, r_p_3), 5: (r_c_5, r_p_5)}
        r_c_hist, r_p_hist = r_hist_map[periodo_ref]
        
        # TAC Ponderados (Costo de Fondos)
        tac_c = get_wg_tac(pesos_c, reg_t)
        tac_p = get_wg_tac(pesos_p, reg_t)
        
        usar_hist_real = True # Definimos variable para evitar error en Metodología
        
        # Escenario 2: Simulación del Patrimonio (Muestra en Gráfico e Indicadores)
        # Tomamos la rentabilidad del periodo seleccionado en el selector de horizonte (debajo del capital)
        r_c_raw = get_wg_rent(pesos_c, col_rent, reg_t)
        r_p_raw = get_wg_rent(pesos_p, col_rent, reg_t)
        
        # --- Lógica de Proyección Neta de Costos (TAC) ---
        # El gráfico y la mediana final son NETOS de comisiones.
        r_c_net, r_p_net = (r_c_raw - tac_c)/100, (r_p_raw - tac_p)/100
        
        # Neta Histórica para comparación en gráfico
        r_c_net_hist = (r_c_hist - tac_c)/100

        # Tabla de Rentabilidades Pro
        st.markdown("<h2 style='font-weight: 900; color: #00B140; margin-top: 1.5rem;'>📈 Análisis de Rentabilidad Histórica (CMF)</h2>", unsafe_allow_html=True)
        
        # --- BLOQUE DE TRANSPARENCIA TÉCNICA (FISHER) ---
        with st.expander("🔬 Transparencia Técnica: ¿Cómo llegamos a estos números? (Ecuación de Fisher)", expanded=True):
            st.markdown("""
            Para asegurar un estándar de nivel institucional, no restamos la inflación de forma simple (método aproximado). 
            Utilizamos la **Ecuación de Fisher**, que es el estándar global para carteras patrimoniales:
            """)
            st.latex(r"Retorno_{Real} = \frac{1 + Retorno_{Nominal}}{1 + Inflación} - 1")
            
            c_inf1, c_inf2, c_inf3 = st.columns(3)
            with c_inf1:
                st.markdown(f"**Punto 1 Año**")
                st.caption(f"UF Hoy: {fmt_clp(UF_VALOR)}")
                st.caption(f"UF Dic 2025*: {fmt_clp(UF_1Y)}")
                st.markdown(f"**Inflación: {INFL_1Y:.2f}%**")
            with c_inf2:
                st.markdown(f"**Punto 3 Años**")
                st.caption(f"UF Hoy: {fmt_clp(UF_VALOR)}")
                st.caption(f"UF Abr 2023*: {fmt_clp(UF_3Y)}")
                st.markdown(f"**Inflación: {INFL_3Y:.2f}%**")
            with c_inf3:
                st.markdown(f"**Punto 5 Años**")
                st.caption(f"UF Hoy: {fmt_clp(UF_VALOR)}")
                st.caption(f"UF Abr 2021*: {fmt_clp(UF_5Y)}")
                st.markdown(f"**Inflación: {INFL_5Y:.2f}%**")
            st.caption("*Valores recuperados en tiempo real desde mindicador.cl")

        def calc_real_with_fixed_infl(r_nom_annual, years, actual_infl_pct):
            nom_acc = (1 + r_nom_annual/100)**years
            real_acc = (nom_acc / (1 + actual_infl_pct/100) - 1) * 100
            return real_acc

        df_rent = pd.DataFrame({
            "Periodo": ["Último Año", "3 Años (Acumulado)", "5 Años (Acumulado)"],
            "Portafolio Comp. (Nominal)": [fmt_pct(calc_acc(r_c_1, 1)), fmt_pct(calc_acc(r_c_3, 3)), fmt_pct(calc_acc(r_c_5, 5))],
            "Portafolio Comp. (Real vs UF)": [fmt_pct(calc_real_with_fixed_infl(r_c_1, 1, INFL_1Y)), 
                                              fmt_pct(calc_real_with_fixed_infl(r_c_3, 3, INFL_3Y)), 
                                              fmt_pct(calc_real_with_fixed_infl(r_c_5, 5, INFL_5Y))],
            "Propuesta Principal (Nominal)": [fmt_pct(calc_acc(r_p_1, 1)), fmt_pct(calc_acc(r_p_3, 3)), fmt_pct(calc_acc(r_p_5, 5))],
            "Propuesta Principal (Real vs UF)": [fmt_pct(calc_real_with_fixed_infl(r_p_1, 1, INFL_1Y)), 
                                                 fmt_pct(calc_real_with_fixed_infl(r_p_3, 3, INFL_3Y)), 
                                                 fmt_pct(calc_real_with_fixed_infl(r_p_5, 5, INFL_5Y))]
        })
        st.dataframe(df_rent, use_container_width=True, hide_index=True)

        # 5. Comparativa Legal y de Salida (Formato Comercial)
        if "Seguro" in vehiculo:
            st.info("🛡️ **Estrategia Blindada:** Al utilizar un Seguro Patrimonial, se prioriza la normativa de Seguros (Circular 21 SII).")
            st.markdown("<h2 style='font-weight: 900; color: #00B140; margin-top: 1.5rem;'>⚖️ Comparativa Estratégica y Legal</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #6b7280; margin-bottom: 1rem;'>Atributos legales y ventajas de salida ante rentabilidad real.</p>", unsafe_allow_html=True)
            
            l1, l2, l3 = st.columns([1.5, 2, 2])
            l1.markdown("**Atributo**")
            l2.markdown("**Portafolio Competencia**")
            l3.markdown("**Propuesta Principal**")
            st.markdown("---")
            
            rows = [
                ("📉 Orden de Retiro", "Utilidad Proporcional", "🚀 **Capital UF Primero (Tax $0)**"),
                ("🧮 Base Imponible", "Monto Bruto Nominal", "🎯 Rendimiento Real (Post-IPC)"),
                ("🕊️ Fallecimiento", "Sujeto a Posesión Efectiva", "✅ **Excluido / Liquidez 48hrs**"),
                ("🎁 Beneficio Fiscal", "Sujeto a IGC Total", "💎 **Cero Renta hasta 85 UTM**"),
                ("🏛️ Art. 108 LIR", "Postergación Básica", "⭐ **Diferimiento Máximo Legal**"),
                ("🔒 Protección", "Activo Embargable", "🛡️ **Inembargable**"),
                ("⭐ Rating Comercial", "⭐⭐ (Standard)", "⭐⭐⭐⭐⭐ (Premium)")
            ]
            for icon, comp, princ in rows:
                c1, c2, c3 = st.columns([1.5, 2, 2])
                c1.write(icon)
                c2.write(comp)
                c3.markdown(princ)
        else:
            st.info("Nota: Comparativa basada en diferencia de costos y tipos de serie.")

        # 6. Cálculos de Inteligencia Tributaria y Escenario
        beneficio_total, detalle_tax = calcular_tax_alpha(capa, reg_t, tasa_igc, vehiculo, pesos_p, df_m)
        
        # Riesgos Ponderados
        def get_wg_riesgo(pesos):
            total = 0
            for f, p in pesos.items():
                mapped_f = map_cmf_name(f, available_cmf_names)
                if mapped_f:
                    match = df_m[df_m['fondo_display']==mapped_f]
                    if not match.empty:
                        val = match.iloc[0]['nivel_riesgo']
                        clean_val = 1.0 if pd.isna(val) else val
                        total += clean_val * (p/100)
                else:
                    total += 3.0 * (p/100) # Riesgo medio por defecto (Acciones o Ext)
            return total

        riesgo_c = get_wg_riesgo(pesos_c)
        riesgo_p = get_wg_riesgo(pesos_p)

        # Proyección Final
        horizonte_map = {"Último Año": (r_c_1, r_p_1), "Últimos 3 Años": (r_c_3, r_p_3), "Últimos 5 Años": (r_c_5, r_p_5)}
        r_c_raw, r_p_raw = horizonte_map[horizonte]
        
        r_c_net, r_p_net = (r_c_raw - tac_c)/100, (r_p_raw - tac_p)/100
        path_c_proj = (capa * ((1 + r_c_net)**plazo_proj))
        path_p_proj = (capa * ((1 + r_p_net)**plazo_proj)) + (beneficio_total * plazo_proj)
        
        # Definición de filas para Reporte PDF (Consistencia institucional)
        rows_report = []
        if "Seguro" in vehiculo:
             rows_report = [
                ("⚖️ Liquidez", "Pérdida por Rescate", "Liquidez en Capital"),
                ("🧾 Impuestos", "Global Complementario", "No Renta (Circular 21)"),
                ("💰 Comisión", fmt_pct(tac_c), fmt_pct(tac_p)),
                ("📄 Beneficio", "Sin Beneficio Art. 107", "Exención Tributaria Activa")
             ]
        else:
             rows_report = [
                ("💰 Costo Anual", fmt_pct(tac_c), fmt_pct(tac_p)),
                ("📈 Rent. Neta Est.", f"{r_c_net*100:.2f}%", f"{r_p_net*100:.2f}%"),
                ("🛡️ Riesgo", f"{riesgo_c:.1f}/7", f"{riesgo_p:.1f}/7")
             ]
        
        # --- SIMULACIÓN MONTE CARLO (WEALTH 3.0) ---
        sim = MonteCarloSimulator()
        
        vol_map = {1: 0.02, 2: 0.04, 3: 0.07, 4: 0.10, 5: 0.14, 6: 0.20, 7: 0.30}
        
        def get_wg_vol(pesos):
            total = 0
            for f, p in pesos.items():
                mapped_f = map_cmf_name(f, available_cmf_names)
                if mapped_f:
                    match = df_m[df_m['fondo_display']==mapped_f]
                    if not match.empty:
                        r_level = match.iloc[0]['nivel_riesgo']
                        total += vol_map.get(r_level, 0.07) * (p/100)
                else:
                    total += 0.14 * (p/100) # Volatilidad alta por defecto para acciones/internacional
            return total
            
        vol_c = get_wg_vol(pesos_c)
        vol_p = get_wg_vol(pesos_p)
        
        # Ejecutar Simulaciones
        paths_c = sim.simulate_gbm(capa, r_c_net, vol_c, plazo_proj, n_simulations=2000)
        paths_p = sim.simulate_gbm(capa, r_p_net, vol_p, plazo_proj, n_simulations=2000)
        
        # Agregar Alpha Tributario
        paths_p = paths_p + (beneficio_total * np.arange(plazo_proj + 1).reshape(-1, 1))
        
        stats_c = sim.get_statistics(paths_c)
        stats_p = sim.get_statistics(paths_p)
        
        var_c = sim.calculate_var(capa, paths_c)
        var_p = sim.calculate_var(capa, paths_p)

        # 7. Resultados Finales
        st.markdown("<h2 style='font-weight: 900; color: #00B140; margin-top: 2rem;'>🏁 Conclusión de la Auditoría (Wealth 3.0)</h2>", unsafe_allow_html=True)
        
        # Estilo para evitar que se corten los números
        st.markdown("""
        <style>
            div[data-testid="stMetricValue"] {
                font-size: 1.5rem !important;
                white-space: normal !important;
                word-break: break-all !important;
            }
        </style>
        """, unsafe_allow_html=True)

        def get_perfil(r):
            if r <= 2.5: return "Conservador"
            if r <= 4.5: return "Moderado"
            return "Agresivo"

        r1, r2, r3, r4, r5 = st.columns(5)
        # Usamos fmt_clp directo para mayor claridad en el resumen
        r1.metric("Patrimonio (Mediana)", fmt_m_din(stats_p['p50'][-1]), delta=fmt_m_din(stats_p['p50'][-1] - stats_c['p50'][-1]),
                  help="Monto final esperado al término del plazo. El 'Delta' muestra la ganancia extra de la propuesta.")
        r2.metric("Eficiencia TAC", fmt_pct(tac_p), delta=f"{-(tac_c - tac_p):.2f}%", delta_color="normal",
                  help="Costo anual de administración de la cartera. El valor en rojo/verde indica qué tan más cara o barata es su propuesta.")
        r3.metric("Riesgo: " + get_perfil(riesgo_p), f"{riesgo_p:.1f}/7", delta=f"{vol_p*100:.1f}% Vol", delta_color="inverse",
                  help="Nivel de riesgo CMF (1-7) y volatilidad anual esperada.")
        
        # Va r: Si es negativo (ganancia en peor escenario), mostramos 0 o aclaramos. Comercialmante mostramos el 'Riesgo'
        var_disp_p = max(0, var_p)
        var_disp_c = max(0, var_c)
        r4.metric("Riesgo Máx (VaR 95%)", fmt_m_din(var_disp_p), delta=fmt_m_din(var_disp_p - var_disp_c), delta_color="inverse", 
                  help="Pérdida máxima esperada en un año con 95% de confianza (Value at Risk).")
        
        r5.metric("Alpha Tribut.", fmt_clp(beneficio_total),
                  help="Ahorro estimado en impuestos anuales gracias a la estructura legal sugerida (APV, Seguro o Art. 107).")
        
        st.markdown("---")
        st.markdown("### 📈 Simulación Estocástica: ¿Por qué usamos Monte Carlo?")
        st.write("A diferencia de una proyección lineal, este modelo Wealth 3.0 simula 2,000 futuros posibles. La **Mediana** (línea sólida) representa el camino más probable, mientras que el **Sombreado** indica dónde caerá su dinero el 90% de las veces, considerando la volatilidad ruidosa del mercado.")
        

        st.markdown("<h3 style='font-weight: 800; color: #1f2937;'>📈 Simulación Estocástica: Bandas de Confianza (Wealth 3.0)</h3>", unsafe_allow_html=True)
        import plotly.graph_objects as go
        fig_evol = go.Figure()
        
        years_idx = list(range(plazo_proj + 1))
        
        # Propuesta Principal: Mediana y Sombreado de Confianza
        fig_evol.add_trace(go.Scatter(
            x=years_idx, y=stats_p['p50'],
            line=dict(color='#00B140', width=4),
            name='Propuesta (Mediana Esperada)'
        ))
        
        # Sombreado de Riesgo (P5 a P95)
        fig_evol.add_trace(go.Scatter(
            x=years_idx + years_idx[::-1],
            y=list(stats_p['p95']) + list(stats_p['p5'])[::-1],
            fill='toself',
            fillcolor='rgba(0, 177, 64, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name='Intervalo de Confianza (90%)'
        ))
        
        # Portafolio Competencia (Mediana)
        fig_evol.add_trace(go.Scatter(
            x=years_idx, y=stats_c['p50'],
            line=dict(color='#ef4444', width=2, dash='dash'),
            name='Competencia (Mediana)'
        ))

        # Línea de Poder Adquisitivo (Inflación)
        path_infl = [capa * (1 + inflacion_avg/100)**t for t in years_idx]
        fig_evol.add_trace(go.Scatter(
            x=years_idx, y=path_infl,
            line=dict(color='#94a3b8', width=1, dash='dot'),
            name='Poder Adquisitivo (IPC)'
        ))
        
        fig_evol.update_layout(
            title="Evolución Estocástica del Patrimonio (Neto de Comisiones)",
            xaxis_title="Años",
            yaxis_title=f"Monto ({moneda})",
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_evol, use_container_width=True)
        st.caption("ℹ️ El gráfico muestra la proyección neta de costos (TAC). Si la curva de la propuesta está bajo la competencia pese a mejores fondos, indica que las comisiones son ineficientes.")

        with st.expander("Metodología: ¿Cómo se calcula este patrimonio?"):
            st.markdown(f"""
            ### Fundamentos del Análisis Patrimonial (Wealth 3.0)
            Esta proyección es una **Auditoría Técnica** basada en:
            
            1. **Pasado Real (UF):** No inventamos la inflación. El programa descarga la variación exacta de la UF de los últimos 5 años ({INFL_5Y:.1f}% acumulado) para calcular su rentabilidad real histórica.
            2. **Escenario Objetivo:** La proyección utiliza su escenario de rentabilidad esperada (**{rent_manual}%**) como base de drift en la simulación.
            3. **Simulación Monte Carlo:** Ejecutamos 2,000 trayectorias aleatorias. La línea sólida es el escenario intermedio. El área sombreada es donde caerá su patrimonio con un 90% de certeza.
            4. **Tax-Alpha:** Calculamos el ahorro impositivo específico de su régimen y vehículo (Seguro/APV), sumándolo como un flujo de caja positivo anual.
            5. **Efecto Compuesto:** Interés acumulado neto de costos (TAC) informados oficialmente por la CMF.
            """)

        # --- BOTONES DE CIERRE (CONVERSIÓN) ---
        st.markdown("---")
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            if st.button("📄 Generar Reporte Ejecutivo PDF", help="Exporta los resultados de la auditoría a un documento PDF formal para presentar al cliente.", type="primary"):
                with st.spinner("🤖 El Agente está redactando tu PDF..."):
                    try:
                        from src.reporting.pdf_engine import generate_audit_pdf
                        
                        pdf_metrics = {
                            "patrimonio": fmt_m_din(stats_p['p50'][-1]),
                            "tac": fmt_pct(tac_p),
                            "alpha": fmt_clp(beneficio_total)
                        }
                        
                        # Generación Real
                        pdf_path = generate_audit_pdf(
                            client_name="Cliente Preferencial", 
                            metrics=pdf_metrics,
                            summary_text="Auditoría de Estrategia Patrimonial",
                            fig_roi=fig_evol,
                            rows_legal=rows_report
                        )
                        
                        with open(pdf_path, "rb") as f:
                            st.download_button("💾 Descargar PDF Listo", f, file_name=os.path.basename(pdf_path))
                        st.success("✅ ¡Reporte Generado con éxito!")
                    except Exception as e:
                        st.error(f"Error al generar PDF: {e}")
        contexto_previo = get_client_context("CLIENTE_A") # Simulado por ahora, usar RUT real luego
        if contexto_previo:
            st.info(f"📜 **Memoria de Reunión Anterior:** {contexto_previo['insights']}")
        
        with st.expander("📝 Guardar Notas Estratégicas para la próxima sesión"):
            notas_input = st.text_area("¿Qué aprendimos hoy de este cliente? (Ej: Le preocupa su hija mayor, busca liquidez en 5 años...)")
            if st.button("💾 Guardar en Memoria del Agente", help="Guarda permanentemente las conclusiones en la base de conocimientos del cliente para futuras sesiones."):
                save_client_context("CLIENTE_A", notas_input)
                st.success("✅ El Agente ha recordado este contexto para la próxima auditoría.")

        # --- BOTONES DE ACCIÓN RÁPIDA (EJECUCIÓN) ---
        st.markdown("### ⚡ Acciones de Cierre")
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            if st.button("📅 Agendar Reunión de Presentación", help="Abre el gestor de calendario para proponer fechas de revisión de portafolio al cliente."):
                from intelligence.skills import AgentSkills
                # Generamos para mañana a las 10am por defecto
                fecha_sug = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                path_ics = AgentSkills.generate_calendar_invite(f"Auditoría Patrimonial: {target_lead if 'target_lead' in locals() else 'Cliente'}", fecha_sug, "10:00")
                with open(path_ics, "rb") as f:
                    st.download_button("📎 Descargar Invitación de Calendario (.ics)", f, file_name="reunion_patrimonial.ics")
                st.success(f"Invitación creada para mañana a las 10:00 AM. ¡Envíala al cliente!")
        
        
        if vehiculo == "Seguro de Vida Patrimonial":
            st.markdown("""
                <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px;'>
                    <div style='background: #e1f5fe; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #01579b;'>🛡️ <b>Inembargabilidad</b></div>
                    <div style='background: #e8f5e9; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #1b5e20;'>⏳ <b>Diferimiento Tax</b></div>
                    <div style='background: #fff3e0; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #e65100;'>🕊️ <b>Liquidez Hereditaria</b></div>
                </div>
            """, unsafe_allow_html=True)
    
    st.button("📄 Descargar Auditoría PDF para Cliente", help="Descarga el PDF detallado del análisis comparativo listo para ser enviado por correo.", use_container_width=True)

def render_infoprobidad_ui():
    st.subheader("🏛️ Minería PEP (Altos Patrimonios Gubernamentales)")
    st.markdown("Extrae los funcionarios públicos, subsecretarios y directores que declararon oficialmente más de **X millones** en Acciones y Depósitos a Plazo (InfoProbidad).")
    
    piso_patrimonio = st.number_input("Piso Mínimo de Patrimonio Líquido Declarado ($ CLP)", value=100000000, step=10000000)
    
    col_e1, col_e2 = st.columns([2, 1])
    with col_e2:
        if st.button("⚖️ Extraer Altos Patrimonios", help="Inicia la minería de datos de declaraciones de patrimonio e intereses (PEP) en InfoProbidad.", use_container_width=True):
            with st.spinner("Realizando Minería Furtiva en InfoProbidad..."):
                from src.osint.scraper_infoprobidad import minar_infoprobidad
                try:
                    num = minar_infoprobidad(piso_patrimonio)
                    st.success(f"¡Extracción Furtiva Completada! Se han cruzado y añadido {num} nuevos funcionarios de muy alto rango al CRM.")
                except Exception as e:
                    st.error(f"Error en la minería: {e}")
                    
    st.divider()
    st.subheader("🤝 Mapa de Redes de Poder (Ley de Lobby)")
    st.markdown("Busca a un prospecto o empresario para ver si registra audiencias con Ministros, Alcaldes u otras Autoridades Públicas.")
    
    lobby_name = st.text_input("Nombre o RUT del Prospecto a Investigar:", placeholder="Ej: Juan Pérez o 12.345.678-9")
    if st.button("🔍 Escanear Red de Influencia", type="primary", use_container_width=True):
        if lobby_name:
            with st.spinner(f"Rastreando reuniones y audiencias de {lobby_name}..."):
                from src.osint.scraper_lobby import LobbyScraper
                import json
                scraper = LobbyScraper()
                res = scraper.search_influencer(lobby_name)
                if res.get("exito"):
                    if res.get("audiencias_encontradas", 0) > 0:
                        st.warning(res.get("mensaje"))
                        st.json(res.get("reuniones_clave"))
                    else:
                        st.info(res.get("mensaje"))
                else:
                    st.error(res.get("mensaje"))

def render_campaign_launcher():
    st.title("🚀 Suite Comercial Asesor Senior")
    st.markdown("Automatización de contacto para clientes de Alto Patrimonio (Arquitectura Anti-Ban)")

    # --- PANEL DE ESTADÍSTICAS GLOBALES ---
    with engine.connect() as con:
        total_universo = con.execute(text("SELECT COUNT(*) FROM prospects")).scalar()
        contactables = con.execute(text("SELECT COUNT(*) FROM prospects WHERE telefono IS NOT NULL AND telefono != 'No encontrado'")).scalar()
        pendientes_mineria = con.execute(text("SELECT COUNT(*) FROM prospects WHERE telefono IS NULL OR telefono = 'No encontrado'")).scalar()
        sin_rut = con.execute(text("SELECT COUNT(*) FROM prospects WHERE rut LIKE 'SINRUT%'")).scalar()

    st.markdown("### 📊 Tablero de Control de Datos")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📈 Universo Total", f"{total_universo:,}".replace(',', '.'))
    c2.metric("✅ Total Teléfonos en BD", f"{contactables:,}".replace(',', '.'), help="Incluye a clientes actuales, leads ya contactados y personas que aún no tienen nombre validado.")
    c3.metric("🔍 En Minería (Ptes)", f"{pendientes_mineria:,}".replace(',', '.'))
    c4.metric("🆔 Sin RUT Real", f"{sin_rut:,}".replace(',', '.'))
    
    st.divider()

    # --- MODO DE OPERACIÓN ---
    st.subheader("🎯 Modo de Operación (CRM)")
    modo_crm = st.radio("Selecciona la base de datos a gestionar:", 
                        ["Prospección de Nuevos Clientes", "Fidelización de Clientes Actuales ⭐"], horizontal=True)
    is_mode_clients = "Fidelización" in modo_crm

    # Consultar la Base de Datos
    cliente_filter = 1 if is_mode_clients else 0
    with engine.connect() as con:
        df = pd.read_sql(f"SELECT * FROM prospects WHERE status_contacto != 'Contactado' AND es_cliente = {cliente_filter} AND telefono IS NOT NULL AND nombre IS NOT NULL AND telefono != 'None' AND nombre != 'None'", con=con)

    if df.empty:
        st.warning("No tienes perfiles en estado Pendiente aptos para mensajear en este modo.")
        return

    # Limpiar y unificar variables categóricas
    cols_a_estandarizar = ['ciudad', 'nombre_asesor', 'supervisor', 'tipo_negocio', 'origen_info', 'titulo_profesional']
    for col in cols_a_estandarizar:
        if col in df.columns:
            df[col] = df[col].apply(lambda c: str(c).strip().title() if pd.notna(c) and str(c).strip() else None)

    # SIDEBAR - FILTROS DINÁMICOS (Original Style)
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filtros de Segmentación")
    min_amount = st.sidebar.number_input("Inversión mínima ($)", min_value=0, value=0, step=1000000)
    
    filter_keys = ['filtro_ciudad', 'filtro_asesor', 'filtro_superv', 'filtro_negocio', 'filtro_origen', 'filtro_titulo']
    for k in filter_keys:
        if k not in st.session_state:
            st.session_state[k] = []

    def get_mask_except(skip_col=None):
        mask = pd.Series(True, index=df.index)
        if min_amount > 0:
            mask &= ((df['monto_suscrito'] >= min_amount) | (df['saldo_administrado'] >= min_amount))
        if skip_col != 'ciudad' and st.session_state['filtro_ciudad']:
            mask &= df['ciudad'].isin(st.session_state['filtro_ciudad'])
        if skip_col != 'nombre_asesor' and st.session_state['filtro_asesor']:
            mask &= df['nombre_asesor'].isin(st.session_state['filtro_asesor'])
        if skip_col != 'supervisor' and st.session_state['filtro_superv']:
            mask &= df['supervisor'].isin(st.session_state['filtro_superv'])
        if skip_col != 'tipo_negocio' and st.session_state['filtro_negocio']:
            mask &= df['tipo_negocio'].isin(st.session_state['filtro_negocio'])
        if skip_col != 'origen_info' and st.session_state['filtro_origen']:
            mask &= df['origen_info'].isin(st.session_state['filtro_origen'])
        if skip_col != 'titulo_profesional' and st.session_state['filtro_titulo']:
            mask &= df['titulo_profesional'].isin(st.session_state['filtro_titulo'])
        return mask

    def render_filter(col_name, title, state_key):
        df_allowed = df[get_mask_except(col_name)]
        valores_unicos = sorted([c for c in df_allowed[col_name].unique() if c is not None])
        st.sidebar.multiselect(title, valores_unicos, key=state_key)

    render_filter('ciudad', "📍 Ciudad / Zona", 'filtro_ciudad')
    render_filter('nombre_asesor', "👤 Asesor Original", 'filtro_asesor')
    render_filter('supervisor', "👔 Supervisor Base", 'filtro_superv')
    render_filter('tipo_negocio', "💼 Tipo de Negocio", 'filtro_negocio')
    render_filter('origen_info', "📑 Origen Información", 'filtro_origen')
    render_filter('titulo_profesional', "🎓 Profesión", 'filtro_titulo')
    
    filtered_df = df[get_mask_except(None)].copy()
    
    st.subheader(f"👥 Meta de Hoy ({len(filtered_df)} Prospectos Segmentados)")
    
    # Tabla Interactiva de Selección
    display_df = filtered_df.copy()
    def clp_format(val):
        if pd.isna(val) or val == 0: return "$ 0"
        return f"$ {int(val):,}".replace(",", ".")
    if 'monto_suscrito' in display_df.columns:
        display_df['monto_suscrito'] = display_df['monto_suscrito'].apply(clp_format)
    display_df.insert(0, "Descartar", False)

    edited_df = st.data_editor(
        display_df,
        column_config={
            "Descartar": st.column_config.CheckboxColumn("❌ Omitir", help="Márcalo si NO quieres escribirle.", default=False),
            "id": None, "rut": "RUT", "nombre": "Nombre", "telefono": "Teléfono", "ciudad": "Ciudad", "monto_suscrito": "Monto"
        },
        disabled=["rut", "nombre", "telefono", "ciudad", "monto_suscrito"], 
        hide_index=True, use_container_width=True
    )
    
    prospectos_ignorados = edited_df[edited_df["Descartar"] == True]["rut"].tolist()

    # CONSTRUCTOR DE MENSAJE (3 Bloques + Adjunto)
    st.markdown("---")
    st.markdown("### 🧩 Constructor de Oferta Multicanal")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**1. Tono del Saludo**")
        default_saludo = "Hola [NOMBRE], ¿cómo estás? Te contacto para compartirte mis comentarios mensuales." if is_mode_clients else "Buen día [NOMBRE], mi nombre es Francisco Valencia y trabajo como Asesor de Inversiones Senior."
        saludo_txt = st.text_area("Opciones de Inicio", default_saludo, height=70)
        st.markdown("<br>**3. Enviar un Documento Adjunto**", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Arrastra aquí un PDF o Imagen", type=["pdf", "png", "jpg", "jpeg"])

    with col_b:
        st.markdown("**2. Cuerpo (La Propuesta)**")
        default_cuerpo = "Adjunto encontrarás nuestro más reciente informe. Me gustaría revisar en conjunto tus inversiones mediante videollamada[TXT_PRESENCIAL]." if is_mode_clients else "Le escribo brevemente para proponerle una breve llamada para analizar expectativas de rentabilidad y aspectos tributarios clave[TXT_PRESENCIAL]."
        cuerpo_txt = st.text_area("Propuesta central", default_cuerpo, height=150)
        st.markdown("**4. Firma Institucional**")
        default_firma = "*Francisco Valencia*\n*Asesor de Inversiones Senior*\n*+569 66779662*"
        firma_txt = st.text_area("Cierre", default_firma, height=80)

    mensaje_spintax = f"{saludo_txt}\n\n{cuerpo_txt}\n\n{firma_txt}"

    # ACCIONES DE ENVÍO
    c_btn1, c_btn2 = st.columns(2)
    if c_btn1.button("🚀 INICIAR CAMPAÑA WHATSAPP", type="primary", use_container_width=True):
        df_a_enviar = filtered_df[~filtered_df["rut"].isin(prospectos_ignorados)]
        if len(df_a_enviar) == 0:
            st.error("No hay nadie seleccionado para enviar.")
            return

        st.info("Iniciando motor de WhatsApp...")
        prog_bar = st.progress(0)
        status_text = st.empty()
        
        attachment_path = None
        if uploaded_file:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                attachment_path = tmp.name

        try:
            from src.messaging.whatsapp_web import WhatsAppBot
            from src.messaging.anti_ban import AntiBanManager
            from src.messaging.spintax import format_message
            
            bot = WhatsAppBot()
            bot.start() 
            manager = AntiBanManager()
            
            for index, row in enumerate(df_a_enviar.to_dict('records')):
                first_name = str(row.get("nombre", "")).split()[0].title()
                row_copy = row.copy()
                row_copy["nombre"] = first_name
                msg_final = format_message(mensaje_spintax, row_copy)
                
                # Género y Presencialidad
                first_upper = first_name.upper()
                if first_upper.endswith('A') or first_upper in ['INES', 'ISABEL', 'CARMEN', 'BEATRIZ']:
                    msg_final = msg_final.replace("Buen día", "Buen día estimada")
                else:
                    msg_final = msg_final.replace("Buen día", "Buen día estimado")
                
                ciudad = str(row.get('ciudad', '')).upper()
                msg_final = msg_final.replace("[TXT_PRESENCIAL]", " o de forma presencial" if "COQUIMBO" in ciudad or "SERENA" in ciudad else "")

                status_text.text(f"Enviando a {first_name} ({row['telefono']})...")
                exito, error = bot.send_attachment_and_message(row['telefono'], msg_final, attachment_path=attachment_path, antiban=manager)
                if exito:
                    mark_contacted(row['id'], status='Enviado')
                
                prog_bar.progress((index + 1) / len(df_a_enviar))
                if index < len(df_a_enviar) - 1:
                    manager.random_wait(index)
            
            bot.close()
            st.balloons()
            st.success("Campaña completada.")
        except Exception as e:
            st.error(f"Error en el robot: {e}")
        finally:
            if attachment_path and os.path.exists(attachment_path): os.remove(attachment_path)

    if c_btn2.button("🧪 Ejecutar Simulacro (A/B Test)", use_container_width=True):
        st.info("Modo Simulacro: Previsualización de los 3 primeros mensajes")
        from src.messaging.spintax import format_message
        df_test = filtered_df[~filtered_df["rut"].isin(prospectos_ignorados)].head(3)
        for lead in df_test.to_dict('records'):
            st.write(f"📝 **{lead['nombre']}**: {format_message(mensaje_spintax, lead)}")

def render_crm_kanban():
    from src.web.components.kanban import render_kanban
    render_kanban()

def render_unified_vault():
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 15px; margin-bottom: 25px; color: white;'>
            <h1 style='color: white; margin: 0; font-size: 2.5em; font-weight: 900;'>🏰 Bóveda de Ingesta Unificada</h1>
            <p style='color: #94a3b8; margin: 10px 0 0 0; font-size: 1.2em;'>Centro de Extracción, Minería y Enriquecimiento de Leads de Alto Patrimonio</p>
        </div>
    """, unsafe_allow_html=True)

    # Estadísticas de la Bóveda
    with engine.connect() as con:
        total = con.execute(text("SELECT COUNT(*) FROM prospects")).scalar()
        today = con.execute(text("SELECT COUNT(*) FROM prospects WHERE fecha_hallazgo >= date('now', '-1 day')")).scalar()
        with_tel = con.execute(text("SELECT COUNT(*) FROM prospects WHERE telefono IS NOT NULL AND telefono != 'No encontrado'")).scalar()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Patrimonio de Datos", f"{total:,}".replace(',', '.'), help="Total de registros en la base de datos.")
    c2.metric("🆕 Captura (24h)", f"{today:,}".replace(',', '.'), delta=f"{today}", help="Nuevos leads capturados hoy.")
    c3.metric("📱 Leads Contactables", f"{with_tel:,}".replace(',', '.'), help="Leads con teléfono validado.")

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🔍 Radar OSINT (Diario Oficial)", 
        "🏛️ Minería PEP (InfoProbidad)", 
        "🎓 Extracción Académica (CAMV)",
        "✨ Enriquecimiento (TransUnion/Rutificador)",
        "📈 Extracción Mercado (CMF)",
        "🧠 Sabiduría (YouTube RAG)",
        "⚖️ Inteligencia Jurídica (BCN)"
    ])

    with tab1:
        st.subheader("🔍 Radar de Oportunidades (OSINT)")
        st.write("Monitoreo automatizado del Diario Oficial para detectar eventos de liquidez.")
        
        col_o1, col_o2 = st.columns([2, 1])
        with col_o1:
            dias = st.slider("Días hacia atrás para escanear", 1, 60, 7)
            region = st.text_input("Filtrar por Región (Opcional)", placeholder="Ej: METROPOLITANA")
        with col_o2:
            st.info("💡 Este scraper busca: Constituciones, Posesiones Efectivas, Expropiaciones y más.")
            if st.button("🚀 Iniciar Escaneo OSINT", help="Busca en el Diario Oficial constituciones de sociedades, posesiones efectivas y eventos de liquidez.", type="primary", use_container_width=True):
                from src.osint.scraper_do import run_scraper
                with st.spinner("Escaneando el Diario Oficial..."):
                    res = run_scraper(region_target=region if region else None, days_back=dias)
                    st.success(f"Escaneo finalizado: {res['nuevos']} nuevos leads encontrados.")
                    
        st.divider()
        st.subheader("💼 Radar de Liquidez Institucional (Mercado Público)")
        st.markdown("Detecta si una empresa acaba de adjudicarse grandes contratos con el Estado (Flujo de Caja Fresco).")
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            rut_empresa = st.text_input("RUT de la Empresa (Proyectar Flujo):", placeholder="Ej: 76.123.456-7")
        with col_m2:
            st.info("💡 Requiere configurar el Ticket de API en el código fuente.")
            if st.button("💰 Detectar Órdenes de Compra", type="primary", use_container_width=True):
                if rut_empresa:
                    with st.spinner(f"Consultando la red de Mercado Público para {rut_empresa}..."):
                        from src.osint.scraper_mercadopublico import MercadoPublicoScraper
                        scraper = MercadoPublicoScraper()
                        res = scraper.fetch_liquidity_events(rut_empresa)
                        if res.get("exito"):
                            st.success(res.get("mensaje"))
                            if res.get("eventos"):
                                st.dataframe(res.get("eventos"))
                        else:
                            st.error(res.get("mensaje"))

    with tab2:
        render_infoprobidad_ui()

    with tab3:
        st.subheader("🎓 Ingesta de Conocimiento Académico")
        st.write("Extrae manuales y leyes del Comité de Acreditación (CAMV) para el cerebro del Agente.")
        if st.button("📚 Sincronizar Biblioteca Académica", help="Descarga y procesa leyes, circulares y normativas de la CMF/CAMV al cerebro del agente (RAG).", use_container_width=True):
            from src.osint.scraper_camv import CAMVScraper
            with st.spinner("Mapeando recursos de CAMV..."):
                scraper = CAMVScraper()
                num = scraper.extract_index()
                st.success(f"Se han mapeado {num} recursos clave. Listos para ser procesados por el motor RAG.")

    with tab4:
        st.subheader("✨ Enriquecimiento de Identidad (Búsqueda Furtiva)")
        st.write("Convierte un Nombre en un RUT válido, y luego cruza ese RUT contra bases comerciales para obtener teléfonos.")
        
        c_e1, c_e2 = st.columns(2)
        with c_e1:
            st.markdown("#### 1. Cazador de RUTs")
            nombre_prospecto = st.text_input("Nombre Completo a investigar:", placeholder="Ej: Juan Perez Cotapos")
            if st.button("🆔 Ejecutar Rutificador", help="Busca el RUT asociado a los nombres extraídos para enriquecer el perfil.", use_container_width=True, type="primary"):
                if nombre_prospecto:
                    with st.spinner("Triangulando identidad en registros OSINT..."):
                        from src.osint.scraper_rutificador import RutificadorScraper
                        scraper_rut = RutificadorScraper()
                        res_rut = scraper_rut.buscar_rut_por_nombre(nombre_prospecto)
                        if res_rut.get("exito"):
                            st.success(res_rut.get("mensaje"))
                            st.metric("RUT Encontrado", res_rut.get("rut"))
                        else:
                            st.error(res_rut.get("mensaje"))
                            
        with c_e2:
            st.markdown("#### 2. Cosechador de Contactos")
            rut_prospecto = st.text_input("RUT a enriquecer (Buró Comercial):", placeholder="Ej: 12345678-9")
            if st.button("📞 Buscar en Buró Comercial", help="Consulta bases de datos enriquecidas para encontrar teléfonos y correos.", use_container_width=True, type="primary"):
                if rut_prospecto:
                    with st.spinner("Cruzando RUT contra burós privados..."):
                        from src.osint.scraper_transunion import TransUnionScraper
                        scraper_tu = TransUnionScraper()
                        res_tu = scraper_tu.buscar_datos_contacto(rut_prospecto)
                        if res_tu.get("exito"):
                            st.success(res_tu.get("mensaje"))
                            st.json({"Teléfonos Detectados": res_tu.get("telefonos"), "Correos": res_tu.get("correos")})
                        else:
                            st.error(res_tu.get("mensaje"))
    with tab5:
        st.subheader("📈 Ingesta de Mercado (CMF)")
        st.write("Sincroniza y procesa datos públicos de la Comisión para el Mercado Financiero.")
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            if st.button("📊 Ingestar Tendencias de Mercado", help="Lee los consolidados de la industria (AUM, partícipes, retornos) y los estructura en SQL. Lo usa el módulo de Inteligencia de Mercado.", use_container_width=True):
                with st.spinner("Procesando histórico de tendencias..."):
                    import subprocess
                    result = subprocess.run(["python", "src/osint/ingestor_tendencias.py"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("Tendencias procesadas correctamente.")
                    else:
                        st.error(f"Error: {result.stderr}")
                        
            if st.button("💰 Ingestar Rentabilidad Histórica", help="Procesa las series de tiempo del rendimiento de cada fondo. Lo usa el Auditor de Portafolio para criticar rentabilidades.", use_container_width=True):
                with st.spinner("Procesando rentabilidad..."):
                    import subprocess
                    result = subprocess.run(["python", "src/osint/ingestor_rentabilidad.py"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("Rentabilidad procesada correctamente.")
                    else:
                        st.error(f"Error: {result.stderr}")
                        
        with col_c2:
            st.markdown("### Fondos Mutuos (AUM y Costos)")
            from src.osint.scraper_cmf_fondos import CMFWeeklyIngestor
            ingestor_fm = CMFWeeklyIngestor()
            ultima_fecha = ingestor_fm.obtener_ultima_actualizacion()
            
            st.info(f"📅 **Última Actualización Base de Datos:** {ultima_fecha}")
            
            if st.button("🔄 Ejecutar Sincronización Semanal (ZIP CMF)", help="Descarga el archivo masivo de la CMF, extrae los TAC y AUM, y cruza los datos con nuestra BD local.", use_container_width=True):
                with st.spinner("Descargando y procesando paquetes semanales de la CMF... esto puede tardar."):
                    res_fm = ingestor_fm.run_weekly_ingestion()
                    if res_fm.get("exito"):
                        st.success(res_fm.get("mensaje"))
                        st.rerun()
                    else:
                        st.error(res_fm.get("mensaje"))

    with tab6:
        st.subheader("🧠 Bóveda de Sabiduría (YouTube)")
        st.write("Descarga subtítulos de YouTube y vectorízalos en el Cerebro (RAG) para usarlos como lecciones de ventas y psicología.")
        youtube_url = st.text_input("🔗 URL o ID del Video de YouTube:", placeholder="Ej: https://youtu.be/tDD_icF3flc")
        youtube_title = st.text_input("📝 Título/Temática (Para el índice del RAG):", placeholder="Ej: 35 Lecciones para vender cualquier cosa")
        
        if st.button("📥 Descargar e Inyectar al Cerebro", type="primary"):
            if youtube_url and youtube_title:
                with st.spinner("Descargando transcripción y vectorizando en ChromaDB... esto puede tardar un minuto."):
                    from src.intelligence.youtube_extractor import YouTubeWisdomExtractor
                    extractor = YouTubeWisdomExtractor()
                    success, msg = extractor.ingest_video_to_rag(youtube_url, youtube_title)
                    if success:
                        st.success(msg)
                    else:
                        st.error(f"Error: {msg}")
            else:
                st.warning("Debes ingresar la URL y un Título.")

    with tab7:
        st.subheader("⚖️ Bóveda Tributaria Automática (BCN)")
        st.write("Conexión directa a la API Ley Chile (Biblioteca del Congreso Nacional) para descargar las leyes fiscales y normativas actualizadas en tiempo real.")
        
        # Mostrar lo que está en memoria actualmente
        import os
        vault_path = "data/knowledge_base/tributaria/"
        if os.path.exists(vault_path):
            archivos_memoria = [f for f in os.listdir(vault_path) if f.endswith('.txt') or f.endswith('.pdf')]
        else:
            archivos_memoria = []
            
        st.markdown("### 📚 Leyes Actualmente en la Memoria de la IA")
        if archivos_memoria:
            for archivo in archivos_memoria:
                peso_kb = os.path.getsize(os.path.join(vault_path, archivo)) / 1024
                st.success(f"✅ **{archivo.replace('.txt', '').replace('_', ' ')}** ({peso_kb:.1f} KB indexados)")
        else:
            st.warning("⚠️ El cerebro está vacío. Necesitas sincronizar la biblioteca.")
        
        st.info("💡 **Nota:** Actualmente el robot está configurado para extraer el DL 824 (Renta) y Ley 21.133. Podemos agregar más Códigos u Oficios según lo requieras.")
        
        if st.button("📥 Sincronizar Biblioteca del Congreso", type="primary", use_container_width=True):
            with st.spinner("Conectando con Ley Chile API (BCN) y descargando XMLs legales..."):
                from src.osint.scraper_bcn import BCNScraper
                bot = BCNScraper()
                exitos, total = bot.sync_tributary_library()
                if exitos > 0:
                    st.success(f"¡Operación Exitosa! Se han descargado y estructurado {exitos} de {total} leyes tributarias clave. El Cerebro RAG ahora leerá de estos textos actualizados.")
                else:
                    st.error("Ocurrió un error al intentar sincronizar con la BCN.")

def render_industry_insights():
    from src.intelligence.market_analyst import render_market_intelligence
    render_market_intelligence()



def render_omni_advisor_ui():
    import os
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white;'>
            <h2 style='margin: 0; color: white;'>🏛️ Asesor Patrimonial Senior (OmniAdvisor)</h2>
            <p style='color: #bfdbfe; margin: 0;'>Respuestas avanzadas con Inteligencia Artificial, Bases Legales Internas (RAG) y Memoria a Largo Plazo por Cliente.</p>
        </div>
    """, unsafe_allow_html=True)
    
    from src.intelligence.omni_advisor import OmniAdvisorAgent
    
    # 1. Selector de Cliente para Memoria
    client_id = st.text_input("Ingresa el RUT o Nombre del Cliente para cargar su memoria (ej. '12345678-9'):", value="cliente_default")
    
    if st.button("🔄 Cargar / Reiniciar Memoria"):
        st.session_state.omni_agent = OmniAdvisorAgent(client_id=client_id)
        st.session_state.omni_messages = []
        st.success(f"Memoria cargada para el cliente: {client_id}")
        
    if "omni_agent" not in st.session_state:
        with st.spinner("Inicializando agente autónomo..."):
            st.session_state.omni_agent = OmniAdvisorAgent(client_id=client_id)
            
    if "omni_messages" not in st.session_state:
        st.session_state.omni_messages = []

    # 2. Controles de Supervisión y Limpieza
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("🚀 Ejecutar Rutina de Supervisión Autónoma", help="Busca cartolas pendientes en el sistema, extrae sus datos y genera reportes de estrategia guardándolos automáticamente."):
            with st.spinner("Despertando al Supervisor..."):
                from src.intelligence.supervisor import AgentSupervisor
                sup = AgentSupervisor()
                logs = sup.run_autonomous_cycle()
                for log in logs:
                    st.info(log)
                st.success("Rutina finalizada.")
    with col_btn2:
        if st.button("🗑️ Limpiar Pantalla"):
            st.session_state.omni_messages = []
            st.rerun()

    st.markdown("---")
    # 3. Interfaz de Chat
    for message in st.session_state.omni_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Consulta normativa CMF, leyes, LIR, APV, Herencia o estrategias para el cliente..."):
        st.session_state.omni_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Pensando, revisando memoria y bases de datos..."):
                response = st.session_state.omni_agent.ask(prompt)
                st.markdown(response)
        
        st.session_state.omni_messages.append({"role": "assistant", "content": response})

def render_flujograma():
    st.title("🧠 Diseñador de Flujos (Playbook)")
    st.write("Configuración de árboles de decisión y guiones de venta dinámicos.")
    # Implementación futura...

def render_blue_ocean_ui():
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 30px; border-radius: 15px; margin-bottom: 25px; color: white;'>
            <h1 style='color: white; margin: 0; font-size: 2.5em; font-weight: 900;'>🌊 Innovación & Océanos Azules</h1>
            <p style='color: #94a3b8; margin: 10px 0 0 0; font-size: 1.2em;'>Arquitectura de nuevos modelos de negocio y generación de ingresos no tradicionales</p>
        </div>
    """, unsafe_allow_html=True)

    from src.intelligence.blue_ocean_strategist import BlueOceanStrategist
    
    if "blue_ocean" not in st.session_state:
        st.session_state.blue_ocean = BlueOceanStrategist()
    
    strategist = st.session_state.blue_ocean
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🛠️ Configurar Estrategia")
        focus = st.selectbox("Área de Enfoque", strategist.get_predefined_strategies() + ["Personalizado..."])
        
        custom_focus = ""
        if focus == "Personalizado...":
            custom_focus = st.text_input("Escribe el nicho o idea base:")
            
        if st.button("🪄 Generar Reporte de Negocio", help="Crea un resumen de inteligencia corporativa sobre la empresa investigada para estructurar tu acercamiento.", type="primary", use_container_width=True):
            with st.spinner("El Arquitecto está diseñando el Océano Azul..."):
                target = custom_focus if custom_focus else focus
                st.session_state.blue_ocean_report = strategist.generate_business_brief(target)

    with col2:
        if "blue_ocean_report" in st.session_state:
            st.markdown(st.session_state.blue_ocean_report)
            
            st.divider()
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                if st.button("💾 Guardar en Playbooks", help="Guarda el reporte generado en el repositorio de Playbooks de Ventas.", use_container_width=True):
                    st.success("Estrategia guardada en la base de conocimientos.")
            with c_a2:
                if st.button("📅 Agendar Sesión de Diseño", help="Programa una reunión interna para discutir estrategias de acercamiento corporativo.", use_container_width=True):
                    st.info("Sesión agendada para profundizar en este modelo.")
        else:
            st.markdown("""
                <div style='background: #f1f5f9; padding: 40px; border-radius: 15px; text-align: center; border: 2px dashed #cbd5e1; color: #64748b;'>
                    <h2 style='margin: 0;'>🚀 Listo para Innovar</h2>
                    <p>Selecciona un área de enfoque a la izquierda para generar una nueva tesis de ingresos.</p>
                </div>
            """, unsafe_allow_html=True)

def main():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');
        
        /* Aplicar a elementos de texto pero evitar romper los íconos de Streamlit */
        html, body, p, h1, h2, h3, h4, h5, h6, label, [class*="css"] {
            font-family: 'Montserrat', sans-serif !important;
        }
        
        /* Proteger los íconos de Material Symbols que usa Streamlit internamente */
        .material-symbols-rounded, .stIcon, [class*="icon"], i {
            font-family: 'Material Symbols Rounded', 'Material Icons' !important;
        }
        
        .section-header {
            color: #1e293b;
            font-weight: 800;
            font-size: 1.2em;
            margin-top: 15px;
            margin-bottom: 5px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Mostrar Logo Corporativo Oficial FV en Vector Nativo Puro SVG
    svg_sidebar_path = os.path.join(root_path, "assets", "brand", "fv_logo_vector_pure.svg")
    if os.path.exists(svg_sidebar_path):
        st.sidebar.image(svg_sidebar_path, use_container_width=True)
    elif os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, use_container_width=True)
    else:
        st.sidebar.title("💎 FV WealthTech")
        
    st.sidebar.markdown("""
        <div style='background: radial-gradient(circle at top right, #2a2a2a 0%, #000000 100%); padding: 10px; border-radius: 8px; border: 1px solid #D4AF37; margin-bottom: 20px;'>
            <p style='color: #D4AF37; font-weight: 600; margin: 0; font-size: 0.8em; text-transform: uppercase;'>Sistema de Control Senior</p>
            <p style='color: #FFFFFF; font-size: 1.1em; font-weight: 500; margin: 0;'>Panel de Comando</p>
        </div>
    """, unsafe_allow_html=True)

    if "main_nav" not in st.session_state:
        st.session_state.main_nav = "🏠 Inicio"

    nav = st.sidebar.radio("Metodología de Trabajo", [
        "🏠 Inicio",
        "👤 1. Gestión de Clientes",
        "📊 2. Análisis de Inversiones",
        "💼 3. Gestión Comercial",
        "📥 4. Ingesta de Datos"
    ], key="main_nav")
    
    st.sidebar.markdown("---")

    def set_nav(main_page, sub_key=None, sub_page=None):
        st.session_state.main_nav = main_page
        if sub_key and sub_page:
            st.session_state[sub_key] = sub_page

    # ----------------------------------------------------
    # 🏠 0. INICIO - LANDING PRINCIPAL CON TODOS LOS HUBS
    # ----------------------------------------------------
    if nav == "🏠 Inicio":
        import base64
        altus_logo_b64 = ""
        altus_logo_path = os.path.join(root_path, "assets", "brand", "altus_ai_logo_dark.png")
        if not os.path.exists(altus_logo_path):
            altus_logo_path = os.path.join(root_path, "assets", "Logo_ALTUS AI_Principal_Fondo oscuro.png")
        if os.path.exists(altus_logo_path):
            with open(altus_logo_path, "rb") as f_alt:
                altus_logo_b64 = f"data:image/png;base64,{base64.b64encode(f_alt.read()).decode('utf-8')}"

        img_banner = f'<img src="{altus_logo_b64}" height="75" style="margin-bottom: 15px;"/>' if altus_logo_b64 else ''

        st.markdown(f"""
        <div style='background: radial-gradient(circle at top right, #3a3a3a 0%, #050505 80%); padding: 45px; border-radius: 15px; margin-bottom: 25px; color: white; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.4); border: 1px solid #D4AF37;'>
            {img_banner}
            <h1 style='color: white; margin: 0; font-size: 3em; font-weight: 700;'>Bienvenido a <span style="color: #D4AF37;">Altus AI</span></h1>
            <p style='color: #ffffff; margin: 10px 0 0 0; font-size: 1.3em;'>Tu Motor Cuantitativo Patrimonial & Asesoría Integrada 360°</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🛠️ Flujo de Trabajo Metodológico")
        st.markdown("<p style='color: #6b7280; margin-bottom: 20px;'>Sigue este camino para una gestión patrimonial óptima:</p>", unsafe_allow_html=True)
        
        # SEC 1: CLIENTES
        st.markdown("#### 👥 1. Punto de Partida & Gestión de Clientes")
        st.button("🎯 Seleccionar o Crear Cliente (Ficha 360°, Herederos, Propiedades & KYC)", on_click=set_nav, args=("👤 1. Gestión de Clientes",), use_container_width=True)

        st.markdown("---")

        # SEC 2: ANÁLISIS DE INVERSIONES (TODAS LAS 7 HERRAMIENTAS VISIBLES EN INICIO)
        st.markdown("#### 📊 2. Hub de Análisis de Inversiones")
        a1, a2 = st.columns(2)
        a1.button("📉 Auditor de Portafolio", on_click=set_nav, args=("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Auditor de Portafolio"), use_container_width=True)
        a2.button("📈 Análisis Técnico y Fundamental", on_click=set_nav, args=("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Análisis Técnico y Fundamental"), use_container_width=True)

        a3, a4 = st.columns(2)
        a3.button("🏢 Valuación de Portafolios (Real Estate)", on_click=set_nav, args=("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Valuación de Portafolios"), use_container_width=True)
        a4.button("🧠 Asesor Patrimonial Senior (Omni AI)", on_click=set_nav, args=("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Asesor Patrimonial Senior (Omni)"), use_container_width=True)

        a5, a6 = st.columns(2)
        a5.button("📊 Estrategia & Cartolas (Parsing Bancario)", on_click=set_nav, args=("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Estrategia & Cartolas"), use_container_width=True)
        a6.button("🌍 Analista Macro (Consenso & Playbooks)", on_click=set_nav, args=("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Analista Macro (Consenso & Playbooks)"), use_container_width=True)

        a7, _ = st.columns([0.5, 0.5])
        a7.button("🧮 Simuladores Cuantitativos (APV Inteligente, Reliquidación & Créditos)", on_click=set_nav, args=("📊 2. Análisis de Inversiones", "sub_nav_analisis", "Simuladores Cuantitativos"), use_container_width=True)

        st.markdown("---")

        # SEC 3: GESTIÓN COMERCIAL (TODAS LAS 5 HERRAMIENTAS VISIBLES EN INICIO)
        st.markdown("#### 💼 3. Gestión Comercial & Marketing Pro")
        m1, m2 = st.columns(2)
        m1.button("🚀 Motor de Campañas & Outreach", on_click=set_nav, args=("💼 3. Gestión Comercial", "sub_nav_comercial", "🚀 Motor de Campañas"), use_container_width=True)
        m2.button("📊 Embudo CRM (Kanban)", on_click=set_nav, args=("💼 3. Gestión Comercial", "sub_nav_comercial", "📊 Embudo CRM (Kanban)"), use_container_width=True)

        m3, m4 = st.columns(2)
        m3.button("🌊 Innovación & Océanos Azules", on_click=set_nav, args=("💼 3. Gestión Comercial", "sub_nav_comercial", "🌊 Innovación & Océanos Azules"), use_container_width=True)
        m4.button("🧠 Diseñador de Flujos (Playbooks)", on_click=set_nav, args=("💼 3. Gestión Comercial", "sub_nav_comercial", "🧠 Diseñador de Flujos (Playbook)"), use_container_width=True)

        m5, _ = st.columns([0.5, 0.5])
        m5.button("📱 Generador de Infografías RRSS (4K)", on_click=set_nav, args=("💼 3. Gestión Comercial", "sub_nav_comercial", "📱 Generador de Infografías RRSS"), use_container_width=True)

        st.markdown("---")

        # SEC 4: INGESTA
        st.markdown("#### 📥 4. Central de Operaciones & Ingesta")
        st.button("🏰 Bóveda de Ingesta Unificada (Scrapers, Cartolas & Data)", on_click=set_nav, args=("📥 4. Ingesta de Datos",), use_container_width=True)

        st.markdown("---")



    # ----------------------------------------------------
    # 👤 1. GESTIÓN DE CLIENTES
    # ----------------------------------------------------
    elif nav == "👤 1. Gestión de Clientes":
        from src.web.client_management_ui import render_client_management_ui
        render_client_management_ui()

    # ----------------------------------------------------
    # 📊 2. ANÁLISIS DE INVERSIONES (HUB CON TODAS LAS HERRAMIENTAS)
    # ----------------------------------------------------
    elif nav == "📊 2. Análisis de Inversiones":
        if "sub_nav_analisis" not in st.session_state:
            st.session_state.sub_nav_analisis = "🏠 Landing de Análisis"

        sub_nav = st.session_state.sub_nav_analisis

        def set_subanalisis(val):
            st.session_state.sub_nav_analisis = val

        # Menú Rápido de 4 Pilares Funcionales
        st.markdown("##### 📌 Menú de Pilares Estratégicos de Análisis:")
        b1, b2, b3, b4, b5 = st.columns(5)
        
        if b1.button("🏠 Inicio Hub", use_container_width=True): set_subanalisis("🏠 Landing de Análisis")
        if b2.button("📁 1. Auditoría & Cartolas", use_container_width=True): set_subanalisis("Pilar 1: Auditoría de Portafolios")
        if b3.button("🌍 2. Macro & Mercado", use_container_width=True): set_subanalisis("Pilar 2: Inteligencia Macro y Mercado")
        if b4.button("🧮 3. Modelación Cuantitativa", use_container_width=True): set_subanalisis("Pilar 3: Modelación Cuantitativa")
        if b5.button("🧠 4. Copilot Omni AI", use_container_width=True): set_subanalisis("Pilar 4: Copilot Patrimonial Omni AI")

        st.markdown("---")

        if sub_nav == "🏠 Landing de Análisis":
            st.markdown("""
                <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 15px; margin-bottom: 25px; color: white;'>
                    <h1 style='color: white; margin: 0; font-size: 2.2em; font-weight: 900;'>🎯 Hub de Análisis de Inversiones</h1>
                    <p style='color: #94a3b8; margin: 10px 0 0 0; font-size: 1.1em;'>Suite integral reorganizada en 4 Pilares Estratégicos de Wealth Management.</p>
                </div>
            """, unsafe_allow_html=True)
            
            if "current_client_name" in st.session_state:
                st.success(f"📌 Analizando al cliente activo: **{st.session_state.current_client_name}**")
            else:
                st.info("ℹ️ Puedes seleccionar un cliente activo en 'Gestión de Clientes' para enriquecer los diagnósticos.")
                
            st.markdown("#### 🏛️ Selecciona el Pilar de Análisis a Ejecutar:")
            
            p1_col, p2_col = st.columns(2)
            with p1_col:
                st.markdown("""
                    <div style='background: #1e293b; padding: 18px; border-radius: 12px; border-left: 5px solid #0284c7; margin-bottom: 12px;'>
                        <h3 style='color: #38bdf8; margin: 0;'>📁 Pilar 1: Auditoría de Portafolios & Cartolas</h3>
                        <p style='color: #cbd5e1; font-size: 0.95em; margin: 8px 0 0 0;'>Ingesta inteligente de cartolas bancarias (OCR/AI) + Diagnóstico de sobrecostos, comisiones y asset allocation.</p>
                    </div>
                """, unsafe_allow_html=True)
                st.button("Ingresar a Pilar 1 (Cartolas & Auditoría)", use_container_width=True, on_click=set_subanalisis, args=("Pilar 1: Auditoría de Portafolios",))

            with p2_col:
                st.markdown("""
                    <div style='background: #1e293b; padding: 18px; border-radius: 12px; border-left: 5px solid #10b981; margin-bottom: 12px;'>
                        <h3 style='color: #34d399; margin: 0;'>🌍 Pilar 2: Inteligencia Macro & Mercado</h3>
                        <p style='color: #cbd5e1; font-size: 0.95em; margin: 8px 0 0 0;'>Análisis Macro (Consenso BCCh, Fed, Playbooks) + Diagnóstico Técnico y Fundamental de activos financieros.</p>
                    </div>
                """, unsafe_allow_html=True)
                st.button("Ingresar a Pilar 2 (Macro & Mercado)", use_container_width=True, on_click=set_subanalisis, args=("Pilar 2: Inteligencia Macro y Mercado",))

            st.markdown("<br>", unsafe_allow_html=True)
            p3_col, p4_col = st.columns(2)
            with p3_col:
                st.markdown("""
                    <div style='background: #1e293b; padding: 18px; border-radius: 12px; border-left: 5px solid #f59e0b; margin-bottom: 12px;'>
                        <h3 style='color: #fbbf24; margin: 0;'>🧮 Pilar 3: Modelación Cuantitativa & Bienes Raíces</h3>
                        <p style='color: #cbd5e1; font-size: 0.95em; margin: 8px 0 0 0;'>Valuación Real Estate + Simuladores Cuantitativos (APV Régimen A/B, Reliquidación Tributaria, Créditos).</p>
                    </div>
                """, unsafe_allow_html=True)
                st.button("Ingresar a Pilar 3 (Simuladores & Real Estate)", use_container_width=True, on_click=set_subanalisis, args=("Pilar 3: Modelación Cuantitativa",))

            with p4_col:
                st.markdown("""
                    <div style='background: #1e293b; padding: 18px; border-radius: 12px; border-left: 5px solid #8b5cf6; margin-bottom: 12px;'>
                        <h3 style='color: #c084fc; margin: 0;'>🧠 Pilar 4: Copilot Patrimonial Senior (Omni AI)</h3>
                        <p style='color: #cbd5e1; font-size: 0.95em; margin: 8px 0 0 0;'>Co-piloto cognitivo senior para síntesis patrimonial integral 360° y preparación de comité de inversión.</p>
                    </div>
                """, unsafe_allow_html=True)
                st.button("Ingresar a Pilar 4 (Copilot Omni AI)", use_container_width=True, on_click=set_subanalisis, args=("Pilar 4: Copilot Patrimonial Omni AI",))

        # PILAR 1: AUDITORÍA Y CARTOLAS
        elif sub_nav in ["Pilar 1: Auditoría de Portafolios", "Estrategia & Cartolas", "Auditor de Portafolio"]:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #0284c7 0%, #0f172a 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white;'>
                    <h2 style='color: white; margin: 0;'>📁 Pilar 1: Auditoría de Portafolios & Cartolas Bancarias</h2>
                    <p style='color: #e0f2fe; margin: 5px 0 0 0;'>Ingesta automatizada de cartolas + Evaluación de riesgos, comisiones y asignación estratégica.</p>
                </div>
            """, unsafe_allow_html=True)
            
            tab_p1_cartolas, tab_p1_auditor = st.tabs(["📊 1.1 Ingesta & Parsing de Cartolas OCR/AI", "🔍 1.2 Diagnóstico & Auditoría de Portafolio"])
            
            with tab_p1_cartolas:
                from src.web.cartolas_ui import render_cartolas_ui
                render_cartolas_ui()
                
            with tab_p1_auditor:
                from src.web.app import render_portfolio_auditor
                render_portfolio_auditor()

        # PILAR 2: INTELIGENCIA MACRO Y MERCADO
        elif sub_nav in ["Pilar 2: Inteligencia Macro y Mercado", "Analista Macro (Consenso & Playbooks)", "Análisis Técnico y Fundamental"]:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #059669 0%, #0f172a 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white;'>
                    <h2 style='color: white; margin: 0;'>🌍 Pilar 2: Inteligencia Macro & Análisis de Mercado</h2>
                    <p style='color: #d1fae5; margin: 5px 0 0 0;'>Visión macroeconómica institucional + Análisis técnico/fundamental de instrumentos financieros.</p>
                </div>
            """, unsafe_allow_html=True)
            
            tab_p2_macro, tab_p2_tecnico = st.tabs(["🌍 2.1 Consenso Macro, Banco Central & Playbooks", "📈 2.2 Análisis Técnico y Fundamental de Activos"])
            
            with tab_p2_macro:
                from src.web.macro_chat_ui import render_macro_chat_ui
                render_macro_chat_ui()
                
            with tab_p2_tecnico:
                from src.web.analysis_hub_ui import render_analysis_hub
                render_analysis_hub()

        # PILAR 3: MODELACIÓN CUANTITATIVA Y REAL ESTATE
        elif sub_nav in ["Pilar 3: Modelación Cuantitativa", "Valuación de Portafolios", "Simuladores Cuantitativos"]:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #d97706 0%, #0f172a 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white;'>
                    <h2 style='color: white; margin: 0;'>🧮 Pilar 3: Modelación Cuantitativa & Bienes Raíces</h2>
                    <p style='color: #fef3c7; margin: 5px 0 0 0;'>Modelos matemáticos para optimización inmobiliaria, tributaria y previsional.</p>
                </div>
            """, unsafe_allow_html=True)
            
            tab_p3_re, tab_p3_apv, tab_p3_reliq, tab_p3_credito = st.tabs([
                "🏢 3.1 Valuación Real Estate & Cap Rates",
                "🏛️ 3.2 APV Inteligente (Régimen A/B)",
                "⚖️ 3.3 Reliquidación Tributaria (Global Comp.)",
                "💰 3.4 Comparador Crédito vs Inversión"
            ])
            
            with tab_p3_re:
                from src.web.valuation_ui import render_valuation_ui
                render_valuation_ui()
                
            with tab_p3_apv:
                from src.web.simulators_ui import render_apv_simulator
                render_apv_simulator(38000)
                
            with tab_p3_reliq:
                from src.web.simulators_ui import render_reliquidacion_simulator
                render_reliquidacion_simulator(66000, 38000)
                
            with tab_p3_credito:
                from src.web.simulators_ui import render_credito_vs_inversion_simulator
                render_credito_vs_inversion_simulator()

        # PILAR 4: COPILOT OMNI AI
        elif sub_nav in ["Pilar 4: Copilot Patrimonial Omni AI", "Asesor Patrimonial Senior (Omni)"]:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #7c3aed 0%, #0f172a 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white;'>
                    <h2 style='color: white; margin: 0;'>🧠 Pilar 4: Copilot Patrimonial Senior (Omni AI)</h2>
                    <p style='color: #ede9fe; margin: 5px 0 0 0;'>Co-piloto cognitivo ejecutivo para dictamen patrimonial integral 360°.</p>
                </div>
            """, unsafe_allow_html=True)
            from src.web.app import render_omni_advisor_ui
            render_omni_advisor_ui()

    # ----------------------------------------------------
    # 💼 3. GESTIÓN COMERCIAL (HUB CON TODOS LOS MÓDULOS)
    # ----------------------------------------------------
    elif nav == "💼 3. Gestión Comercial":
        if "sub_nav_comercial" not in st.session_state:
            st.session_state.sub_nav_comercial = "🚀 Motor de Campañas"

        sub_nav_com = st.session_state.sub_nav_comercial

        # Barra superior de navegación interna horizontal en la pantalla principal
        st.markdown("##### 📌 Menú Rápido Comercial:")
        c1, c2, c3, c4, c5, c6 = st.columns(6)

        def set_subcomercial(val):
            st.session_state.sub_nav_comercial = val

        if c1.button("🏠 Inicio Hub", use_container_width=True): set_subcomercial("🏠 Landing Comercial")
        if c2.button("🚀 Campañas", use_container_width=True): set_subcomercial("🚀 Motor de Campañas")
        if c3.button("📊 CRM (Kanban)", use_container_width=True): set_subcomercial("📊 Embudo CRM (Kanban)")
        if c4.button("🌊 Innovación", use_container_width=True): set_subcomercial("🌊 Innovación & Océanos Azules")
        if c5.button("🧠 Flujogramas", use_container_width=True): set_subcomercial("🧠 Diseñador de Flujos (Playbook)")
        if c6.button("📱 Infografías", use_container_width=True): set_subcomercial("📱 Generador de Infografías RRSS")

        st.markdown("---")

        if sub_nav_com == "🏠 Landing Comercial":
            st.markdown("""
                <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 15px; margin-bottom: 25px; color: white;'>
                    <h1 style='color: white; margin: 0; font-size: 2.2em; font-weight: 900;'>💼 Hub de Gestión Comercial & Marketing Pro</h1>
                    <p style='color: #94a3b8; margin: 10px 0 0 0; font-size: 1.1em;'>Selecciona el módulo comercial que deseas operar hoy.</p>
                </div>
            """, unsafe_allow_html=True)
            
            m1, m2 = st.columns(2)
            m1.button("🚀 3.1 Motor de Campañas & Outreach", on_click=set_subcomercial, args=("🚀 Motor de Campañas",), use_container_width=True)
            m2.button("📊 3.2 Embudo CRM (Kanban)", on_click=set_subcomercial, args=("📊 Embudo CRM (Kanban)",), use_container_width=True)

            m3, m4 = st.columns(2)
            m3.button("🌊 3.3 Innovación & Océanos Azules", on_click=set_subcomercial, args=("🌊 Innovación & Océanos Azules",), use_container_width=True)
            m4.button("🧠 3.4 Diseñador de Flujos (Playbooks)", on_click=set_subcomercial, args=("🧠 Diseñador de Flujos (Playbook)",), use_container_width=True)

            m5, _ = st.columns([0.5, 0.5])
            m5.button("📱 3.5 Generador de Infografías RRSS (4K)", on_click=set_subcomercial, args=("📱 Generador de Infografías RRSS",), use_container_width=True)

        elif sub_nav_com == "🚀 Motor de Campañas":
            from src.web.app import render_campaign_launcher
            render_campaign_launcher()
        elif sub_nav_com == "📊 Embudo CRM (Kanban)":
            from src.web.app import render_crm_kanban
            render_crm_kanban()
        elif sub_nav_com == "🌊 Innovación & Océanos Azules":
            from src.web.app import render_blue_ocean_ui
            render_blue_ocean_ui()
        elif sub_nav_com == "🧠 Diseñador de Flujos (Playbook)":
            from src.web.app import render_flujograma
            render_flujograma()
        elif sub_nav_com == "📱 Generador de Infografías RRSS":
            from src.web.infographic_generator_ui import render_infographic_generator_ui
            render_infographic_generator_ui()

    # ----------------------------------------------------
    # 📥 4. CENTRAL DE OPERACIONES
    # ----------------------------------------------------
    elif nav == "📥 4. Ingesta de Datos":
        from src.web.app import render_unified_vault
        render_unified_vault()



    # Pie de página en sidebar
    st.sidebar.markdown("---")
    import datetime
    st.sidebar.markdown(f"v4.1.0 | Metodología Activa | Sincronizado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")

if __name__ == "__main__":
    main()

