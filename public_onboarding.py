import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import importlib
import datetime
import src.stonex_onboarding.fill_excel as fill_excel_module
importlib.reload(fill_excel_module)
from src.stonex_onboarding.fill_excel import generate_stonex_excel
from src.stonex_onboarding.send_email import send_onboarding_email
from src.stonex_onboarding.draft_manager import save_draft, load_draft

st.set_page_config(page_title="Stonex Onboarding", page_icon="🚀", layout="centered")

def render_save_section():
    st.markdown("---")
    st.markdown("#### 💾 ¿Necesitas pausar y continuar después?")
    if st.button("Guardar progreso ahora"):
        token = st.session_state.get("token", None)
        new_token = save_draft(st.session_state.step, st.session_state.data, token)
        
        if new_token and new_token.startswith("ERROR:"):
            st.error(f"No se pudo guardar el progreso. Error interno: {new_token}")
        else:
            st.session_state.token = new_token
            # Build the save link
            base_url = "https://fv-registro.streamlit.app" # Default cloud url
            save_link = f"{base_url}/?token={new_token}"
            
            st.success("Tu progreso ha sido guardado de forma segura.")
            st.markdown("⚠️ **IMPORTANTE:** Debes **COPIAR** el siguiente enlace si deseas continuar en otro momento o desde otro dispositivo.")
            
            st.text_input("Haz clic aquí y copia todo el texto:", value=save_link, key=f"copy_save_link_{new_token}", help="Este es tu enlace único. Si lo pierdes, perderás tu progreso.")
            
            html_code = f"""
            <div style="display: flex; justify-content: center;">
                <button id="copyBtn" style="background-color: #0A2342; color: white; border: none; padding: 10px 24px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; font-family: sans-serif;">
                    📋 Copiar Enlace Automáticamente
                </button>
            </div>
            <script>
                const btn = document.getElementById('copyBtn');
                btn.addEventListener('click', () => {{
                    navigator.clipboard.writeText('{save_link}').then(() => {{
                        btn.innerHTML = '✅ ¡Copiado y Listo!';
                        setTimeout(() => {{ btn.innerHTML = '📋 Copiar Enlace Automáticamente'; }}, 3000);
                    }}).catch(err => {{
                        console.error('Error al copiar: ', err);
                        btn.innerHTML = '❌ Error al copiar (Cópialo manualmente arriba)';
                    }});
                }});
            </script>
            """
            components.html(html_code, height=70)
            
            st.info("Para retomar más tarde, simplemente pega ese enlace en tu navegador de internet.")

