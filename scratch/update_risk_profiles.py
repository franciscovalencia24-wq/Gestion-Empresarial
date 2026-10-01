import re

file_path = r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\web\client_management_ui.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'(?s)(riesgo_map = \{.*?\n                          \})(.*?)(elif perfil_final == "Agresivo":\s+st\.warning\(".*?\)?)'

replacement_code = r'''                          riesgo_map = {
                              "Depósito a Plazo": ("Muy conservador", 0.04),
                              "Cotización Obligatoria": ("Moderado", 0.06),
                              "APV-A": ("Muy conservador", 0.04),
                              "APV-B": ("Decidido", 0.08),
                              "APV con Póliza": ("Conservador", 0.05),
                              "Depósito Convenido (DC-R)": ("Moderado", 0.06),
                              "Depósito Convenido (DC-L)": ("Moderado", 0.06),
                              "Cuenta 2": ("Moderado", 0.06),
                              "Fondo Mutuo": ("Moderado", 0.06),
                              "Acciones": ("Agresivo", 0.12),
                              "Otro": ("Moderado", 0.06)
                          }
                          
                          total_inv = df_plot["Monto CLP"].sum()
                          roi_ponderado = 0.0
                          score_riesgo = 0.0
                          
                          perfil_score_map = {
                              "Muy conservador": 1,
                              "Conservador": 2,
                              "Cauteloso": 3,
                              "Moderado": 4,
                              "Decidido": 5,
                              "Agresivo": 6
                          }
                          
                          for _, row_inv in df_plot.iterrows():
                              tipo = row_inv.get("Tipo", "Otro")
                              monto = float(row_inv.get("Monto CLP", 0.0))
                              peso = monto / total_inv if total_inv > 0 else 0.0
                              perfil, ret_est = riesgo_map.get(tipo, ("Moderado", 0.06))
                              
                              roi_ponderado += peso * ret_est
                              score_riesgo += peso * perfil_score_map.get(perfil, 4)
                              
                          if score_riesgo < 1.5:
                              perfil_final = "Muy conservador (0% Renta variable)"
                          elif score_riesgo < 2.5:
                              perfil_final = "Conservador (10% Máxima exposición RV)"
                          elif score_riesgo < 3.5:
                              perfil_final = "Cauteloso (25% Máxima exposición RV)"
                          elif score_riesgo < 4.5:
                              perfil_final = "Moderado (50% Máxima exposición RV)"
                          elif score_riesgo < 5.5:
                              perfil_final = "Decidido (75% Máxima exposición RV)"
                          else:
                              perfil_final = "Agresivo (100% Máxima exposición RV)"
                          
                          col_r1, col_r2 = st.columns(2)
                          with col_r1:
                              st.metric("Perfil de Riesgo Estimado", perfil_final.split(" (")[0], help="Calculado en base a la ponderación de activos.")
                          with col_r2:
                              st.metric("TIR Histórica Esperada (ROI anual)", f"{roi_ponderado*100:.1f}%", help="Estimación conservadora basada en promedios históricos por tipo de activo.")
                          
                          if score_riesgo < 2.5 and total_inv > 100000000:
                              st.info("💡 **Oportunidad Altus:** El portafolio es muy conservador para su volumen patrimonial. Podría beneficiarse de instrumentos de mayor alfa o activos alternativos (Private Equity / Deuda Privada).")
                          elif score_riesgo >= 5.5:
                              st.warning("⚠️ **Alerta de Volatilidad:** El portafolio tiene alta exposición a renta variable. Se recomienda revisar horizontes de liquidez a corto plazo.")'''

# First check if the pattern matches
match = re.search(pattern, content)
if match:
    content = content.replace(match.group(0), replacement_code)
    print("Replaced!")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("Not found, falling back to read file to find the block")
