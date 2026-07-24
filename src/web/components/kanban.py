import streamlit as st
import pandas as pd
from src.database.connection import engine
from sqlalchemy import text

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

    # Cargar prospectos
    with engine.connect() as con:
        df = pd.read_sql("SELECT * FROM prospects ORDER BY score_liquidez DESC LIMIT 100", con=con)

    # Definir Estados
    states = ["Pendiente", "Contactado", "En Reunión", "Propuesta Enviada", "Cierre / Cliente"]
    
    # Simular distribución si no hay datos de estado reales
    if 'status_contacto' not in df.columns:
        df['status_contacto'] = "Pendiente"

    cols = st.columns(len(states))

    for i, state in enumerate(states):
        with cols[i]:
            st.markdown(f"### {state}")
            state_prospects = df[df['status_contacto'] == state] if state != "Cierre / Cliente" else df[df['es_cliente'] == 1]
            
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
                        st.session_state.selected_lead = row['id']
                        st.info(f"Detalle del Lead: {row['nombre']}")

def main():
    render_kanban()

if __name__ == "__main__":
    main()
