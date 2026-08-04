import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_main = False
for i, line in enumerate(lines):
    if line.startswith('def main():'):
        new_lines.append('def render_campaign_launcher():\n')
        in_main = True
    elif in_main and line.startswith('if __name__ == "__main__":'):
        in_main = False
        new_lines.append('''
def render_crm_kanban():
    st.subheader("📊 Embudo de Ventas (Pipeline)")
    st.markdown("Arrastra, gestiona y monitorea el estado de cada persona a la que le has escrito.")

    # Convertir antiguos "Contactado" a "Enviado"
    try:
        with engine.connect() as con:
            con.execute(text("UPDATE prospects SET status_contacto = 'Enviado' WHERE status_contacto = 'Contactado'"))
            con.commit()
    except Exception:
        pass

    import pandas as pd
    df = pd.read_sql("SELECT id, rut, nombre, status_contacto, observaciones, telefono, ciudad FROM prospects WHERE status_contacto NOT IN ('Pendiente', 'No Contactar')", con=engine)
    
    if df.empty:
        st.info("Aún no tienes prospectos en etapa de seguimiento. ¡Ve al Motor de Campañas y lanza tu primer envío!")
        return

    # Estandarizar
    estados_embudo = ["Enviado", "Respondió Positivo", "Reunión Agendada", "Reunión Realizada", "No Interesado", "Enfriado - Seguimiento Q3"]
    
    # UI Filters
    st.markdown("### 🔍 Buscador de Leads")
    col1, col2 = st.columns(2)
    with col1:
        search_txt = st.text_input("Buscar por Nombre o RUT...")
    with col2:
        filter_status = st.multiselect("Filtrar por Estado", estados_embudo, default=[])
        
    if search_txt:
        df = df[df['nombre'].str.contains(search_txt, case=False, na=False) | df['rut'].str.contains(search_txt, case=False, na=False)]
    if filter_status:
        df = df[df['status_contacto'].isin(filter_status)]

    st.markdown("---")
    
    # Editable Dataframe
    st.markdown('##### Tablero Interactivo (Los cambios se guardan en vivo)')
    
    edited_df = st.data_editor(
        df,
        column_config={
            "status_contacto": st.column_config.SelectboxColumn(
                "🏁 Estado CRM",
                options=estados_embudo,
                required=True,
                width="medium"
            ),
            "observaciones": st.column_config.TextColumn(
                "📝 Notas / Próx. Pasos",
                help="Anota aquí qué te contestó, a qué hora llamarlo, etc.",
                width="large"
            ),
            "id": None, # Hide ID
            "rut": "RUT",
            "nombre": "Nombre Prospecto",
            "telefono": "Celular",
            "ciudad": "Ciudad"
        },
        disabled=["rut", "nombre", "telefono", "ciudad"],
        hide_index=True,
        use_container_width=True,
        key="crm_editor"
    )

    if st.button("💾 Guardar Cambios del Embudo", type="primary"):
        with engine.connect() as con:
            for index, row in edited_df.iterrows():
                # Update BD
                original_row = df.iloc[index]
                if row['status_contacto'] != original_row['status_contacto'] or row['observaciones'] != original_row['observaciones']:
                    con.execute(text("UPDATE prospects SET status_contacto = :status, observaciones = :obs WHERE id = :pid"),
                                {"status": row['status_contacto'], "obs": row['observaciones'], "pid": int(row['id'])})
            con.commit()
        st.success("✅ Cambios de estado y notas sincronizados con la Base de Datos Histórica.")


def main():
    st.sidebar.title("🚀 Suite Comercial")
    nav = st.sidebar.radio("Navegación del Sistema", ["🎯 Motor de Campañas", "📊 Embudo CRM (Kanban)"])
    
    st.sidebar.markdown("---")
    
    if nav == "🎯 Motor de Campañas":
        render_campaign_launcher()
    else:
        render_crm_kanban()

''' + line)
    else:
        # Reemplazar "mark_contacted(prospect_db_id)" a mark_contacted pero enviando "Enviado"
        if "mark_contacted(prospect_db_id)" in line and in_main:
            new_lines.append(line.replace("mark_contacted(prospect_db_id)", "mark_contacted(prospect_db_id, status='Enviado')\n"))
        elif "st.title(\"🚀 Suite Comercial Asesor Senior\")" in line and in_main:
            new_lines.append(line.replace("st.title", "st.header"))
        else:
            new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
