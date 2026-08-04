import re

with open('src/web/client_management_ui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_indent = False
omit_flag = ''

i = 0
while i < len(lines):
    line = lines[i]
    
    if 'with st.expander(' in line and '(2) Perfil' in line:
        new_lines.append(line)
        indent = len(line) - len(line.lstrip())
        inner_indent = ' ' * (indent + 4)
        new_lines.append(inner_indent + 'st.session_state[f\"omit_{rut}_sii\"] = st.checkbox(\"Omitir seccin\", value=st.session_state.get(f\"omit_{rut}_sii\", False), key=f\"cb_omit_{rut}_sii\")\n')
        new_lines.append(inner_indent + 'if st.session_state[f\"omit_{rut}_sii\"]:\n')
        new_lines.append(inner_indent + '    st.info(\" La seccin de Perfil Tributario fue omitida intencionalmente.\")\n')
        new_lines.append(inner_indent + 'else:\n')
        omit_flag = 'sii'
        skip_indent = True
        i += 1
        continue
        
    elif 'with st.expander(' in line and '(3) Cartera' in line:
        new_lines.append(line)
        indent = len(line) - len(line.lstrip())
        inner_indent = ' ' * (indent + 4)
        new_lines.append(inner_indent + 'st.session_state[f\"omit_{rut}_inmobiliaria\"] = st.checkbox(\"Omitir seccin\", value=st.session_state.get(f\"omit_{rut}_inmobiliaria\", False), key=f\"cb_omit_{rut}_inmobiliaria\")\n')
        new_lines.append(inner_indent + 'if st.session_state[f\"omit_{rut}_inmobiliaria\"]:\n')
        new_lines.append(inner_indent + '    st.info(\" La seccin de Cartera Inmobiliaria fue omitida intencionalmente.\")\n')
        new_lines.append(inner_indent + 'else:\n')
        omit_flag = 'inmobiliaria'
        skip_indent = True
        i += 1
        continue

    elif 'with st.expander(' in line and '(4) Pliza' in line:
        new_lines.append(line)
        indent = len(line) - len(line.lstrip())
        inner_indent = ' ' * (indent + 4)
        new_lines.append(inner_indent + 'st.session_state[f\"omit_{rut}_seguros\"] = st.checkbox(\"Omitir seccin\", value=st.session_state.get(f\"omit_{rut}_seguros\", False), key=f\"cb_omit_{rut}_seguros\")\n')
        new_lines.append(inner_indent + 'if st.session_state[f\"omit_{rut}_seguros\"]:\n')
        new_lines.append(inner_indent + '    st.info(\" La seccin de Seguros fue omitida intencionalmente.\")\n')
        new_lines.append(inner_indent + 'else:\n')
        omit_flag = 'seguros'
        skip_indent = True
        i += 1
        continue

    elif 'with st.expander(' in line and '(5) Mapa' in line:
        new_lines.append(line)
        indent = len(line) - len(line.lstrip())
        inner_indent = ' ' * (indent + 4)
        new_lines.append(inner_indent + 'st.session_state[f\"omit_{rut}_deudas\"] = st.checkbox(\"Omitir seccin\", value=st.session_state.get(f\"omit_{rut}_deudas\", False), key=f\"cb_omit_{rut}_deudas\")\n')
        new_lines.append(inner_indent + 'if st.session_state[f\"omit_{rut}_deudas\"]:\n')
        new_lines.append(inner_indent + '    st.info(\" La seccin de Deudas fue omitida intencionalmente.\")\n')
        new_lines.append(inner_indent + 'else:\n')
        omit_flag = 'deudas'
        skip_indent = True
        i += 1
        continue

    elif 'with st.expander(' in line and '(6) Inversiones' in line:
        new_lines.append(line)
        indent = len(line) - len(line.lstrip())
        inner_indent = ' ' * (indent + 4)
        new_lines.append(inner_indent + 'st.session_state[f\"omit_{rut}_inversiones\"] = st.checkbox(\"Omitir seccin\", value=st.session_state.get(f\"omit_{rut}_inversiones\", False), key=f\"cb_omit_{rut}_inversiones\")\n')
        new_lines.append(inner_indent + 'if st.session_state[f\"omit_{rut}_inversiones\"]:\n')
        new_lines.append(inner_indent + '    st.info(\" La seccin de Inversiones fue omitida intencionalmente.\")\n')
        new_lines.append(inner_indent + 'else:\n')
        omit_flag = 'inversiones'
        skip_indent = True
        i += 1
        continue

    elif 'with st.expander(' in line and '(7) Alertas' in line:
        # Reset flag
        omit_flag = ''
        skip_indent = False

    if omit_flag and not line.strip() == '':
        current_indent = len(line) - len(line.lstrip())
        # Check if the block ended
        if current_indent <= 12 and 'with st.expander' not in line: 
            pass # Keep indenting if inside the expander
    
    if omit_flag and not line.startswith(' '*12) and line.strip() != '':
        # We exited the expander somehow, maybe. But st.expander is at 12 indent.
        pass

    if omit_flag and line.strip() != '':
        new_lines.append('    ' + line)
    else:
        new_lines.append(line)
        
    i += 1

with open('src/web/client_management_ui.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Done')
