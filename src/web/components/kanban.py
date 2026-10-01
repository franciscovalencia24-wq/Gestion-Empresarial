import streamlit as st
import pandas as pd
import time
from src.database.connection import engine
from sqlalchemy import text

@st.dialog("Ficha Detallada del Lead")
def open_lead_dialog(row_dict):
    st.markdown(f"### {row_dict.get('nombre', 'Sin Nombre')}")
    st.write(f"**RUT:** {row_dict.get('rut', '')}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Teléfono:** {row_dict.get('telefono', 'No registrado')}")
        st.write(f"**Email:** {row_dict.get('email', 'No registrado')}")
    with col2:
        st.write(f"**Ciudad:** {row_dict.get('ciudad', 'No registrada')}")
        st.write(f"**Score de Liquidez:** {row_dict.get('score_liquidez', 0)}")

    estado_actual = row_dict.get('status_contacto', 'Pendiente')
    opciones_estado = ["Pendiente", "Contactado", "En Reunión", "Propuesta Enviada", "Cierre / Cliente", "Pendiente (Cross-Sell)", "Venta Cruzada Cerrada", "Descartado (Teléfono Equivocado)", "Descartado"]
    
    idx = opciones_estado.index(estado_actual) if estado_actual in opciones_estado else 0
    nuevo_estado = st.selectbox("Cambiar Estado del Lead", opciones_estado, index=idx)
    
    if st.button("Guardar Cambios", width="stretch", type="primary"):
        try:
            with engine.connect() as con:
                con.execute(text("UPDATE prospects SET status_contacto = :s WHERE id = :id"), {"s": nuevo_estado, "id": row_dict['id']})
                con.commit()
            st.success("Estado actualizado con éxito.")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Error al actualizar: {e}")

def render_kanban():
    st.markdown("""
        <style>
        .kanban-board {
            display: flex;
            gap: 20px;
            overflow-x: auto;
            padding: 20px 0;
        }
        .kanban-column {
            background-color: #f1f5f9;
            border-radius: 12px;
            min-width: 300px;
            max-width: 300px;
            padding: 15px;
            border: 1px solid #e2e8f0;
        }
        .kanban-header {
            font-weight: 800;
            font-size: 1.1em;
            color: #1e293b;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .kanban-card {
            background: white;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid #00B140;
            cursor: pointer;
            transition: transform 0.1s;
        }
        .kanban-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card-title {
            font-weight: 700;
            color: #334155;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .card-meta {
            font-size: 0.75em;
            color: #64748b;
        }
        .badge {
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 0.7em;
            font-weight: 600;
        }
        .badge-new { background: #dcfce7; color: #166534; }
        .badge-hot { background: #fee2e2; color: #991b1b; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📊 Embudo CRM Patrimonial")
    st.write("Gestión visual de oportunidades y pipeline de clientes de alto patrimonio.")

    search_query = st.text_input("🔍 Buscar lead por Teléfono, Nombre o RUT", placeholder="Ej. +56912345678 o Juan Pérez")
    if search_query:
        with engine.connect() as con:
            search_df = pd.read_sql(f"SELECT * FROM prospects WHERE telefono LIKE '%%{search_query}%%' OR nombre LIKE '%%{search_query}%%' OR rut LIKE '%%{search_query}%%' LIMIT 10", con=con)
        if not search_df.empty:
            st.markdown("#### Resultados de búsqueda")
            for _, row in search_df.iterrows():
                col_s1, col_s2, col_s3 = st.columns([3, 2, 1])
                col_s1.write(f"**{row['nombre']}** ({row['rut']})")
                col_s2.write(f"📱 {row['telefono']} | 🏷️ {row.get('status_contacto', 'Pendiente')}")
                if col_s3.button("Abrir Ficha", key=f"search_btn_{row['id']}"):
                    open_lead_dialog(row.to_dict())
            st.markdown("---")
        else:
            st.warning("No se encontraron leads con ese criterio.")

    # --- MODO DE EMBUDO ---
    modo_kanban = st.radio("🎯 Selecciona el Embudo a visualizar:", 
                        ["Prospección de Nuevos Clientes", "Fidelización de Clientes Actuales ⭐"], horizontal=True)
    is_fidelizacion = "Fidelización" in modo_kanban
    cliente_filter = 1 if is_fidelizacion else 0

    # Cargar prospectos (Ocultando registros del Diario Oficial y filtrando por tipo de cliente)
    estados_activos = ["Contactado", "En Reunión", "Propuesta Enviada", "Cierre / Cliente", "Venta Cruzada Cerrada"]
    estados_str = "', '".join(estados_activos)
    query = f"""
        SELECT * FROM prospects 
        WHERE rut NOT LIKE 'DO%' 
        AND es_cliente = {cliente_filter} 
        AND status_contacto IN ('{estados_str}')
        UNION ALL
        SELECT * FROM (
            SELECT * FROM prospects 
            WHERE (rut NOT LIKE 'DO%' OR rut IS NULL)
            AND es_cliente = {cliente_filter} 
            AND (status_contacto NOT IN ('{estados_str}') OR status_contacto IS NULL)
            ORDER BY score_liquidez DESC 
            LIMIT 100
        )
    """
    with engine.connect() as con:
        df = pd.read_sql(query, con=con)

    # Definir Estados según el embudo
    if is_fidelizacion:
        states = ["Pendiente (Cross-Sell)", "Contactado", "En Reunión", "Propuesta Enviada", "Venta Cruzada Cerrada"]
    else:
        states = ["Pendiente", "Contactado", "En Reunión", "Propuesta Enviada", "Cierre / Cliente"]
    
    # Simular distribución si no hay datos de estado reales
    if 'status_contacto' not in df.columns:
        df['status_contacto'] = "Pendiente"

    cols = st.columns(len(states))

    for i, state in enumerate(states):
        with cols[i]:
            st.markdown(f"### {state}")
            
            if not is_fidelizacion and state == "Cierre / Cliente":
                # En prospección, los que ya son clientes van al final
                state_prospects = df[(df['status_contacto'] == state) | (df['es_cliente'] == 1)]
            elif is_fidelizacion and state == "Pendiente (Cross-Sell)":
                # En fidelización, los clientes cuyo estado quedó en "Cierre" de una campaña anterior, vuelven a empezar como Pendientes
                state_prospects = df[(df['status_contacto'] == state) | (df['status_contacto'] == 'Pendiente') | (df['status_contacto'] == 'Cierre / Cliente') | (df['status_contacto'].isna())]
            else:
                state_prospects = df[df['status_contacto'] == state]
                
            st.caption(f"{len(state_prospects)} leads")
            
            for _, row in state_prospects.head(10).iterrows():
                with st.container():
                    score = row.get('score_liquidez', 0)
                    badge_class = "badge-hot" if score > 80 else "badge-new"
                    st.markdown(f"""
                        <div class="kanban-card">
                            <div class="card-title">{row['nombre'][:30]}...</div>
                            <div class="card-meta">
                                🆔 {row['rut']}<br>
                                <span class="badge {badge_class}">Score: {score}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Ver {row['id']}", help="Abre la ficha detallada de este prospecto o cliente.", key=f"btn_{row['id']}"):
                        open_lead_dialog(row.to_dict())

def main():
    render_kanban()

if __name__ == "__main__":
    main()
