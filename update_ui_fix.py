import re

with open('src/web/client_management_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the duplicated block outside try:
bad_block = '''                if "edited_inv" in locals():
                            from src.database.models import ClientPortfolio
                            db.query(ClientPortfolio).filter(ClientPortfolio.prospect_id == prospect.id).delete()
                            for _, row in edited_inv.iterrows():
                                def safe_float(val):
                                    try: return float(val) if pd.notna(val) else 0.0
                                    except: return 0.0
                                kwargs = {
                                    "prospect_id": prospect.id,
                                    "institucion": str(row.get("Institución", "")),
                                    "activo": str(row.get("Activo", "")),
                                    "tipo_activo": str(row.get("Tipo", "")),
                                    "monto_original": safe_float(row.get("Monto")),
                                    "moneda_original": str(row.get("Moneda", "CLP")),
                                    "monto_clp": safe_float(row.get("Monto (CLP)"))
                                }
                                db.add(ClientPortfolio(**kwargs))
                        
                        # --- PERSISTENCIA EN BASE DE DATOS REAL ---
                try:'''

if bad_block in content:
    content = content.replace(bad_block, "                # --- PERSISTENCIA EN BASE DE DATOS REAL ---\n                try:")
else:
    # try variations of spaces and newlines if bad_block fails
    print("Exact bad block not found. Trying regex.")
    content = re.sub(
        r'if "edited_inv" in locals\(\):\s*from src\.database\.models import ClientPortfolio\s*db\.query\(ClientPortfolio\)\.filter[^#]*# --- PERSISTENCIA EN BASE DE DATOS REAL ---',
        r'# --- PERSISTENCIA EN BASE DE DATOS REAL ---',
        content,
        flags=re.MULTILINE
    )

# Add it at the end of the prospect block
good_block = '''
                        # 7. Inversiones
                        if "edited_inv" in locals():
                            from src.database.models import ClientPortfolio
                            db.query(ClientPortfolio).filter(ClientPortfolio.prospect_id == prospect.id).delete()
                            for _, row in edited_inv.iterrows():
                                def safe_float(val):
                                    try: return float(val) if pd.notna(val) else 0.0
                                    except: return 0.0
                                kwargs = {
                                    "prospect_id": prospect.id,
                                    "institucion": str(row.get("Institución", "")),
                                    "activo": str(row.get("Activo", "")),
                                    "tipo_activo": str(row.get("Tipo", "")),
                                    "monto_original": safe_float(row.get("Monto")),
                                    "moneda_original": str(row.get("Moneda", "CLP")),
                                    "monto_clp": safe_float(row.get("Monto (CLP)"))
                                }
                                db.add(ClientPortfolio(**kwargs))
'''

# Find the place to insert it. "7. Inversiones" goes after "6. Sociedades" logic
if "# 7. Inversiones" not in content:
    content = re.sub(
        r'(porcentaje_utilidades=ut\n\s*\)\n\s*db\.add\(nueva_sociedad\))',
        r'\1' + good_block,
        content
    )

with open('src/web/client_management_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fix applied")
