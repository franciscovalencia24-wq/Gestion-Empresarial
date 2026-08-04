with open('src/web/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add "Análisis Técnico y Fundamental" to the selectbox
old_selectbox = """        sub_nav = st.sidebar.selectbox("Herramientas Analíticas", [
            "🏠 Landing de Análisis",
            "Auditor de Portafolio", 
            "Valoración de Portafolios", 
            "Asesor Patrimonial Senior (Omni)", 
            "Estrategia & Cartolas", 
            "Analista Macro (Consenso & Playbooks)",
            "Simuladores Cuantitativos"
        ], key="sub_nav_analisis")"""

new_selectbox = """        sub_nav = st.sidebar.selectbox("Herramientas Analíticas", [
            "🏠 Landing de Análisis",
            "Análisis Técnico y Fundamental",
            "Auditor de Portafolio", 
            "Valoración de Portafolios", 
            "Asesor Patrimonial Senior (Omni)", 
            "Estrategia & Cartolas", 
            "Analista Macro (Consenso & Playbooks)",
            "Simuladores Cuantitativos"
        ], key="sub_nav_analisis")"""

if old_selectbox in text:
    text = text.replace(old_selectbox, new_selectbox)
else:
    # Handle the fact that emojis might be encoded differently in the file
    import re
    # We find the selectbox list and insert "Análisis Técnico y Fundamental" after the first element
    match = re.search(r'(sub_nav = st\.sidebar\.selectbox\("Herramientas Anal[^\"]+", \[\s*"[^"]+",)', text)
    if match:
        text = text[:match.end()] + '\n            "Análisis Técnico y Fundamental",' + text[match.end():]

# 2. Add the button in Landing de Análisis
button_anchor = 'c2.button("🧑‍💼 Analista Macro"'
new_button = 'c2.button("🧑‍💼 Analista Macro", use_container_width=True, on_click=set_subnav, args=("Analista Macro (Consenso & Playbooks)",))\n            c1.button("📈 Análisis Técnico y Fundamental", use_container_width=True, on_click=set_subnav, args=("Análisis Técnico y Fundamental",))'

# We do a smart replace if button_anchor exists (ignoring emojis)
match = re.search(r'(c2\.button\("[^"]+Analista Macro".*?\))', text)
if match:
    text = text[:match.start()] + match.group(1) + '\n            c1.button("📈 Análisis Técnico y Fundamental", use_container_width=True, on_click=set_subnav, args=("Análisis Técnico y Fundamental",))' + text[match.end():]

# 3. Add the logic to render it
render_anchor = 'elif sub_nav == "Auditor de Portafolio":'
new_render = """elif sub_nav == "Análisis Técnico y Fundamental":
            from src.web.analysis_hub_ui import render_analysis_hub_ui
            render_analysis_hub_ui()
        elif sub_nav == "Auditor de Portafolio":"""

text = text.replace(render_anchor, new_render)


# 4. Remove the gradient divs that cause NotFoundError!
def remove_unsafe_div(match):
    html = match.group(1)
    # naive extraction of h1 and p
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html)
    p = re.search(r'<p[^>]*>(.*?)</p>', html)
    h1_text = h1.group(1) if h1 else ""
    p_text = p.group(1) if p else ""
    return f'st.title("{h1_text}")\n              st.markdown("{p_text}")'

text = re.sub(r'st\.markdown\(\"\"\"\s*<div style=\'background: linear-gradient[^\"]+ Hub de An[^\"]+</div>\s*\"\"\", unsafe_allow_html=True\)', remove_unsafe_div, text, flags=re.DOTALL)

with open('src/web/app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch applied successfully.")
