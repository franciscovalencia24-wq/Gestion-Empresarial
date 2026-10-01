import re

file_path = r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\web\client_management_ui.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'(?s)(st\.plotly_chart\(fig2, use_container_width=True\)\s+else:\s+st\.info\("Ingresa montos v.*?lidos en CLP para visualizar la distribuci.*?n\."\))'

replacement = r'''\1
                          
                          # [HITO 4] Cálculo de Rentabilidad y Perfil de Riesgo
                          st.markdown("##### 📈 Perfil de Riesgo y Asset Allocation")
                          riesgo_map = {
                              "Depósito a Plazo": ("Conservador", 0.05),
                              "Cotización Obligatoria": ("Moderado", 0.06),
                              "APV-A": ("Conservador", 0.05),
                              "APV-B": ("Moderado", 0.07),
                              "APV con Póliza": ("Conservador", 0.04),
                              "Depósito Convenido (DC-R)": ("Moderado", 0.06),
                              "Depósito Convenido (DC-L)": ("Moderado", 0.06),
                              "Cuenta 2": ("Moderado", 0.06),
                              "Fondo Mutuo": ("Moderado", 0.07),
                              "Acciones": ("Agresivo", 0.12),
                              "Otro": ("Moderado", 0.06)
                          }
                          
                          total_inv = df_plot["Monto CLP"].sum()
                          roi_ponderado = 0.0
                          score_riesgo = 0.0
                          
                          for _, row_inv in df_plot.iterrows():
                              tipo = row_inv.get("Tipo", "Otro")
                              monto = float(row_inv.get("Monto CLP", 0.0))
                              peso = monto / total_inv if total_inv > 0 else 0.0
                              perfil, ret_est = riesgo_map.get(tipo, ("Moderado", 0.06))
                              
                              roi_ponderado += peso * ret_est
                              if perfil == "Conservador": score_riesgo += peso * 1
                              elif perfil == "Moderado": score_riesgo += peso * 2
                              elif perfil == "Agresivo": score_riesgo += peso * 3
                              
                          perfil_final = "Conservador" if score_riesgo < 1.5 else "Moderado" if score_riesgo < 2.5 else "Agresivo"
                          
                          col_r1, col_r2 = st.columns(2)
                          with col_r1:
                              st.metric("Perfil de Riesgo Estimado", perfil_final, help="Calculado en base a la ponderación de activos.")
                          with col_r2:
                              st.metric("TIR Histórica Esperada (ROI anual)", f"{roi_ponderado*100:.1f}%", help="Estimación conservadora basada en promedios históricos por tipo de activo.")
                          
                          if perfil_final == "Conservador" and total_inv > 100000000:
                              st.info("💡 **Oportunidad Altus:** El portafolio es muy conservador para su volumen patrimonial. Podría beneficiarse de instrumentos de mayor alfa o activos alternativos (Private Equity / Deuda Privada).")
                          elif perfil_final == "Agresivo":
                              st.warning("⚠️ **Alerta de Volatilidad:** El portafolio tiene alta exposición a renta variable. Se recomienda revisar horizontes de liquidez a corto plazo.")
'''

content, count = re.subn(pattern, replacement, content)
print(f"Replaced Risk Profile Logic: {count}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
