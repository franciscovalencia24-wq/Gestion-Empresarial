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
# SINCRONIZACIÓN AUTOMÁTICA CON LA NUBE (Google Cloud Storage)
# -----------------------------------------------------------------------------
# Cada vez que se abre la app o inicia una sesión, se verifica con GCS
# que la base de datos local sea idéntica a la última generación de la Bóveda.
# Si la Nube tiene una versión más nueva, se descarga automáticamente.
if "gcs_session_initialized" not in st.session_state:
    try:
        from src.utils.gcs_sync import ensure_latest_database_from_gcs, get_gcs_cloud_status
        ensure_latest_database_from_gcs()

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

