import os
import re

with open('src/web/analysis_hub_ui.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix the RSI decimals issue. It was: colB.metric("RSI (14)", f"{summary['rsi_14']}")
text = text.replace('colB.metric("RSI (14)", f"{summary[\'rsi_14\']}")', 'colB.metric("RSI (14)", f"{float(summary[\'rsi_14\']):.2f}")')
# Just in case there was a different form
text = text.replace('colB.metric("RSI (14)", f"{float(summary[\'rsi_14\'])}")', 'colB.metric("RSI (14)", f"{float(summary[\'rsi_14\']):.2f}")')

# 2. Fix the state wipe issue.
# Replace the Execute button
text = text.replace('if st.button("Ejecutar Análisis IA", type="primary", use_container_width=True):',
'''if st.button("Ejecutar Análisis IA", type="primary", use_container_width=True):
        st.session_state["run_analysis_hub"] = True

    if st.session_state.get("run_analysis_hub"):''')

# Now for the PDF button, we don't want it to refresh either. But wait, st.download_button doesn't refresh the page if we use it correctly!
# Let's replace the st.button("Generar Reporte PDF") with just generating the PDF bytes on the fly, or using a form.
# Actually, if we use session state for run_analysis_hub, the screen STAYS ON when the user clicks the PDF button!
# The PDF button is: `if st.button("📄 Generar Reporte PDF (Análisis Integral)", type="primary"):`
# If they click it, the page reruns. BUT because `st.session_state["run_analysis_hub"]` is True, it will RE-RUN the analysis. Which is acceptable (takes maybe 2-3 seconds).
# Or we can just use st.download_button directly if we generate the PDF bytes inside the analysis block.
# I'll let it re-run the analysis.

with open('src/web/analysis_hub_ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Applied fix")
