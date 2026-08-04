import re

with open(r'backups\temp_restore\src\web\analysis_hub_ui.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the specific div that causes NotFoundError with a simpler title.
text = re.sub(
    r'st\.markdown\(\"\"\"\s*<div style=\'background: linear-gradient.*?</div>\s*\"\"\", unsafe_allow_html=True\)',
    'st.title("🎯 Análisis Técnico y Fundamental (IA)")\n    st.markdown("Evaluación Integral con agentes cuantitativos de Altus AI.")',
    text,
    flags=re.DOTALL
)

with open(r'src\web\analysis_hub_ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('File restored and patched safely.')
