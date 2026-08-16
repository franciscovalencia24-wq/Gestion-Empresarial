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
    
    # Modo Demo en Sidebar
    st.sidebar.markdown("### Herramientas de Desarrollo")
    if st.sidebar.button("🤖 Llenar con Datos de Prueba"):
        st.session_state.data = {
            "nombre_completo": "Juan Pérez Demo",
            "rut": "15.444.333-2",
            "email": "juan.demo@altus.cl",
            "estado_civil": "Casado/a",
            "ocupacion": "Ingeniero Civil",
            "horizonte_tiempo": "5 - 10 años",
            "experiencia": "Buena (3-5 años)",
            "porcentaje_activos": "25% - 50%",
            "objetivos_inversion": "Crecimiento agresivo",
            "tolerancia_riesgo": "Alta",
            "ingresos_anuales": "100.000 - 250.000",
            "patrimonio_total": "500.000 - 1.000.000",
            "origen_fondos": "Venta de empresa",
            "monto_inversion": "150000"
        }
        st.session_state.step = 1
        st.rerun()
        
    # Barra de progreso
    st.progress(step / 5)
    
    def get_idx(opciones, clave, default):
        val = st.session_state.data.get(clave, default)
        return opciones.index(val) if val in opciones else 0

    if step == 1:
        st.header("1. Datos Personales")
        with st.form("form_step_1"):
            nombre = st.text_input("Nombre Completo (como aparece en su documento)", value=st.session_state.data.get("nombre_completo", ""))
            rut = st.text_input("RUT / Nro Documento", value=st.session_state.data.get("rut", ""))
            email = st.text_input("Correo Electrónico", value=st.session_state.data.get("email", ""))
            
            opc_ec = ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"]
            estado_civil = st.selectbox("Estado Civil", opc_ec, index=get_idx(opc_ec, "estado_civil", "Soltero/a"))
            
            ocupacion = st.text_input("Profesión / Ocupación", value=st.session_state.data.get("ocupacion", ""))
            
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
            
            opc_hor = ["Menos de 1 año", "1 - 3 años", "3 - 5 años", "5 - 10 años", "Más de 10 años"]
            horizonte = st.selectbox("1 - ¿Cuál es su horizonte de tiempo para esta inversión?", opc_hor, index=get_idx(opc_hor, "horizonte_tiempo", opc_hor[0]))
            
            opc_exp = ["Ninguna", "Limitada (1-3 años)", "Buena (3-5 años)", "Extensa (Más de 5 años)"]
            experiencia = st.selectbox("2 - Experiencia en inversiones (Años)", opc_exp, index=get_idx(opc_exp, "experiencia", opc_exp[0]))
            
            opc_porc = ["Menos del 10%", "10% - 25%", "25% - 50%", "Más del 50%"]
            porcentaje = st.selectbox("3 - ¿Qué porcentaje de sus activos totales líquidos representa esta inversión?", opc_porc, index=get_idx(opc_porc, "porcentaje_activos", opc_porc[0]))
            
            opc_obj = ["Preservación de capital", "Generación de ingresos", "Crecimiento moderado", "Crecimiento agresivo"]
            objetivos = st.selectbox("4 - Objetivos de inversión", opc_obj, index=get_idx(opc_obj, "objetivos_inversion", opc_obj[0]))
            
            opc_tol = ["Baja", "Media", "Alta"]
            tolerancia = st.selectbox("5 - ¿Cuál es su tolerancia al riesgo frente a caídas temporales del mercado?", opc_tol, index=get_idx(opc_tol, "tolerancia_riesgo", opc_tol[0]))
            
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
            opc_ing = ["Menos de 50.000", "50.000 - 100.000", "100.000 - 250.000", "Más de 250.000"]
            ingresos = st.selectbox("Ingresos Anuales Estimados (USD)", opc_ing, index=get_idx(opc_ing, "ingresos_anuales", opc_ing[0]))
            
            opc_pat = ["Menos de 100.000", "100.000 - 500.000", "500.000 - 1.000.000", "Más de 1.000.000"]
            patrimonio = st.selectbox("Patrimonio Total Estimado (USD)", opc_pat, index=get_idx(opc_pat, "patrimonio_total", opc_pat[0]))
            
            opc_ori = ["Ahorros / Salario", "Venta de propiedad", "Herencia", "Inversiones previas", "Venta de empresa"]
            origen = st.selectbox("Origen principal de los fondos", opc_ori, index=get_idx(opc_ori, "origen_fondos", opc_ori[0]))
            
            monto = st.text_input("Monto aproximado de inversión inicial (USD)", value=st.session_state.data.get("monto_inversion", "50000"))
            
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
