import sys

def main():
    try:
        with open('src/web/client_management_ui.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Load variables
        target1 = "objetivo_val = getattr(prospect.profile, 'objetivo_inversion', \"Otro\") or \"Otro\""
        replace1 = target1 + "\n                        f_seguros_val = getattr(prospect.profile, 'fecha_ultima_act_seguros', None)\n                        f_deudas_val = getattr(prospect.profile, 'fecha_ultima_act_deudas', None)"
        content = content.replace(target1, replace1)
        
        # 2. Set into session state
        target2 = "st.session_state[f\"{rut}_objetivo\"] = objetivo_val"
        replace2 = target2 + "\n                if 'f_seguros_val' in locals():\n                    st.session_state[f\"{rut}_f_seguros\"] = f_seguros_val\n                    st.session_state[f\"{rut}_f_deudas\"] = f_deudas_val\n                else:\n                    st.session_state[f\"{rut}_f_seguros\"] = None\n                    st.session_state[f\"{rut}_f_deudas\"] = None"
        content = content.replace(target2, replace2)
        
        # 3. Add logic in Section 7
        target3 = "if not missing_herederos and not missing_propiedades and not missing_polizas:\n                    st.success(\"? **Perfil Completo:** Tienes toda la información necesaria para los análisis avanzados.\")"
        replace3 = target3 + "\n\n                f_seguros = st.session_state.get(f\"{rut}_f_seguros\")\n                if f_seguros and not st.session_state.get(f\"omit_{rut}_seguros\"):\n                    diff = (datetime.date.today() - f_seguros).days\n                    if diff > 180:\n                        st.warning(\"?? **Información de Seguros desactualizada:** Hace más de 6 meses que no se actualizan las pólizas.\")\n\n                f_deudas = st.session_state.get(f\"{rut}_f_deudas\")\n                if f_deudas and not st.session_state.get(f\"omit_{rut}_deudas\"):\n                    diff = (datetime.date.today() - f_deudas).days\n                    if diff > 90:\n                        st.warning(\"?? **Información de Deudas desactualizada:** Hace más de 3 meses que no se actualiza el mapa de deudas (CMF).\")"
        content = content.replace(target3, replace3)
        
        # 4. Save logic
        target4 = "prospect.profile.secciones_omitidas = json.dumps(omit_list)"
        replace4 = target4 + "\n                        prospect.profile.fecha_ultima_act_seguros = st.session_state.get(f\"{rut}_f_seguros\")\n                        prospect.profile.fecha_ultima_act_deudas = st.session_state.get(f\"{rut}_f_deudas\")"
        content = content.replace(target4, replace4)
        
        # 5. Update date on import Seguros
        target5 = "if f\"editor_polizas_{rut}\" in st.session_state:\n                                              del st.session_state[f\"editor_polizas_{rut}\"]"
        replace5 = target5 + "\n                                          st.session_state[f\"{rut}_f_seguros\"] = datetime.date.today()"
        content = content.replace(target5, replace5)
        
        # 6. Update date on import Deudas
        target6 = "if f\"editor_deudas_{rut}\" in st.session_state:\n                                            del st.session_state[f\"editor_deudas_{rut}\"]\n                                        st.rerun()"
        replace6 = target6.replace("st.rerun()", "st.session_state[f\"{rut}_f_deudas\"] = datetime.date.today()\n                                        st.rerun()")
        content = content.replace(target6, replace6)
        
        with open('src/web/client_management_ui.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Updated dates logic!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
