with open('src/web/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out_lines = []
skip_until = -1

for i, line in enumerate(lines):
    if i < skip_until:
        continue
        
    # 1. Add option to selectbox
    if 'sub_nav = st.sidebar.selectbox("Herramientas Anal' in line:
        out_lines.append(line)
        out_lines.append(lines[i+1]) # Landing de Analisis
        out_lines.append('              "Análisis Técnico y Fundamental",\n')
        skip_until = i + 2
        continue

    # 2. Add button in the UI
    if 'c2.button("🧑‍💼 Analista Macro"' in line or 'c2.button("YO? Analista Macro"' in line:
        out_lines.append(line)
        out_lines.append('              c1.button("📈 Análisis Técnico y Fundamental", use_container_width=True, on_click=set_subnav, args=("Análisis Técnico y Fundamental",))\n')
        continue
        
    # 3. Add handler
    if 'elif sub_nav == "Auditor de Portafolio":' in line:
        out_lines.append('          elif sub_nav == "Análisis Técnico y Fundamental":\n')
        out_lines.append('              from src.web.analysis_hub_ui import render_analysis_hub_ui\n')
        out_lines.append('              render_analysis_hub_ui()\n')
        out_lines.append(line)
        continue
        
    # 4. Remove unsafe_allow_html from Hub
    if 'st.markdown("""' in line and i+1 < len(lines) and "<div style='background: linear-gradient" in lines[i+1] and "Hub de An" in lines[i+2]:
        out_lines.append('              st.title("🎯 Hub de Análisis de Inversiones")\n')
        out_lines.append('              st.markdown("Selecciona qué aspecto del patrimonio deseas evaluar hoy.")\n')
        # Skip the next 5 lines which are the rest of the unsafe div
        skip_until = i + 6
        continue
        
    out_lines.append(line)

with open('src/web/app.py', 'w', encoding='utf-8') as f:
    f.writelines(out_lines)

print("Patch applied carefully by line!")
