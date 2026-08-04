import re

ui_path = 'src/web/client_management_ui.py'
with open(ui_path, 'r', encoding='utf-8') as f:
    content = f.read()

cap_rate_old = '"Rentabilidad S/Deuda (Cap Rate %)": st.column_config.NumberColumn("Cap Rate (%)", format="%.2f%%", disabled=True),'
cap_rate_new = '"Rentabilidad S/Deuda (Cap Rate %)": st.column_config.NumberColumn("Cap Rate (%)", format="%.2f%%", disabled=True, help="Rentabilidad de la propiedad asumiendo compra al contado.\\n\\nFórmula: (Ingreso Operativo Anual / Valor Comercial) * 100\\nObjetivo: Evaluar el rendimiento puro del activo inmobiliario sin considerar el apalancamiento bancario."),'

roe_old = '"Retorno C/Deuda (ROE %)": st.column_config.NumberColumn("ROE (%)", format="%.2f%%", disabled=True),'
roe_new = '"Retorno C/Deuda (ROE %)": st.column_config.NumberColumn("ROE (%)", format="%.2f%%", disabled=True, help="Retorno sobre el Patrimonio (Return on Equity).\\n\\nFórmula: (Flujo de Caja Anual / Patrimonio Inmovilizado) * 100\\nObjetivo: Medir la rentabilidad real de la porción que ya has pagado, maximizando el uso del apalancamiento."),'

flujo_old = '"Flujo Caja Anual (CLP)": st.column_config.NumberColumn("Flujo Caja Anual", format="$ %,d", disabled=True),'
flujo_new = '"Flujo Caja Anual (CLP)": st.column_config.NumberColumn("Flujo Caja Anual", format="$ %,d", disabled=True, help="Dinero real (liquidez) que produce la propiedad anualmente.\\n\\nFórmula: Ingresos por Arriendo - (Gastos Operativos + Dividendos Hipotecarios)\\nObjetivo: Conocer cuánto dinero líquido te deja (o te cuesta) mantener la propiedad al año."),'

retorno_old = '"Retorno Total (%)": st.column_config.NumberColumn("Retorno Total", format="%.2f%%", disabled=True),'
retorno_new = '"Retorno Total (%)": st.column_config.NumberColumn("Retorno Total", format="%.2f%%", disabled=True, help="Ganancia consolidada de la propiedad.\\n\\nFórmula: ROE (o Cap Rate si no hay deuda) + Plusvalía Esperada Anual\\nObjetivo: Visión completa de la creación de riqueza de la propiedad a través del tiempo."),'

content = content.replace(cap_rate_old, cap_rate_new)
content = content.replace(roe_old, roe_new)
content = content.replace(flujo_old, flujo_new)
content = content.replace(retorno_old, retorno_new)

with open(ui_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Tooltips added.")
