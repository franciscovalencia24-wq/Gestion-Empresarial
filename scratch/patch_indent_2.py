with open('src/web/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 10 spaces to 8 spaces
text = text.replace('          elif sub_nav == "Análisis Técnico y Fundamental":', '        elif sub_nav == "Análisis Técnico y Fundamental":')
text = text.replace('              from src.web.analysis_hub_ui import render_analysis_hub_ui\n              render_analysis_hub_ui()', '            from src.web.analysis_hub_ui import render_analysis_hub_ui\n            render_analysis_hub_ui()')

with open('src/web/app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Indentation fixed again.")