def main():
    st.title("Portal de Registro Clientes")
    st.markdown("Bienvenido al proceso de apertura de cuenta. Por favor complete los siguientes pasos para procesar su solicitud.")
    
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
        query_params = st.query_params
        if "token" in query_params:
            token = query_params["token"]
            saved_step, saved_data = load_draft(token)
            if saved_step is not None:
                st.session_state.step = saved_step
                st.session_state.data = saved_data
                st.session_state.token = token
                st.success("¡Progreso cargado exitosamente! Puedes continuar donde lo dejaste.")
            else:
                st.error("El enlace de guardado es inválido o expiró.")
                st.session_state.step = 1
                st.session_state.data = {}
        else:
            st.session_state.step = 1
            st.session_state.data = {}
            
    if "pending_toast" in st.session_state:
        st.toast(st.session_state.pending_toast)
        del st.session_state["pending_toast"]
        
    step = st.session_state.step
    
    # Tipo de cuenta global
    st.markdown("### ¿Qué tipo de cuenta desea abrir?")
    tipo_cuenta_actual = st.session_state.data.get("tipo_cuenta", "Persona Natural")
    tipo_cuenta = st.radio("Tipo de Cliente", ["Persona Natural", "Persona Jurídica"], index=0 if tipo_cuenta_actual == "Persona Natural" else 1)
    if tipo_cuenta != tipo_cuenta_actual:
        st.session_state.data["tipo_cuenta"] = tipo_cuenta

        st.session_state.step = 1
        st.rerun()
        
    # Scroll to Top (Gamification & UX hack) - Forced re-render by appending step
    components.html(
        f"""
        <script>
            /* Render trigger for step {step} */
            setTimeout(function() {{
                var elements = window.parent.document.querySelectorAll('.stApp, .main, [data-testid="stAppViewContainer"]');
                elements.forEach(function(el) {{ el.scrollTo({{ top: 0, behavior: 'smooth' }}); }});
                window.parent.scrollTo({{ top: 0, behavior: 'smooth' }});
            }}, 200);
        </script>
        """,
        height=0
    )

    # Mensajes motivacionales
    mensajes_progreso = {
        1: "Paso 1 de 5: ¡Empecemos con tus datos básicos! 🏁",
        2: "Paso 2 de 5: Tu perfil de riesgo es clave para protegerte 🛡️",
        3: "Paso 3 de 5: ¡Ya vas por la mitad, excelente ritmo! 🔥",
        4: "Paso 4 de 5: ¡Último paso! Solo nos faltan los documentos 📂",
        5: "Paso 5 de 5: ¡Todo listo! 🎉"
    }
    if tipo_cuenta == "Persona Jurídica" and step == 1:
        mensajes_progreso[1] = "Paso 1 de 5: ¡Empecemos con los datos de tu empresa! 🏢"
        
    st.markdown(f"**{mensajes_progreso.get(step, '')}**")
    st.progress(step / 5)
    
    def get_idx(opciones, clave, default):
        val = st.session_state.data.get(clave, default)
        return opciones.index(val) if val in opciones else 0

    if step == 1:
        st.header("1. Datos Personales 👤" if tipo_cuenta == "Persona Natural" else "1. Datos de la Empresa y Representante 🏢")
        if tipo_cuenta == "Persona Natural":
            st.info("""
**Información a adjuntar Persona Natural:**
- ID vigente del titular - cédula de identidad.
- Evidencia de domicilio vigente del titular.
- Estado de cuenta actual desde donde se transferirán los fondos, que sustente el monto de la inversión.
- Evidenciar cómo se generaron los fondos a invertir, por ejemplo:
    - Venta de propiedad – presentar contrato de compraventa.
    - Herencia – presentar adjudicación por sucesión.
    - Ingresos regulares – declaración jurada o recibos de ingresos regulares.
    - Profesión del cliente – ingresos regulares / declaración jurada.
- Solo se aceptará la presentación de declaración jurada del titular como evidencia válida de sus ingresos regulares.
""")
        with st.form("form_step_1"):
            if tipo_cuenta == "Persona Natural":
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    pn_primer_nombre = st.text_input("Primer Nombre", value=st.session_state.data.get("pn_primer_nombre", ""))
                with col_n2:
                    pn_segundo_nombre = st.text_input("Segundo Nombre", value=st.session_state.data.get("pn_segundo_nombre", ""))
                
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    pn_primer_apellido = st.text_input("Primer Apellido", value=st.session_state.data.get("pn_primer_apellido", ""))
                with col_a2:
                    pn_segundo_apellido = st.text_input("Segundo Apellido", value=st.session_state.data.get("pn_segundo_apellido", ""))
                
                rut = st.text_input("RUT / Nro Documento", value=st.session_state.data.get("rut", ""))
                email = st.text_input("Correo Electrónico", value=st.session_state.data.get("email", ""))
                
                st.caption("💡 *Tip: Puedes escribir el año manualmente o usar el calendario.*")
                fecha_nacimiento = st.date_input("Fecha de Nacimiento", value=pd.to_datetime(st.session_state.data.get("fecha_nacimiento", "1960-01-01")).date(), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 1, 1))
                
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    direccion_residencia = st.text_input("Dirección de Residencia", value=st.session_state.data.get("direccion_residencia", ""))
                    ciudad = st.text_input("Ciudad", value=st.session_state.data.get("ciudad", ""))
                with col_d2:
                    provincia = st.text_input("Provincia (Región)", value=st.session_state.data.get("provincia", ""))
                    codigo_postal = st.text_input("Código Postal", value=st.session_state.data.get("codigo_postal", ""))
                
                st.markdown("##### Dirección de Correspondencia")
                st.info("Complete solo si su dirección de correspondencia es **distinta** a la de residencia.")
                direccion_correspondencia = st.text_input("Dirección de Correspondencia", value=st.session_state.data.get("direccion_correspondencia", ""))
                difiere_dir = True if direccion_correspondencia else False
                
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    telefono = st.text_input("Teléfono", value=st.session_state.data.get("telefono", ""))
                with col_t2:
                    acepta_correo = st.selectbox("¿Acepta que la correspondencia sea por correo electrónico?", ["Sí", "No"], index=get_idx(["Sí", "No"], "acepta_correo", "Sí"))

                col1, col2 = st.columns(2)
                with col1:
                    opc_pais = ["Chile", "Perú", "Colombia", "Estados Unidos", "Otro"]
                    pais_res = st.selectbox("País de Residencia", opc_pais, index=get_idx(opc_pais, "pais_residencia", "Chile"))
                    
                    opc_nac = ["Chilena", "Peruana", "Colombiana", "Estadounidense", "Otra"]
                    nac = st.selectbox("Nacionalidad", opc_nac, index=get_idx(opc_nac, "nacionalidad", "Chilena"))
                    ciud = st.selectbox("Ciudadanía", opc_nac, index=get_idx(opc_nac, "ciudadania", "Chilena"))
                    
                    opc_td = ["ID Nacional", "Pasaporte"]
                    tipo_doc = st.selectbox("Tipo de Documento", opc_td, index=get_idx(opc_td, "tipo_documento", "ID Nacional"))
                    pais_emi = st.selectbox("País Emisor Documento", opc_pais, index=get_idx(opc_pais, "pais_emisor_doc", "Chile"))
                    
                with col2:
                    opc_ec = ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"]
                    estado_civil = st.selectbox("Estado Civil", opc_ec, index=get_idx(opc_ec, "estado_civil", "Soltero/a"))
                    
                    cantidad_hijos = st.text_input("Cantidad de Hijos", value=st.session_state.data.get("cantidad_hijos", "0"))

                    opc_sit = ["Empleado", "Independiente", "Jubilado", "Desempleado", "Estudiante"]
                    sit_lab = st.selectbox("Situación Laboral", opc_sit, index=get_idx(opc_sit, "situacion_laboral", "Empleado"))
                    
                    ocupacion = st.text_input("Profesión / Ocupación", value=st.session_state.data.get("ocupacion", ""))
                    
                    opc_pep = ["No", "Sí"]
                    pep = st.selectbox("¿Es Persona Expuesta Políticamente (PEP)?", opc_pep, index=get_idx(opc_pep, "pep", "No"))
                
                # Cónyuge (Siempre visible para evitar bloqueo del form, pero marcado como condicional)
                st.markdown("---")
                st.markdown("##### Datos del Cónyuge")
                st.info("Complete esta sección **solo si seleccionó 'Casado/a'** en su Estado Civil.")
                cc1, cc2 = st.columns(2)
                with cc1:
                    con_nombres = st.text_input("Nombres del Cónyuge", value=st.session_state.data.get("con_nombres", ""))
                with cc2:
                    con_apellidos = st.text_input("Apellidos del Cónyuge", value=st.session_state.data.get("con_apellidos", ""))
                
                cc3, cc4 = st.columns(2)
                with cc3:
                    con_rut = st.text_input("Número de Documento / RUT Cónyuge", value=st.session_state.data.get("con_rut", ""))
                with cc4:
                    con_fecha_nac = str(st.date_input("Fecha Nacimiento Cónyuge", value=pd.to_datetime(st.session_state.data.get("con_fecha_nac", "1960-01-01")).date(), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 1, 1)))
                    
                cc5, cc6 = st.columns(2)
                with cc5:
                    con_tipo_doc = st.selectbox("Tipo Doc. Cónyuge", opc_td, index=get_idx(opc_td, "con_tipo_doc", "ID Nacional"))
                with cc6:
                    con_pais_emi = st.selectbox("País Emisor Doc. Cónyuge", opc_pais, index=get_idx(opc_pais, "con_pais_emi", "Chile"))
                
                cc7, cc8 = st.columns(2)
                with cc7:
                    con_nac = st.selectbox("Nacionalidad Cónyuge", opc_nac, index=get_idx(opc_nac, "con_nac", "Chilena"))
                with cc8:
                    con_sit_lab = st.selectbox("Situación Laboral Cónyuge", opc_sit, index=get_idx(opc_sit, "con_sit_lab", "Empleado"))
                    
                st.info("💡 Si su cónyuge es Empleado o Independiente, por favor indique su cargo y empresa.")
                cc9, cc10, cc11 = st.columns(3)
                with cc9:
                    con_cargo = st.text_input("Cargo del Cónyuge", value=st.session_state.data.get("con_cargo", ""))
                with cc10:
                    con_empresa = st.text_input("Empresa del Cónyuge", value=st.session_state.data.get("con_empresa", ""))
                with cc11:
                    con_rubro = st.text_input("Rubro de la Empresa", value=st.session_state.data.get("con_rubro", ""))
                    
                # Guardamos los valores dinámicos para que no se pierdan en el submit
                st.session_state.data["con_cargo"] = con_cargo
                st.session_state.data["con_empresa"] = con_empresa
                st.session_state.data["con_rubro"] = con_rubro
                
                submitted = st.form_submit_button("Siguiente ->")
                if submitted:
                    pn_valid = all([pn_primer_nombre, pn_primer_apellido, rut, email, direccion_residencia, ciudad, provincia, codigo_postal, telefono, ocupacion, cantidad_hijos])
                    dir_valid = True if not difiere_dir else bool(direccion_correspondencia)
                    con_valid = True if estado_civil != "Casado/a" else all([con_nombres, con_apellidos, con_rut])
                    
                    if not pn_valid:
                        st.error("Por favor complete todos los campos obligatorios de sus Datos Personales (nombres, RUT, correo, dirección completa, teléfono, ocupación, cantidad de hijos).")
                    elif not dir_valid:
                        st.error("Indicó que su dirección de correspondencia es distinta. Por favor, complétela.")
                    elif not con_valid:
                        st.error("Seleccionó estado civil Casado/a. Por favor complete los Nombres, Apellidos y RUT de su Cónyuge.")
                    else:
                        st.session_state.data.update({
                            "pn_primer_nombre": pn_primer_nombre, "pn_segundo_nombre": pn_segundo_nombre,
                            "pn_primer_apellido": pn_primer_apellido, "pn_segundo_apellido": pn_segundo_apellido,
                            # Create backwards compatible 'nombre_completo' just in case
                            "nombre_completo": f"{pn_primer_nombre} {pn_segundo_nombre} {pn_primer_apellido} {pn_segundo_apellido}".replace("  ", " ").strip(),
                            "rut": rut, "email": email, "fecha_nacimiento": str(fecha_nacimiento),
                            "direccion_residencia": direccion_residencia, "ciudad": ciudad, "provincia": provincia,
                            "codigo_postal": codigo_postal, "direccion_correspondencia": direccion_correspondencia,
                            "telefono": telefono, "pais_residencia": pais_res, "nacionalidad": nac, "ciudadania": ciud,
                            "tipo_documento": tipo_doc, "pais_emisor_doc": pais_emi, "estado_civil": estado_civil,
                            "cantidad_hijos": cantidad_hijos, "situacion_laboral": sit_lab, "ocupacion": ocupacion, "pep": pep,
                        "con_nombres": con_nombres, "con_apellidos": con_apellidos, "con_fecha_nac": str(con_fecha_nac),
                            "con_sit_lab": con_sit_lab, "con_nac": con_nac, "con_tipo_doc": con_tipo_doc,
                            "con_pais_emi": con_pais_emi, "con_rut": con_rut, "difiere_dir": difiere_dir,
                            "con_cargo": st.session_state.data.get("con_cargo", ""), "con_empresa": st.session_state.data.get("con_empresa", ""), "con_rubro": st.session_state.data.get("con_rubro", ""),
                            "acepta_correo": acepta_correo
                        })
                        st.session_state.pending_toast = "¡Excelente! Datos iniciales listos. Vamos al siguiente paso 🚀"
                        st.session_state.step = 2
                        st.rerun()
            else:
                st.subheader("Datos de la Empresa")
                razon_social = st.text_input("Razón Social / Nombre Completo", value=st.session_state.data.get("nombre_completo", ""))
                rut_emp = st.text_input("RUT Empresa", value=st.session_state.data.get("rut_empresa", ""))
                rubro = st.text_input("Rubro", value=st.session_state.data.get("rubro", ""))
                act_eco = st.text_input("Actividad Económica", value=st.session_state.data.get("actividad_economica", ""))
                email_emp = st.text_input("Correo Electrónico Empresa", value=st.session_state.data.get("email_empresa", ""))
                descripcion_inversiones = st.text_area("Descripción del tipo y tamaño de las inversiones de la cuenta", value=st.session_state.data.get("descripcion_inversiones", ""))
                
                col1, col2 = st.columns(2)
                with col1:
                    dir_emp = st.text_input("Dirección Empresa", value=st.session_state.data.get("direccion_empresa", ""))
                    prov_emp = st.text_input("Provincia (Región)", value=st.session_state.data.get("provincia_empresa", ""))
                    opc_pais = ["Chile", "Perú", "Colombia", "Estados Unidos", "Otro"]
                    pais_emp = st.selectbox("País Empresa", opc_pais, index=get_idx(opc_pais, "pais_empresa", "Chile"))
                with col2:
                    ciud_emp = st.text_input("Ciudad Empresa", value=st.session_state.data.get("ciudad_empresa", ""))
                    cp_emp = st.text_input("Código Postal Empresa", value=st.session_state.data.get("cp_emp", ""))
                    tel_emp = st.text_input("Teléfono Empresa", value=st.session_state.data.get("telefono_empresa", ""))
                
                st.markdown("##### Cumplimiento Normativo (SEC)")
                col_c1, col_c2 = st.columns(2)
                opc_sino = ["No", "Sí"]
                with col_c1:
                    acepta_correo = st.selectbox("¿Acepta correspondencia por correo electrónico?", ["Sí", "No"], index=get_idx(["Sí", "No"], "acepta_correo", "Sí"))
                    deposito_terceros = st.selectbox("¿Tendrá depósito/retiro de terceros?", opc_sino, index=get_idx(opc_sino, "deposito_terceros", "No"))
                    fondo_cobertura = st.selectbox("¿Es fondo de cobertura/inversión?", opc_sino, index=get_idx(opc_sino, "fondo_cobertura", "No"))
                    negocios_us = st.selectbox("¿Tiene negocios con clientes en US?", opc_sino, index=get_idx(opc_sino, "negocios_us", "No"))
                    cuentas_us = st.selectbox("¿Tiene otras cuentas en US?", opc_sino, index=get_idx(opc_sino, "cuentas_us", "No"))
                with col_c2:
                    acciones_portador = st.selectbox("¿Alguna vez emitió acciones al portador?", opc_sino, index=get_idx(opc_sino, "acciones_portador", "No"))
                    es_banco = st.selectbox("¿La empresa es un banco o representa uno?", opc_sino, index=get_idx(opc_sino, "es_banco", "No"))
                    es_broker = st.selectbox("¿En US sería considerada broker?", opc_sino, index=get_idx(opc_sino, "es_broker", "No"))
                    casa_cambio = st.selectbox("¿Es casa de cambios/intermediario de dinero?", opc_sino, index=get_idx(opc_sino, "casa_cambio", "No"))
                    gubernamental = st.selectbox("¿Es una entidad gubernamental?", opc_sino, index=get_idx(opc_sino, "gubernamental", "No"))
                    fondo_asesor = st.selectbox("¿Es un fondo de inversión o asesor financiero?", opc_sino, index=get_idx(opc_sino, "fondo_asesor", "No"))
                
                st.markdown("---")
                st.subheader("Datos del Representante Legal / Beneficiario")
                
                col3, col4 = st.columns(2)
                with col3:
                    cat_rep = st.selectbox("Categoría", ["Beneficiario Final", "Representante Legal", "Apoderado"], index=get_idx(["Beneficiario Final", "Representante Legal", "Apoderado"], "categoria_rep", "Beneficiario Final"))
                    n_rep = st.text_input("Nombres Representante", value=st.session_state.data.get("nombre_rep", ""))
                    a_rep = st.text_input("Apellidos Representante", value=st.session_state.data.get("apellido_rep", ""))
                    dir_rep = st.text_input("Dirección Representante", value=st.session_state.data.get("dir_rep", ""))
                    prov_rep = st.text_input("Provincia Representante", value=st.session_state.data.get("prov_rep", ""))
                    ciud_rep = st.text_input("Ciudad Representante", value=st.session_state.data.get("ciud_rep", ""))
                    cp_rep = st.text_input("Código Postal Representante", value=st.session_state.data.get("cp_rep", ""))
                    rut_rep = st.text_input("RUT Representante", value=st.session_state.data.get("rut_rep", ""))
                    email_rep = st.text_input("Correo Representante", value=st.session_state.data.get("email_rep", ""))
                    tel_rep = st.text_input("Teléfono Representante", value=st.session_state.data.get("telefono_rep", ""))
                    porc_part = st.text_input("% de Participación", value=st.session_state.data.get("porcentaje_part", ""))
                with col4:
                    fecha_nac_rep = st.date_input("Fecha Nacimiento", value=pd.to_datetime(st.session_state.data.get("fecha_nac_rep", "1960-01-01")).date(), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 1, 1))
                    fecha_emi_doc = st.date_input("Fecha Emisión Documento", value=pd.to_datetime(st.session_state.data.get("fecha_emi_doc", "2020-01-01")).date(), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 1, 1))
                    fecha_exp_doc = st.date_input("Fecha Expiración Documento", value=pd.to_datetime(st.session_state.data.get("fecha_exp_doc", "2030-01-01")).date(), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 1, 1))
                    opc_td = ["ID Nacional", "Pasaporte", "Documento Gubernamental"]
                    tipo_doc = st.selectbox("Tipo de Documento", opc_td, index=get_idx(opc_td, "tipo_doc", "ID Nacional"))
                    pais_emi = st.selectbox("País Emisor Documento", opc_pais, index=get_idx(opc_pais, "pais_emisor_doc", "Chile"))
                    nac_rep = st.selectbox("Nacionalidad", ["Chilena", "Peruana", "Colombiana", "Estadounidense", "Otra"], index=get_idx(["Chilena", "Peruana", "Colombiana", "Estadounidense", "Otra"], "nacionalidad", "Chilena"))
                    ciud_rep = st.selectbox("Ciudadanía", ["Chilena", "Peruana", "Colombiana", "Estadounidense", "Otra"], index=get_idx(["Chilena", "Peruana", "Colombiana", "Estadounidense", "Otra"], "ciudadania", "Chilena"))
                
                col5, col6 = st.columns(2)
                with col5:
                    sit_lab = st.selectbox("Situación Laboral", ["Empleado", "Independiente", "Empleado/Independiente", "Jubilado", "Desempleado"], index=get_idx(["Empleado", "Independiente", "Empleado/Independiente", "Jubilado", "Desempleado"], "situacion_laboral", "Empleado"))
                    ocupacion = st.text_input("Ocupación", value=st.session_state.data.get("ocupacion", ""))
                    estado_civil = st.selectbox("Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"], index=get_idx(["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"], "estado_civil", "Casado/a"))
                with col6:
                    cant_hijos = st.text_input("Cantidad de hijos", value=st.session_state.data.get("cantidad_hijos", ""))
                    pep = st.selectbox("¿Es Persona Expuesta Políticamente (PEP)?", opc_sino, index=get_idx(opc_sino, "pep", "No"))
                    genero = st.selectbox("Género", ["Masculino", "Femenino", "Otro"], index=get_idx(["Masculino", "Femenino", "Otro"], "genero", "Masculino"))
                
                if sit_lab in ["Empleado", "Empleado/Independiente"]:
                    st.markdown("##### Información Laboral")
                    col7, col8 = st.columns(2)
                    with col7:
                        cargo_rep = st.text_input("Cargo", value=st.session_state.data.get("cargo_rep", ""))
                        empresa_rep = st.text_input("Empresa Empleadora", value=st.session_state.data.get("empresa_rep", ""))
                        rubro_rep = st.text_input("Rubro de la Empresa", value=st.session_state.data.get("rubro_rep", ""))
                        pais_emp_rep = st.selectbox("País Empresa Empleadora", opc_pais, index=get_idx(opc_pais, "pais_emp_rep", "Chile"))
                        prov_emp_rep = st.text_input("Provincia Empresa Empleadora", value=st.session_state.data.get("prov_emp_rep", ""))
                    with col8:
                        ciud_emp_rep = st.text_input("Ciudad Empresa Empleadora", value=st.session_state.data.get("ciud_emp_rep", ""))
                        dir_emp_rep = st.text_input("Dirección Empresa Empleadora", value=st.session_state.data.get("dir_emp_rep", ""))
                        tel_emp_rep = st.text_input("Teléfono Empresa Empleadora", value=st.session_state.data.get("tel_emp_rep", ""))
                        email_emp_rep = st.text_input("Email Empresa Empleadora", value=st.session_state.data.get("email_emp_rep", ""))
                else:
                    cargo_rep, empresa_rep, rubro_rep, pais_emp_rep, prov_emp_rep, ciud_emp_rep, dir_emp_rep, tel_emp_rep, email_emp_rep = "", "", "", "", "", "", "", "", ""
                
                submitted = st.form_submit_button("Siguiente ->")
                if submitted:
                    pj_valid = all([razon_social, rut_emp, rubro, act_eco, email_emp, dir_emp, prov_emp, ciud_emp, cp_emp])
                    rep_valid = all([n_rep, a_rep, rut_rep, email_rep, tel_rep, porc_part])
                    
                    if not pj_valid:
                        st.error("Por favor complete todos los campos obligatorios de la Empresa (Razón Social, RUT, Rubro, Dirección completa, Correo, etc).")
                    elif not rep_valid:
                        st.error("Por favor complete todos los campos obligatorios del Representante Legal (Nombres, Apellidos, RUT, Correo, Teléfono y % de participación).")
                    else:
                        st.session_state.data.update({
                            "nombre_completo": razon_social, "rut_empresa": rut_emp, 
                            "rubro": rubro, "actividad_economica": act_eco,
                            "email_empresa": email_emp, "direccion_empresa": dir_emp,
                            "provincia_empresa": prov_emp, "ciudad_empresa": ciud_emp,
                            "pais_empresa": pais_emp, "telefono_empresa": tel_emp, "cp_emp": cp_emp,
                            "descripcion_inversiones": descripcion_inversiones,
                            "acepta_correo": acepta_correo, "deposito_terceros": deposito_terceros,
                            "fondo_cobertura": fondo_cobertura, "negocios_us": negocios_us,
                            "cuentas_us": cuentas_us, "acciones_portador": acciones_portador,
                            "es_banco": es_banco, "es_broker": es_broker, "casa_cambio": casa_cambio,
                            "gubernamental": gubernamental, "fondo_asesor": fondo_asesor,
                            "categoria_rep": cat_rep, "nombre_rep": n_rep, "apellido_rep": a_rep,
                            "dir_rep": dir_rep, "prov_rep": prov_rep, "ciud_rep": ciud_rep, "cp_rep": cp_rep,
                            "rut_rep": rut_rep, "email_rep": email_rep, "telefono_rep": tel_rep,
                            "porcentaje_part": porc_part, "fecha_nac_rep": str(fecha_nac_rep),
                            "fecha_emi_doc": str(fecha_emi_doc), "fecha_exp_doc": str(fecha_exp_doc),
                            "tipo_doc": tipo_doc, "pais_emisor_doc": pais_emi, "nacionalidad": nac_rep,
                            "ciudadania": ciud_rep, "situacion_laboral": sit_lab, "ocupacion": ocupacion,
                            "estado_civil": estado_civil, "cantidad_hijos": cant_hijos, "pep": pep,
                            "genero": genero, "cargo_rep": cargo_rep, "empresa_rep": empresa_rep,
                            "rubro_rep": rubro_rep, "pais_emp_rep": pais_emp_rep, "prov_emp_rep": prov_emp_rep,
                            "ciud_emp_rep": ciud_emp_rep, "dir_emp_rep": dir_emp_rep, "tel_emp_rep": tel_emp_rep,
                            "email_emp_rep": email_emp_rep
                        })
                        st.session_state.pending_toast = "¡Excelente! Datos de la empresa listos. Vamos al siguiente paso 🚀"
                        st.session_state.step = 2
                        st.rerun()

        render_save_section()

    elif step == 2:
        st.header("2. Perfilamiento de Inversión 📊")
        with st.form("form_step_2"):
            st.info("Estas preguntas son exigidas por la regulación estadounidense (SEC).")
            
            opc_hor = ["Menos de 1 año", "1 - 3 años", "3 - 5 años", "5 - 10 años", "Más de 10 años"]
            horizonte = st.selectbox("1 - ¿Cuál es su horizonte de tiempo para esta inversión?", opc_hor, index=get_idx(opc_hor, "horizonte_tiempo", opc_hor[0]))
            
            opc_exp = ["Ninguna", "Limitada (1-3 años)", "Buena (3-5 años)", "Extensa (Más de 5 años)"]
            experiencia = st.selectbox("2 - Experiencia general en inversiones (Años)", opc_exp, index=get_idx(opc_exp, "experiencia", opc_exp[0]))
            
            # BLOQUE DE EXPERIENCIA ESPECIFICA
            st.markdown("##### Experiencia Específica de Inversiones")
            st.caption("Completar información contemplando a todos los titulares:")
            opc_nivel = ["Nula", "Limitada", "Promedio", "Alta"]
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                exp_acciones = st.selectbox("Acciones", opc_nivel, index=get_idx(opc_nivel, "exp_acciones", "Nula"))
                exp_fondos = st.selectbox("Fondos Mutuos", opc_nivel, index=get_idx(opc_nivel, "exp_fondos", "Nula"))
                exp_anual = st.selectbox("Anualidades", opc_nivel, index=get_idx(opc_nivel, "exp_anualidades", "Nula"))
            with col_e2:
                exp_opciones = st.selectbox("Opciones", opc_nivel, index=get_idx(opc_nivel, "exp_opciones", "Nula"))
                exp_alt = st.selectbox("Inversiones Alternativas", opc_nivel, index=get_idx(opc_nivel, "exp_alternativas", "Nula"))
            st.markdown("---")
            
            opc_porc = ["Menos del 10%", "10% - 25%", "25% - 50%", "Más del 50%"]
            porcentaje = st.selectbox("3 - ¿Qué porcentaje de sus activos totales líquidos representa esta inversión?", opc_porc, index=get_idx(opc_porc, "porcentaje_activos", opc_porc[0]))
            
            opc_obj = ["Preservación de capital", "Generación de ingresos", "Crecimiento moderado", "Crecimiento agresivo"]
            objetivos = st.selectbox("4 - Objetivos de inversión", opc_obj, index=get_idx(opc_obj, "objetivos_inversion", opc_obj[0]))
            
            opc_tol = ["Baja", "Media", "Alta"]
            tolerancia = st.selectbox("5 - ¿Cuál es su tolerancia al riesgo frente a caídas temporales del mercado?", opc_tol, index=get_idx(opc_tol, "tolerancia_riesgo", opc_tol[0]))
            
            # Nuevas preguntas (6, 7, 8)
            st.markdown("---")
            st.markdown("#### 6 - Elección de portafolio")
            st.markdown("El siguiente gráfico muestra la evolución del valor de tres portafolios de inversión hipotéticos, para un período de 4 años...")
            if os.path.exists("assets/grafico_6.png"):
                st.image("assets/grafico_6.png", caption="Gráfico Pregunta 6")
            else:
                st.info("💡 Por favor suba el archivo 'grafico_6.png' a la carpeta 'assets/' para ver este gráfico.")
            opc_p6 = ["Portafolio 1", "Portafolio 2", "Portafolio 3"]
            eleccion_portafolio = st.radio("¿En cuál de los portafolios se sentiría más cómodo?", opc_p6, index=get_idx(opc_p6, "eleccion_portafolio", "Portafolio 2"))

            st.markdown("---")
            st.markdown("#### 7 - Elección de rendimiento")
            st.markdown("La gráfica del cuadro que aparece a continuación muestra el rendimiento de cinco inversiones hipotéticas diferentes...")
            if os.path.exists("assets/grafico_7.png"):
                st.image("assets/grafico_7.png", caption="Gráfico Pregunta 7")
            else:
                st.info("💡 Por favor suba el archivo 'grafico_7.png' a la carpeta 'assets/' para ver este gráfico.")
            opc_p7 = ["Portafolio A", "Portafolio B", "Portafolio C", "Portafolio D", "Portafolio E"]
            eleccion_rendimiento = st.radio("¿Con cuál de estas inversiones se sentiría más cómodo?", opc_p7, index=get_idx(opc_p7, "eleccion_rendimiento", "Portafolio C"))

            st.markdown("---")
            st.markdown("#### 8 - Caída en portafolio")
            st.markdown("Considere el siguiente escenario: Imagine que durante los últimos 3 meses la bolsa de valores tuvo una pérdida del 25%, algunos fondos de su portafolio también están perdiendo 25% de su valor. ¿Qué haría usted?")
            opc_p8 = ["Vendería toda mi inversión", "Vendería parte de mi inversión", "No haría nada", "Compraría más"]
            caida_portafolio = st.radio("Seleccione una opción", opc_p8, index=get_idx(opc_p8, "caida_portafolio", "No haría nada"))

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("<- Volver"):
                    st.session_state.step = 1
                    st.rerun()
            with col2:
                if st.form_submit_button("Siguiente ->"):
                    data_update = {
                        "horizonte_tiempo": horizonte,
                        "experiencia": experiencia,
                        "porcentaje_activos": porcentaje,
                        "objetivos_inversion": objetivos,
                        "tolerancia_riesgo": tolerancia,
                        "eleccion_portafolio": eleccion_portafolio,
                        "eleccion_rendimiento": eleccion_rendimiento,
                        "caida_portafolio": caida_portafolio
                    }
                    if tipo_cuenta == "Persona Jurídica":
                        data_update.update({
                            "exp_acciones": exp_acciones,
                            "exp_fondos": exp_fondos,
                            "exp_anualidades": exp_anual,
                            "exp_opciones": exp_opciones,
                            "exp_alternativas": exp_alt
                        })
                    st.session_state.data.update(data_update)
                    st.session_state.pending_toast = "¡Perfil guardado! Estás avanzando rápido 🔥"
                    st.session_state.step = 3
                    st.rerun()

        render_save_section()

    elif step == 3:
        st.header("3. Origen de Fondos e Información Financiera 💰")
        with st.form("form_step_3"):
            if tipo_cuenta == "Persona Jurídica":
                opc_ing = ["Menos de 50.000", "50.000-99.999", "100.000-199.999", "200.000-499.999", "500.000-999.999", "1.000.000-2.499.999", "Más de 2.500.000"]
                opc_pat = ["Menos de 50.000", "50.000-99.999", "100.000-199.999", "200.000-499.999", "500.000-999.999", "1.000.000-2.499.999", "Más de 2.500.000"]
                opc_tiempo = ["Menos de un año", "1-3 años", "4-6 años", "7-9 años", "Más de 10 años"]
            else:
                opc_ing = ["Menos de 50.000", "50.000 - 100.000", "100.000 - 250.000", "Más de 250.000"]
                opc_pat = ["Menos de 100.000", "100.000 - 500.000", "500.000 - 1.000.000", "Más de 1.000.000"]
                opc_tiempo = ["Menos de 1 año", "1 - 3 años", "3 - 5 años", "Más de 10 años"]
                
            ingresos = st.selectbox("Ingresos Anuales Estimados (USD)", opc_ing, index=get_idx(opc_ing, "ingresos_anuales", opc_ing[0]))
            ingresos_exacto = st.text_input("Monto exacto de ingresos anuales (USD)", value=st.session_state.data.get("ingresos_exacto", ""))
            
            patrimonio = st.selectbox("Patrimonio Total Estimado (USD)", opc_pat, index=get_idx(opc_pat, "patrimonio_total", opc_pat[0]))
            
            activos_liq = st.selectbox("Activos Líquidos Estimados (USD)", opc_pat, index=get_idx(opc_pat, "activos_liquidos", opc_pat[0]))
            activos_exacto = st.text_input("Monto exacto de activos líquidos (USD)", value=st.session_state.data.get("activos_exacto", ""))
            
            opc_liq = ["Baja", "Media", "Alta"]
            nec_liq = st.selectbox("Necesidad de Liquidez", opc_liq, index=get_idx(opc_liq, "necesidad_liquidez", opc_liq[0]))
            
            opc_aportes = ["No", "Sí"]
            aportes = st.selectbox("¿Hará aportes adicionales planificados?", opc_aportes, index=get_idx(opc_aportes, "aportes_adicionales", opc_aportes[0]))
            
            tiempo_ret = st.selectbox("Tiempo esperado para realizar retiros", opc_tiempo, index=get_idx(opc_tiempo, "tiempo_retiros", opc_tiempo[0]))
            
            opc_ori = ["Ahorros / Salario", "Venta de propiedad", "Herencia", "Inversiones previas", "Venta de empresa"]
            origen = st.selectbox("Origen principal de los fondos", opc_ori, index=get_idx(opc_ori, "origen_fondos", opc_ori[0]))
            
            banco_origen = st.text_input("Banco origen de los fondos", value=st.session_state.data.get("banco_origen", ""))
            
            opc_pais = ["Chile", "Perú", "Colombia", "Estados Unidos", "Otro"]
            pais_ori = st.selectbox("País de origen de los fondos", opc_pais, index=get_idx(opc_pais, "pais_origen_fondos", "Chile"))
            
            monto = st.text_input("Monto aproximado de inversión inicial (USD)", value=st.session_state.data.get("monto_inversion", "50000"))
            
            opc_cont = ["Canalización de órdenes", "Gestión de portafolio"]
            tipo_contrato = st.selectbox("Tipo de contrato", opc_cont, index=get_idx(opc_cont, "tipo_contrato", opc_cont[0]), help="Puede mantener la opción por defecto y definirlo posteriormente con el asesor financiero.")
            st.caption("💡 *Sugerencia: Si no está seguro, puede dejarlo como está y definirlo posteriormente con su asesor.*")
            
            opc_pago = ["Transferencia", "Transferencia de activos", "ACAT", "ACH", "Otros"]
            metodo_pago = st.selectbox("Método de pago", opc_pago, index=get_idx(opc_pago, "metodo_pago", opc_pago[0]), help="Elija ACAT si planea realizar transferencia de activos.")
            st.caption("💡 *Sugerencia: Si planea realizar una transferencia de activos, seleccione la opción ACAT.*")
            
            st.markdown("---")
            st.subheader("Bancos Habituales")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                banco_pais = st.selectbox("País del Banco Habitual", opc_pais, index=get_idx(opc_pais, "banco_pais", "Chile"))
                banco_nombre = st.text_input("Nombre del Banco", value=st.session_state.data.get("banco_nombre", ""))
            with col_b2:
                banco_ciudad = st.text_input("Ciudad del Banco Habitual", value=st.session_state.data.get("banco_ciudad", ""))
                banco_sucursal = st.text_input("Sucursal", value=st.session_state.data.get("banco_sucursal", ""))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("<- Volver"):
                    st.session_state.step = 2
                    st.rerun()
            with col2:
                if st.form_submit_button("Siguiente ->"):
                    data_update = {
                        "ingresos_anuales": ingresos, "ingresos_exacto": ingresos_exacto, 
                        "patrimonio_total": patrimonio, "activos_liquidos": activos_liq, "activos_exacto": activos_exacto,
                        "necesidad_liquidez": nec_liq, "aportes_adicionales": aportes, "tiempo_retiros": tiempo_ret,
                        "origen_fondos": origen, "banco_origen": banco_origen, "pais_origen_fondos": pais_ori, 
                        "monto_inversion": monto, "tipo_contrato": tipo_contrato, "metodo_pago": metodo_pago,
                        "banco_pais": banco_pais, "banco_ciudad": banco_ciudad, "banco_nombre": banco_nombre, "banco_sucursal": banco_sucursal
                    }
                    st.session_state.data.update(data_update)
                    st.session_state.pending_toast = "¡Información financiera completada! Ya casi terminamos ✨"
                    st.session_state.step = 4
                    st.rerun()

        render_save_section()

    elif step == 4:
        st.header("4. Carga de Documentos Obligatorios 📄")
        st.write("Para procesar la transferencia de su cuenta (ACAT), requerimos los siguientes documentos.")
        
        with st.form("form_step_4"):
            doc1 = st.file_uploader("1. Cédula de Identidad (Ambos lados en un solo PDF/Imagen)", type=["pdf", "jpg", "png"])
            doc2 = st.file_uploader("2. Comprobante de Domicilio (Agua, Luz, Teléfono)", type=["pdf", "jpg", "png"])
            doc3 = st.file_uploader("3. Última Cartola de Inversiones (SURA/Pershing/Etc)", type=["pdf"])
            
            st.markdown("---")
            terminos = st.checkbox(
                "Autorizo el tratamiento de mis datos personales con la finalidad de gestionar mi enrolamiento en la plataforma Stonex y en los sistemas de AIVA, así como para permitir la correcta administración y monitoreo de mis inversiones. El tratamiento de mis datos se realizará únicamente mientras mantenga vigente mi relación con los servicios contratados o mientras resulte necesario para la adecuada gestión de mis inversiones. El responsable del tratamiento se obliga a utilizar mis datos exclusivamente para las finalidades señaladas y...", 
                value=False
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("<- Volver"):
                    st.session_state.step = 3
                    st.rerun()
            with col2:
                submitted = st.form_submit_button("✅ Finalizar y Enviar")
                if submitted:
                    if not terminos:
                        st.error("Debe autorizar el tratamiento de sus datos personales para continuar.")
                    else:
                        st.session_state.attachments = []
                        os.makedirs("data/uploads", exist_ok=True)
                        for doc in [doc1, doc2, doc3]:
                            if doc is not None:
                                # Usar absolute path para evitar que smtplib/MIME falle si cwd cambia
                                path = os.path.abspath(os.path.join("data/uploads", doc.name))
                                with open(path, "wb") as f:
                                    f.write(doc.getbuffer())
                                st.session_state.attachments.append({"filename": doc.name, "path": path})
                        st.session_state.pending_toast = "¡Solicitud completada! Preparando todo... 🎉"
                        st.session_state.step = 5
                        st.rerun()

        render_save_section()

    elif step == 5:
        st.success("¡Formulario Completado Exitosamente!")
        st.balloons()
        
        st.write("Generando su expediente y notificando a su asesor...")
        
        # Generar el Excel
        try:
            nombre_cliente = st.session_state.data.get('nombre_completo', 'Cliente')
            filename = f"Stonex_Apertura_{nombre_cliente.replace(' ', '_')}.xlsx"
            excel_path = generate_stonex_excel(st.session_state.data, output_filename=filename)
            
            # Enviar el correo
            with st.spinner("Enviando documentación de forma segura..."):
                attachments = st.session_state.get("attachments", [])
                exito = send_onboarding_email(nombre_cliente, excel_path, attachments=attachments)
                
            if exito:
                st.success("Toda su información ha sido enviada con éxito a su asesor. Ya puede cerrar esta ventana.")
            else:
                st.warning("Sus datos fueron procesados, pero hubo un problema enviando el correo de confirmación automático. Su asesor se comunicará a la brevedad.")
            
        except Exception as e:
            st.error(f"Hubo un error al procesar su solicitud: {str(e)}")
            print(f"Error en paso 5 público: {e}")

if __name__ == "__main__":
    main()
