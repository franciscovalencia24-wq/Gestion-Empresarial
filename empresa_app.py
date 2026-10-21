import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import tempfile
import subprocess
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuración de Página Streamlit
st.set_page_config(
    page_title="Gestión Empresarial - Altus Core",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Prevenir que la traducción automática de Google Chrome rompa el DOM de React
st.markdown("""
<head>
    <meta name="google" content="notranslate">
</head>
<style>
    html { translate: no !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DESCARGA ATÓMICA DE GCS (Global y Thread-safe para todo el contenedor)
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Sincronizando Bóveda de Seguridad (Global)...")
def sync_gcs_on_boot_global():
    try:
        from src.utils.gcs_sync import download_db_from_gcs
        download_db_from_gcs()
    except Exception as e:
        import logging
        logging.error(f"Global GCS sync failed: {e}")
    return True

sync_gcs_on_boot_global()

# Inicialización por sesión (para que cada pestaña tenga la generación actual de GCS)
if "gcs_session_initialized" not in st.session_state:
    try:
        from src.utils.gcs_sync import download_db_from_gcs, get_gcs_cloud_status
        should_download = not os.path.exists("data/crm_database.db")
        if not should_download:
            try:
                import sqlite3
                conn_chk = sqlite3.connect("data/crm_database.db")
                c_chk = conn_chk.cursor()
                c_chk.execute("SELECT COUNT(*) FROM company_financial_movements")
                cnt = c_chk.fetchone()[0]
                conn_chk.close()
                if cnt < 90:
                    should_download = True
            except Exception:
                should_download = True

        if should_download:
            download_db_from_gcs()

        c_stat = get_gcs_cloud_status()
        if c_stat.get("exists"):
            st.session_state.gcs_db_generation = c_stat.get("generation")
            st.session_state.gcs_last_sync_time = c_stat.get("updated_chile_str")
        st.session_state["gcs_session_initialized"] = True
    except Exception as e:
        import logging
        logging.warning(f"Session GCS init check: {e}")

# -----------------------------------------------------------------------------
# BASE DE DATOS Y CONEXIÓN CENTRALIZADA (data/crm_database.db)
# -----------------------------------------------------------------------------
sys.path.append(os.getcwd())
from src.database.connection import engine, SessionLocal, Base
from src.database.models import CompanyFinancialMovement, CompanyAccount

try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

# -----------------------------------------------------------------------------
# INTERFAZ DE USUARIO PRINCIPAL
# -----------------------------------------------------------------------------
from src.web.company_management_ui import render_company_management_ui

render_company_management_ui()

