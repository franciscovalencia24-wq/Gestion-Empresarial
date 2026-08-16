import streamlit as st
import os
from src.stonex_onboarding.fill_excel import generate_stonex_excel

st.set_page_config(page_title="Stonex Onboarding", page_icon="🚀", layout="centered")

def main():
    st.title("Apertura de Cuenta StoneX")
    st.markdown("Bienvenido al proceso de apertura de cuenta internacional. Por favor complete los siguientes pasos para procesar su solicitud (ACAT).")
    
    # Custom CSS to make it look elegant (Typeform style)
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            border-radius: 20px;
            background-color: #0052cc;
            color: white;
            padding: 10px;
            font-weight: bold;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
        }
        .stSelectbox>div>div>div {
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if "step" not in st.session_state:
        st.session_state.step = 1
        st.session_state.data = {}
        
    step = st.session_state.step
    
    # Barra de progreso
    st.progress(step / 4)
    
    if step == 1:
        st.header("1. Datos Personales")
        with st.form("form_step_1"):
            nombre = st.text_input("Nombre Completo (como aparece en su documento)")
            rut = st.text_input("RUT / Nro Documento")
            email = st.text_input("Correo Electrónico")
            estado_civil = st.selectbox("Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"])
            ocupacion = st.text_input("Profesión / Ocupación")
            
            submitted = st.form_submit_button("Siguiente ->")
            if submitted:
                if nombre and rut and email:
                    st.session_state.data.update({
                        "nombre_completo": nombre,
                        "rut": rut,
                        "email": email,
                        "estado_civil": estado_civil,
                        "ocupacion": ocupacion
                    })
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("Por favor complete los campos obligatorios.")
                    
    elif step == 2:
        st.header("2. Perfilamiento de Inversión")
        with st.form("form_step_2"):
            st.info("Estas preguntas son exigidas por la regulación estadounidense (SEC).")
            horizonte = st.selectbox("1 - ¿Cuál es su horizonte de tiempo para esta inversión?", [
                "Menos de 1 año", "1 - 3 años", "3 - 5 años", "5 - 10 años", "Más de 10 años"
            ])
            experiencia = st.selectbox("2 - Experiencia en inversiones (Años)", [
                "Ninguna", "Limitada (1-3 años)", "Buena (3-5 años)", "Extensa (Más de 5 años)"
            ])
            porcentaje = st.selectbox("3 - ¿Qué porcentaje de sus activos totales líquidos representa esta inversión?", [
                "Menos del 10%", "10% - 25%", "25% - 50%", "Más del 50%"
            ])
            objetivos = st.selectbox("4 - Objetivos de inversión", [
                "Preservación de capital", "Generación de ingresos", "Crecimiento moderado", "Crecimiento agresivo"
            ])
            tolerancia = st.selectbox("5 - ¿Cuál es su tolerancia al riesgo frente a caídas temporales del mercado?", [
                "Baja", "Media", "Alta"
            ])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("<- Volver"):
                    st.session_state.step = 1
                    st.rerun()
            with col2:
                if st.form_submit_button("Siguiente ->"):
                    st.session_state.data.update({
                        "horizonte_tiempo": horizonte,
                        "experiencia": experiencia,
                        "porcentaje_activos": porcentaje,
                        "objetivos_inversion": objetivos,
                        "tolerancia_riesgo": tolerancia
                    })
                    st.session_state.step = 3
                    st.rerun()

    elif step == 3:
        st.header("3. Origen de Fondos e Información Financiera")
        with st.form("form_step_3"):
            ingresos = st.selectbox("Ingresos Anuales Estimados (USD)", [
                "Menos de 50.000", "50.000 - 100.000", "100.000 - 250.000", "Más de 250.000"
            ])
            patrimonio = st.selectbox("Patrimonio Total Estimado (USD)", [
                "Menos de 100.000", "100.000 - 500.000", "500.000 - 1.000.000", "Más de 1.000.000"
            ])
            origen = st.selectbox("Origen principal de los fondos", [
                "Ahorros / Salario", "Venta de propiedad", "Herencia", "Inversiones previas", "Venta de empresa"
            ])
            monto = st.text_input("Monto aproximado de inversión inicial (USD)", value="50000")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("<- Volver"):
                    st.session_state.step = 2
                    st.rerun()
            with col2:
                if st.form_submit_button("Siguiente ->"):
                    st.session_state.data.update({
                        "ingresos_anuales": ingresos,
                        "patrimonio_total": patrimonio,
                        "origen_fondos": origen,
                        "monto_inversion": monto
                    })
                    st.session_state.step = 4
                    st.rerun()

    elif step == 4:
        st.header("4. Carga de Documentos Obligatorios")
        st.write("Para procesar la transferencia de su cuenta (ACAT), requerimos los siguientes documentos.")
        
        with st.form("form_step_4"):
            st.file_uploader("1. Cédula de Identidad (Ambos lados en un solo PDF/Imagen)", type=["pdf", "jpg", "png"])
            st.file_uploader("2. Comprobante de Domicilio (Agua, Luz, Teléfono)", type=["pdf", "jpg", "png"])
            st.file_uploader("3. Última Cartola de Inversiones (SURA/Pershing/Etc)", type=["pdf"])
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("<- Volver"):
                    st.session_state.step = 3
                    st.rerun()
            with col2:
                submitted = st.form_submit_button("✅ Finalizar y Enviar")
                if submitted:
                    st.session_state.step = 5
                    st.rerun()

    elif step == 5:
        st.success("¡Formulario Completado Exitosamente!")
        st.balloons()
        
        st.write("Generando los documentos oficiales para StoneX y Principal...")
        
        # Generar el Excel
        try:
            nombre_cliente = st.session_state.data.get('nombre_completo', 'Cliente')
            filename = f"Stonex_Apertura_{nombre_cliente.replace(' ', '_')}.xlsx"
            excel_path = generate_stonex_excel(st.session_state.data, output_filename=filename)
            
            st.write("### Sus Documentos de Onboarding están listos:")
            
            with open(excel_path, "rb") as file:
                st.download_button(
                    label="📥 Descargar Excel de Onboarding (Stonex)",
                    data=file,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.markdown("---")
            st.write("### Para uso interno del Asesor:")
            st.write("Copia este texto y envíalo a `dlpichilecomplianceoffshore@exchange.principal.com` con copia a Averta Support:")
            
            email_text = f"""
**Asunto:** Onboarding y ACAT In - {nombre_cliente}

Estimados,
Adjunto la documentación para la apertura de cuenta en StoneX del cliente **{nombre_cliente}**.
Adicionalmente, adjuntamos la cartola de inversiones (Pershing) ya que la cuenta será fondeada vía **ACAT** por un monto aproximado de USD {st.session_state.data.get('monto_inversion', '50.000')}.

Por favor confirmar cuando se envíe el DocuSign al cliente.
Quedo atento.
            """
            st.code(email_text, language="markdown")
            
        except Exception as e:
            st.error(f"Hubo un error al generar el Excel: {e}")
            
        if st.button("Empezar un nuevo cliente"):
            st.session_state.step = 1
            st.session_state.data = {}
            st.rerun()

if __name__ == "__main__":
    main()
