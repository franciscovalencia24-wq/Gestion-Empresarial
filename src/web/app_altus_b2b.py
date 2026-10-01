import streamlit as st
import os
import sys

# Asegurar que el directorio raíz esté en el path
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

st.set_page_config(page_title="Altus Core - B2B Institucional", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    .main, .sidebar-content, div[data-testid="stMarkdownContainer"] p {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stDeployButton {display:none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

# Menú lateral limpio con logo
altus_logo_path = os.path.join(root_path, "assets", "brand", "altus_ai_logo_dark.svg")
if os.path.exists(altus_logo_path):
    st.sidebar.image(altus_logo_path, width=140)
else:
    st.sidebar.title("🏢 Altus AI - B2B")

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='background: radial-gradient(circle at top right, #0f172a 0%, #020617 100%); padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 20px; text-align: center;'>
    <p style='color: #38bdf8; font-weight: 700; margin: 0; font-size: 0.9em; text-transform: uppercase;'>Portal de Administración</p>
    <p style='color: #f8fafc; font-size: 1.2em; font-weight: 500; margin: 0;'>Institucional B2B</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: #64748b; font-size: 0.8rem;'>Powered by <b>Altus Core</b><br>© ALTUS AI SpA</div>", unsafe_allow_html=True)

# Parche SQL en caliente para la base de datos B2B
from src.database.connection import engine
from sqlalchemy import text
for query in [
    "ALTER TABLE empresas_b2b ADD COLUMN ultimo_certificado_hash VARCHAR(64)",
    "ALTER TABLE empresas_b2b ADD COLUMN fecha_ultimo_certificado VARCHAR(50)"
]:
    try:
        with engine.connect() as con:
            con.execute(text(query))
            con.commit()
    except Exception:
        pass

# Invocar la UI de B2B
from src.web.b2b_management_ui import render_b2b_management_ui
from src.web.b2b_employee_portal_ui import render_b2b_employee_portal

def main():
    query_params = st.query_params
    if "b2b_token" in query_params:
        token = query_params["b2b_token"]
        render_b2b_employee_portal(token)
    else:
        render_b2b_management_ui()

if __name__ == "__main__":
    main()
