import streamlit as st
import os
import datetime
from src.web.b2b_onboarding_ui import render_b2b_onboarding
from src.database.connection import get_db
from src.database.models import EjecutivoB2B

st.set_page_config(page_title="Altus Core - Onboarding Corporativo", page_icon="🚀", layout="centered")

def get_ejecutivo_by_token(token: str):
    try:
        db = next(get_db())
        ejecutivo = db.query(EjecutivoB2B).filter(EjecutivoB2B.token_acceso == token).first()
        return ejecutivo
    except Exception as e:
        print(f"Error validating token: {e}")
        return None

def is_token_valid(ejecutivo):
    if not ejecutivo:
        return False
    if ejecutivo.fecha_expiracion_acceso and datetime.datetime.utcnow() > ejecutivo.fecha_expiracion_acceso:
        return False
    return True

def main():
    # Inicializar estado de la sesión para el token
    if "b2b_token" not in st.session_state:
        st.session_state.b2b_token = None
        
    query_params = st.query_params
    url_token = query_params.get("b2b_token", None)
    
    # Si viene en la URL un token nuevo, lo capturamos
    if url_token and url_token != st.session_state.b2b_token:
        st.session_state.b2b_token = url_token
        
    token_to_check = st.session_state.b2b_token
    
    # Custom CSS para una apariencia elegante (estilo Typeform corporativo)
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            background-color: #0A2342;
            color: white;
            padding: 10px;
            font-weight: bold;
            border: none;
        }
        .stButton>button:hover {
            background-color: #1E3A5F;
        }
        .stTextInput>div>div>input {
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Si hay token en la sesión, lo validamos transaccionalmente
    if token_to_check:
        ejecutivo = get_ejecutivo_by_token(token_to_check)
        if is_token_valid(ejecutivo):
            # Renderizamos el onboarding inyectando el componente UI seguro
            render_b2b_onboarding(token_to_check)
            return
        else:
            st.error("Token de acceso inválido, expirado o no reconocido.")
            st.session_state.b2b_token = None
            if "b2b_token" in st.query_params:
                del st.query_params["b2b_token"]
            st.stop()
            
    # Pantalla de acceso general si no hay token en la URL o si la validación falló
    st.title("Altus Core")
    st.markdown("### Portal B2B Corporativo")
    st.markdown("Bienvenido al portal exclusivo para ejecutivos. Por favor, ingrese su token de acceso único para iniciar su Levantamiento Patrimonial 360 de forma privada y segura.")
    
    with st.container():
        st.write("")
        st.write("")
        token_input = st.text_input("🔑 Token de Acceso Único", type="password", placeholder="Ingrese el token provisto por su empleador...")
        st.write("")
        if st.button("Ingresar al Portal Privado"):
            if token_input:
                # Validar el token antes de aceptarlo en la sesión
                ej = get_ejecutivo_by_token(token_input)
                if is_token_valid(ej):
                    st.session_state.b2b_token = token_input
                    st.query_params["b2b_token"] = token_input
                    st.rerun()
                else:
                    st.error("El token ingresado no es válido o ha expirado.")
            else:
                st.warning("Por favor ingrese su token de acceso.")
                
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray; font-size: 0.8em;'>© 2024 ALTUS AI SpA. Todos los derechos reservados. Su información está protegida bajo estrictos estándares de confidencialidad.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
