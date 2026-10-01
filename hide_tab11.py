with open('src/web/client_management_ui_new.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('        with st.expander("⚖️ (11) Gobierno Corporativo'):
        start_idx = i
        break

end_idx = -1
for i in range(start_idx + 1, len(lines)):
    if 'st.button("💾 Guardar y Actualizar Perfil Integral"' in lines[i]:
        end_idx = i
        break

for i in range(end_idx - 1, start_idx, -1):
    if lines[i].startswith('        st.markdown("---")'):
        end_idx = i
        break

lines[start_idx] = '        if not is_b2b:\n    ' + lines[start_idx]

for i in range(start_idx + 1, end_idx):
    if lines[i].strip():
        lines[i] = '    ' + lines[i]

with open('src/web/client_management_ui_new.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Patched tab 11 successfully')
