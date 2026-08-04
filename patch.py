import os

filepath = "src/web/cartolas_ui.py"

with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.startswith("import streamlit as st"):
        new_lines.append(line)
        new_lines.append("from src.intelligence.competitor_agent import CompetitorAgent\n")
    elif i >= 115 and i <= 250: # Lines col1, col2 to the end of the prospect logic (excluding finally: db.close())
        if line.strip() == "col1, col2 = st.columns([1, 2])":
            new_lines.append("        tab1, tab2 = st.tabs([\"📊 Análisis y Estrategia\", \"⚔️ Benchmarking Competencia\"])\n")
            new_lines.append("        with tab1:\n")
            new_lines.append("    " + line)
        else:
            if line.strip() == "":
                new_lines.append(line)
            else:
                new_lines.append("    " + line)
    else:
        new_lines.append(line)

# Insert tab2 logic before finally: db.close()
tab2_logic = """
        with tab2:
            st.subheader("⚔️ Benchmarking vs Competencia")
            st.info("Sube un folleto, PDF o imagen de un producto de la competencia (ej. Fondo Mutuo, APV) para generar un contra-argumento instantáneo.")
            
            comp_file = st.file_uploader("Subir Propuesta de Competencia (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"], key="comp_uploader")
            
            if comp_file and st.button("Analizar Competencia y Generar Objeciones", type="primary"):
                with st.spinner("Leyendo letras chicas y comparando con FV Asesorías..."):
                    try:
                        file_bytes = comp_file.getvalue()
                        mime_type = comp_file.type
                        agent = CompetitorAgent()
                        resultado_bench = agent.generate_counter_proposal(file_bytes, mime_type, prospect.nombre)
                        st.session_state[f"bench_{prospect.id}"] = resultado_bench
                    except Exception as e:
                        st.error(f"Error al analizar competencia: {str(e)}")
            
            if f"bench_{prospect.id}" in st.session_state:
                st.markdown(st.session_state[f"bench_{prospect.id}"])
"""

# Find the finally block to insert before it
for i in range(len(new_lines)-1, -1, -1):
    if "finally:" in new_lines[i]:
        new_lines.insert(i, tab2_logic)
        break

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Patch applied successfully.")
