import os
import re

with open('src/web/analysis_hub_ui.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix "Último"
text = text.replace('ÚÚÚÚltimo Precio', 'Último Precio')

# 2. Format metrics
def replace_metric(match):
    full_str = match.group(0)
    if "precio_cierre" in full_str:
        return 'colA.metric("Último Precio", f"USD {float(summary[\'precio_cierre\']):,.2f}")'
    elif "rsi_14" in full_str:
        return 'colB.metric("RSI (14)", f"{float(summary[\'rsi_14\']):.2f}")'
    elif "pe_ratio" in full_str:
        return 'colX.metric("P/E Ratio", f"{float(sum_f.get(\'pe_ratio\', 0)):.2f}" if sum_f.get("pe_ratio") else "N/A")'
    elif "pb_ratio" in full_str:
        return 'colY.metric("P/B Ratio", f"{float(sum_f.get(\'pb_ratio\', 0)):.2f}" if sum_f.get("pb_ratio") else "N/A")'
    elif "free_cashflow" in full_str:
        return 'colZ.metric("Flujo de Caja Libre", f"USD {int(sum_f.get(\'free_cashflow\', 0)):,}" if sum_f.get("free_cashflow") else "N/A")'
    return full_str

text = re.sub(r'col[A-Z]\.metric\([^)]+\)', replace_metric, text)

# Update task status manually
with open('src/web/analysis_hub_ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("UI formatting applied")
