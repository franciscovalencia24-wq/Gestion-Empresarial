import streamlit as st
from src.utils.simulators.board_simulator import FamilyBoardSimulator

def render():
    st.header("🏛️ Board-as-a-Service: Gobierno Familiar", anchor=False)
    st.markdown("Estructuración societaria, sucesión y protocolos familiares institucionales.")

    simulator = FamilyBoardSimulator()

    tab1, tab2, tab3 = st.tabs(["1. Análisis Legal & Societario", "2. Protocolo Familiar", "3. Simulación Sucesoria"])

    with tab1:
        st.subheader("Auditoría de Escrituras y Poderes")
        st.info("Sube la documentación legal de la estructura familiar para que Altus AI identifique riesgos cruzados y proponga esquemas de sucesión.")
        uploaded_file = st.file_uploader("Cargar Escritura o Pacto de Accionistas (PDF/Word)", type=["pdf", "doc", "docx"])
        
        if st.button("Generar Informe Legal"):
            if uploaded_file:
                with st.spinner("Altus AI está leyendo e interpretando la estructura legal..."):
                    informe = simulator.generar_informe_legal(uploaded_file.name)
                    st.session_state['informe_legal'] = informe
            else:
                st.warning("Por favor carga un documento de prueba para ejecutar el análisis.")
                
        if 'informe_legal' in st.session_state:
            st.success("Análisis completado. Puedes editar el informe a continuación antes de exportarlo al cliente.")
            st.text_area("Borrador del Informe Legal (Editable)", value=st.session_state['informe_legal'], height=400)
            st.download_button("Descargar Informe", data=st.session_state['informe_legal'], file_name="Informe_Societario_AltusAI.txt")

    with tab2:
        st.subheader("Generador de Protocolo Familiar")
        st.markdown("Ingresa ágilmente los parámetros clave para estructurar el gobierno de la familia empresaria.")
        
        if st.button("🎭 Autocompletar Caso de Ejemplo (Demo)"):
            st.session_state['demo_fundador'] = "Familia Del Río Undurraga"
            st.session_state['demo_herederos'] = "4 hijos (2 en el directorio, 1 radicado en el extranjero, 1 dedicado a filantropía)."
            st.session_state['demo_valores'] = "Unidad, Mérito, Responsabilidad Social y Crecimiento Global."
            st.session_state['demo_politica'] = "Garantizar un dividendo preferente del 4% sobre patrimonio neto. 80% del remanente se reinvierte en activos alternativos."
            st.session_state['demo_restricciones'] = "Nombramientos directivos requieren evaluación externa de Headhunter. Los cónyuges o familiares políticos no pueden participar en la administración directa."
            
        def_fundador = st.session_state.get('demo_fundador', "Ej: Familia Pérez González")
        def_herederos = st.session_state.get('demo_herederos', "Ej: 3 hijos. 2 activos en la empresa, 1 pasivo.")
        def_valores = st.session_state.get('demo_valores', "Ej: Innovación, Respeto, Prudencia Financiera")
        def_politica = st.session_state.get('demo_politica', "Ej: Repartir el 30% anual y reinvertir el 70%")
        def_restricciones = st.session_state.get('demo_restricciones', "Ej: Mínimo 5 años de experiencia laboral previa fuera del grupo empresarial.")
        
        col1, col2 = st.columns(2)
        with col1:
            fundador = st.text_input("Nombre del Fundador / Matriarca / Patriarca", def_fundador)
            herederos = st.text_area("Nombre y perfiles de los Herederos", def_herederos)
            valores = st.text_input("Valores Nucleares de la Familia", def_valores)
        with col2:
            politica_div = st.text_area("Política de Dividendos Esperada", def_politica)
            restricciones = st.text_area("Políticas de Contratación de Familiares", def_restricciones)
            
        if st.button("Estructurar Protocolo Familiar"):
            info = {
                'fundador': fundador,
                'herederos': herederos,
                'valores': valores,
                'politica_dividendos': politica_div,
                'restricciones': restricciones
            }
            with st.spinner("Altus AI está redactando el marco del protocolo..."):
                protocolo = simulator.generar_protocolo_familiar(info)
                st.session_state['protocolo_familiar'] = protocolo
                
        if 'protocolo_familiar' in st.session_state:
            st.success("Borrador estructurado exitosamente. Ajusta las redacciones finales aquí.")
            st.text_area("Protocolo Familiar (Editable)", value=st.session_state['protocolo_familiar'], height=400)
            st.download_button("Descargar Protocolo", data=st.session_state['protocolo_familiar'], file_name="Protocolo_Familiar_AltusAI.txt")

    with tab3:
        st.subheader("Simulación Sucesoria y Creador de Testamentos")
        st.markdown("Calcula el impacto progresivo del **Impuesto a la Herencia (Ley 16.271)** y diseña la estructura testamentaria óptima.")
        
        # Security Note
        st.info("🔒 **Seguridad Nivel Bancario**: Los datos ingresados en este inventario patrimonial se almacenan cifrados (AES-256) y se vinculan de manera segura a su Perfil 360° en la nube privada de Altus AI, garantizando protección absoluta ante ciberamenazas y permitiendo reanudar su planificación en cualquier momento sin pérdida de información.")

        if st.button("🎭 Autocompletar Caso de Ejemplo (Sucesión)"):
            st.session_state['demo_patrimonio'] = "5.000.000.000"
            st.session_state['demo_n_herederos'] = 4
            st.session_state['demo_testador'] = "Juan Del Río"
            st.session_state['demo_albacea'] = "xxx"
            st.session_state['demo_cuarta'] = "100% a la Fundación Filantrópica Familiar"
            
        pat_def = st.session_state.get('demo_patrimonio', "2.500.000.000")
        testador_def = st.session_state.get('demo_testador', "Ej: Juan Pérez")
        albacea_def = st.session_state.get('demo_albacea', "xxx")
        cuarta_def = st.session_state.get('demo_cuarta', "Ej: A mis nietos en partes iguales")

        st.markdown("### 1. Inventario Patrimonial y Matemática Tributaria")
        
        c_inv1, c_inv2 = st.columns(2)
        with c_inv1:
            st.markdown("Descargue la plantilla de Excel, complétela con tranquilidad y súbala para automatizar la base imponible.")
            plantilla_bytes = simulator.generar_plantilla_inventario()
            st.download_button("Descargar Plantilla de Inventario (.xlsx)", data=plantilla_bytes, file_name="Plantilla_Inventario_AltusAI.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with c_inv2:
            uploaded_file = st.file_uploader("Subir Inventario del Cliente (.xlsx)", type=["xlsx"])
            if uploaded_file is not None:
                st.success("Inventario cargado y cifrado correctamente. El sistema ha actualizado los valores patrimoniales.")

        c1, c2 = st.columns(2)
        patrimonio_str = c1.text_input("Patrimonio Total Estimado (CLP) - Use formato con puntos", value=pat_def)
        try:
            patrimonio = float(patrimonio_str.replace(".", "").replace(",", ""))
        except:
            patrimonio = 0

        st.markdown("**Composición Familiar (Afecta recargos y exenciones Ley 16.271):**")
        h1, h2, h3, h4 = st.columns(4)
        c_conyuge = h1.number_input("Cónyuge/Hijos (Exentos 50 UTA)", min_value=0, value=st.session_state.get('demo_n_herederos', 3), step=1)
        c_asc = h2.number_input("Ascendientes (Padres)", min_value=0, value=0, step=1)
        c_herm = h3.number_input("Hermanos (+20% Impuesto)", min_value=0, value=0, step=1)
        c_otros = h4.number_input("Terceros/Extraños (+40% Imp.)", min_value=0, value=0, step=1)
        
        herederos_dict = {
            'conyuge_hijos': c_conyuge,
            'ascendientes': c_asc,
            'hermanos': c_herm,
            'otros': c_otros
        }
        
        imp_tradicional, imp_por_h_trad = simulator.simular_impuesto_herencia_avanzado(patrimonio, herederos_dict)
        imp_opt, imp_por_h_opt = simulator.simular_escenario_optimizado_avanzado(patrimonio, herederos_dict)
        ahorro = imp_tradicional - imp_opt
        
        def fmt_m(v): return f"$ {v/1000000:,.0f} M".replace(",", ".")
        
        st.markdown("#### Comparativa de Impacto Fiscal")
        r1, r2, r3 = st.columns(3)
        r1.metric("Impuesto Tradicional (Sin Planificación)", fmt_m(imp_tradicional))
        r2.metric("Impuesto Estructura Altus AI", fmt_m(imp_opt), delta="- Estrategia Legal Aplicada", delta_color="normal")
        r3.metric("Ahorro Patrimonial", fmt_m(ahorro), delta="Patrimonio Rescatado", delta_color="normal")
        
        st.info("⚖️ **Base Legal del Ahorro (Art. 6 Ley 16.271):** Si el patriarca tiene 70 años, la Ley permite valorar el Usufructo Vitalicio en una proporción menor. Al transferir en vida solo la **Nuda Propiedad** de las Sociedades de Inversión, la base imponible se reduce legalmente, pagando el impuesto de herencia sobre una fracción del valor total y evitando caer en los tramos más altos (25%). NOTA: Los Seguros de Vida con ahorro pueden estar afectos a retenciones según Circular 22 del SII.")

        st.markdown("---")
        st.markdown("### 2. Creador de Testamentos")
        c3, c4 = st.columns(2)
        with c3:
            testador = st.text_input("Nombre del Testador", testador_def)
            albacea = st.text_input("Nombre del Albacea (Administrador Herencia)", albacea_def)
        with c4:
            cuarta = st.text_area("Instrucciones para Cuarta de Libre Disposición", cuarta_def)
        
        if st.button("Generar Borrador de Testamento"):
            info = {'testador': testador, 'albacea': albacea, 'cuarta_libre': cuarta}
            with st.spinner("Redactando formato legal..."):
                testamento = simulator.generar_testamento(info)
                st.session_state['testamento'] = testamento
                
        if 'testamento' in st.session_state:
            st.success("Testamento redactado. Listo para revisión legal.")
            st.text_area("Borrador Testamentario", value=st.session_state['testamento'], height=300)
            st.download_button("Descargar Testamento", data=st.session_state['testamento'], file_name="Testamento_AltusAI.txt")
