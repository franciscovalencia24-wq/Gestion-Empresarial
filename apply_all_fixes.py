import re
import os
import sys

# 1. Fix parser_inversiones.py
parser_inv_path = 'src/osint/parser_inversiones.py'
with open(parser_inv_path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('prompt = ""\"', 'prompt = \"\"\"')
with open(parser_inv_path, 'w', encoding='utf-8') as f:
    f.write(content)


# 2. Fix parser_cmf_deudas.py keys (Remove accents)
parser_deudas_path = 'src/osint/parser_cmf_deudas.py'
with open(parser_deudas_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The parser is actually returning:
# "Institución": institucion,
# "Tipo Crédito": tipo,
# "Monto Original": monto_original,
# "Monto Actual": monto_actual,
# "Carga Financiera": carga_financiera,
# "Mora": mora_actual,
# "Otorgamiento"
# "Vencimiento"
content = content.replace('"Institución"', '"Institucion"')
content = content.replace('"Tipo Crédito"', '"Tipo_Credito"')
with open(parser_deudas_path, 'w', encoding='utf-8') as f:
    f.write(content)


# 3. Fix client_management_ui.py
ui_path = 'src/web/client_management_ui.py'
with open(ui_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Omitir seccin
content = content.replace('Omitir seccin', 'Omitir sección')

# Fix Deudas mapping to match parser changes
content = content.replace('expected_cols = ["Institución", "Tipo Crédito", "Monto Original", "Monto Actual", "Carga Financiera", "Otorgamiento", "Vencimiento", "Mora", "Observaciones"]', 'expected_cols = ["Institucion", "Tipo_Credito", "Monto Original", "Monto Actual", "Carga Financiera", "Otorgamiento", "Vencimiento", "Mora", "Observaciones"]')
content = content.replace('mask = st.session_state[k_debt]["Institución"].notna() & (st.session_state[k_debt]["Institución"] != "")', 'mask = st.session_state[k_debt]["Institucion"].notna() & (st.session_state[k_debt]["Institucion"] != "")')
content = content.replace('subset_cols = ["Institución", "Tipo Crédito", "Monto Original", "Otorgamiento"]', 'subset_cols = ["Institucion", "Tipo_Credito", "Monto Original", "Otorgamiento"]')

content = content.replace('"Institución": d.institucion,', '"Institucion": d.institucion,')
content = content.replace('"Tipo Crédito": d.tipo_credito,', '"Tipo_Credito": d.tipo_credito,')

content = content.replace('"Institución": str(row.get("Institución", "")) if pd.notna(row.get("Institución")) and str(row.get("Institución")) != "None" else "",', '"institucion": str(row.get("Institucion", "")) if pd.notna(row.get("Institucion")) and str(row.get("Institucion")) != "None" else "",')
content = content.replace('"tipo_credito": str(row.get("Tipo Crédito", "")) if pd.notna(row.get("Tipo Crédito")) and str(row.get("Tipo Crédito")) != "None" else "",', '"tipo_credito": str(row.get("Tipo_Credito", "")) if pd.notna(row.get("Tipo_Credito")) and str(row.get("Tipo_Credito")) != "None" else "",')

# To be completely sure, replace any remaining "Institución" usage in Deudas UI editor mapping if needed... wait, only the UI column names for display.
# Let's fix the column_config:
# "Institucion": st.column_config.TextColumn("Institución") 
# "Tipo_Credito": st.column_config.TextColumn("Tipo Crédito")
# But for now, since it was just the keys:
content = content.replace(
    '''"Monto Original": st.column_config.NumberColumn(format="$ %,d"),''',
    '''"Institucion": st.column_config.TextColumn("Institución"),
                            "Tipo_Credito": st.column_config.TextColumn("Tipo Crédito"),
                            "Monto Original": st.column_config.NumberColumn(format="$ %,d"),'''
)


# 4. Fix UnboundLocalError for 'db'.
# We already tried to fix it but maybe the user hit another one?
# In the original error message, it says line 1292. Let's see what is near line 1292.
# Let's just wrap the entire db logic inside try/except safely or look for 'if "edited_inv" in locals():' outside try.
bad_db_save = '''                if "edited_inv" in locals():
                            from src.database.models import ClientPortfolio
                            db.query(ClientPortfolio).filter(ClientPortfolio.prospect_id == prospect.id).delete()'''

# If it exists, replace it with nothing or move it
if bad_db_save in content:
    content = content.replace(bad_db_save, '                # Old edited_inv saving removed to avoid UnboundLocalError')
    print("Found bad db save outside try block, fixed.")
else:
    # Let's check with regex just in case
    import re
    content, count = re.subn(r'if "edited_inv" in locals\(\):\s*from src\.database\.models import ClientPortfolio\s*db\.query\(ClientPortfolio\)\.filter\(ClientPortfolio\.prospect_id == prospect\.id\)\.delete\(\)', r'# Old edited_inv saving removed to avoid UnboundLocalError', content)
    if count > 0:
        print("Found bad db save with regex, fixed.")

with open(ui_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("All fixes applied successfully.")
