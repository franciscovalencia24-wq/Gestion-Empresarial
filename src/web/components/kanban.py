import streamlit as st
import pandas as pd
import time
import re
import urllib.parse
from src.database.connection import engine
from sqlalchemy import text
from src.utils.kyc_email_generator import generar_comunicacion_kyc

def sanitize_email(raw_email: str) -> str:
    """Valida y limpia la dirección de correo electrónico del prospecto."""
    if not raw_email or pd.isna(raw_email):
        return ""
    email_clean = str(raw_email).strip()
    if email_clean.lower() in ["no registrado", "none", "nan", "null", "s/i", ""]:
        return ""
    if "@" not in email_clean:
        return ""
    return email_clean

def sanitize_whatsapp_phone(raw_phone: str) -> str:
    """
    Sanitiza y formatea el número telefónico para la API de WhatsApp (wa.me).
    Limpia símbolos, espacios y asegura el prefijo de país 56 para números de Chile.
    """
    if not raw_phone or pd.isna(raw_phone):
        return ""
    phone_clean = str(raw_phone).strip()
    if phone_clean.lower() in ["no registrado", "none", "nan", "null", "s/i", ""]:
        return ""
    digits = re.sub(r'\D', '', phone_clean)
    if not digits:
        return ""
    # Si tiene 9 dígitos y empieza con 9 (móvil chileno típico ej. 912345678), anteponer código país 56
    if len(digits) == 9 and digits.startswith('9'):
        digits = '56' + digits
    elif len(digits) == 8:
        digits = '56' + digits
    return digits

@st.dialog("Ficha Detallada del Lead")
def open_lead_dialog(row_dict):
    from src.utils.rut_utils import format_rut_miles
    st.markdown(f"### {row_dict.get('nombre', 'Sin Nombre')}")
    st.write(f"**RUT:** {format_rut_miles(row_dict.get('rut', ''))}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Teléfono:** {row_dict.get('telefono', 'No registrado')}")
        st.write(f"**Email:** {row_dict.get('email', 'No registrado')}")
    with col2:
        st.write(f"**Ciudad:** {row_dict.get('ciudad', 'No registrada')}")
        st.write(f"**Score de Liquidez:** {row_dict.get('score_liquidez', 0)}")

    st.markdown("---")
    lead_id = row_dict.get('id', 'temp')
    ice_key = f"icebreaker_lead_{lead_id}"

    st.markdown("#### 🤖 Prospección Asistida por IA")
    btn_label = "🔄 Regenerar Icebreaker" if ice_key in st.session_state else "🤖 Generar Mensaje de Contacto (Icebreaker)"
    
    if st.button(btn_label, use_container_width=True, key=f"btn_gen_{lead_id}"):
        with st.spinner("Redactando mensaje de alto impacto con IA..."):
            try:
                from src.intelligence.crm_automation import CRMAutomationEngine
                automation_engine = CRMAutomationEngine()
                nombre_cliente = row_dict.get('nombre', 'Estimado/a')
                
                # Extraer entidad administradora de las observaciones si existe
                obs = row_dict.get('observaciones', '')
                empresa_origen = "la industria financiera"
                if "Administrado por: " in str(obs):
                    partes = str(obs).split("Administrado por: ")
                    if len(partes) > 1:
                        empresa_origen = partes[1].split(" |")[0].strip()
                
                mensaje = automation_engine.generate_hnwi_icebreaker(nombre_cliente, empresa_origen)
                st.session_state[ice_key] = mensaje
            except Exception as e:
                st.error(f"❌ Error al conectar con la IA: {str(e)}")

    if ice_key in st.session_state and st.session_state[ice_key]:
        mensaje_base = st.session_state[ice_key]
        st.success("✅ Mensaje generado con éxito. Listo para copiar y contactar:")
        
        # Área de edición / personalización
        mensaje_final = st.text_area(
            "Icebreaker sugerido (editable antes de enviar):",
            value=mensaje_base,
            height=120,
            key=f"txt_ice_{lead_id}"
        )
        
        # 1. Copiar al Portapapeles (1 Clic mediante st.code nativo)
        st.markdown("**📋 Copiar al Portapapeles (1 clic en el icono superior derecho):**")
        st.code(mensaje_final, language="text")
        
        # 2. Acciones Rápidas de Contacto (Última Milla: Email y WhatsApp)
        st.markdown("**🚀 Acciones Rápidas de Contacto:**")
        
        email_clean = sanitize_email(row_dict.get('email', ''))
        phone_clean = sanitize_whatsapp_phone(row_dict.get('telefono', ''))
        
        encoded_icebreaker = urllib.parse.quote(mensaje_final)
        client_name = row_dict.get('nombre', 'Estimado/a')
        subject = f"Contacto Patrimonial | FV Asesorías - {client_name}"
        encoded_subject = urllib.parse.quote(subject)
        
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if email_clean:
                mailto_link = f"mailto:{email_clean}?subject={encoded_subject}&body={encoded_icebreaker}"
                st.markdown(f"""
                    <a href="{mailto_link}" target="_blank" style="text-decoration: none; display: block;">
                        <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); 
                                    color: white; padding: 12px 14px; border-radius: 8px; 
                                    text-align: center; font-weight: 600; font-size: 0.9em; 
                                    box-shadow: 0 2px 4px rgba(30,64,175,0.2); transition: all 0.2s ease;">
                            ✉️ Enviar por Email<br>
                            <span style="font-size: 0.8em; font-weight: normal; opacity: 0.95;">{email_clean}</span>
                        </div>
                    </a>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="background-color: #f8fafc; color: #94a3b8; padding: 12px 14px; 
                                border-radius: 8px; text-align: center; font-size: 0.85em; 
                                border: 1px dashed #cbd5e1;">
                        ✉️ <strong>Enviar por Email</strong><br>
                        <span style="font-size: 0.8em;">(Sin email registrado)</span>
                    </div>
                """, unsafe_allow_html=True)
                
        with col_act2:
            if phone_clean:
                whatsapp_link = f"https://wa.me/{phone_clean}?text={encoded_icebreaker}"
                st.markdown(f"""
                    <a href="{whatsapp_link}" target="_blank" style="text-decoration: none; display: block;">
                        <div style="background: linear-gradient(135deg, #15803d 0%, #22c55e 100%); 
                                    color: white; padding: 12px 14px; border-radius: 8px; 
                                    text-align: center; font-weight: 600; font-size: 0.9em; 
                                    box-shadow: 0 2px 4px rgba(21,128,61,0.2); transition: all 0.2s ease;">
                            💬 Enviar por WhatsApp<br>
                            <span style="font-size: 0.8em; font-weight: normal; opacity: 0.95;">+{phone_clean}</span>
                        </div>
                    </a>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="background-color: #f8fafc; color: #94a3b8; padding: 12px 14px; 
                                border-radius: 8px; text-align: center; font-size: 0.85em; 
                                border: 1px dashed #cbd5e1;">
                        💬 <strong>Enviar por WhatsApp</strong><br>
                        <span style="font-size: 0.8em;">(Sin teléfono registrado)</span>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    estado_actual = row_dict.get('status_contacto', 'Prospecto HNWI')
    opciones_estado = ["Prospecto HNWI", "Contacto Inicial", "Reunión Patrimonial", "Propuesta (Principal/APV)", "Cliente FV (Cerrado)", "Descartado"]
    
    idx = opciones_estado.index(estado_actual) if estado_actual in opciones_estado else 0
    nuevo_estado = st.selectbox("Cambiar Estado del Lead", opciones_estado, index=idx)
    
    if st.button("Guardar Cambios", use_container_width=True, type="primary"):
        try:
            with engine.connect() as con:
                con.execute(text("UPDATE prospects SET status_contacto = :s WHERE id = :id"), {"s": nuevo_estado, "id": row_dict['id']})
                con.commit()
            st.success("Estado actualizado con éxito.")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Error al actualizar: {e}")
            
    if nuevo_estado == "Cliente FV (Cerrado)":
        st.success("🎉 ¡Nuevo Cliente Ganado! Iniciando flujo de Onboarding...")
        with st.expander("Ver Borrador Correo KYC (Principal)"):
            correo_kyc, _ = generar_comunicacion_kyc(client_name=row_dict.get('nombre', ''))
            st.text_area("Copia este correo para el cliente:", value=correo_kyc, height=250)

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
            from src.utils.rut_utils import format_rut_miles
            st.markdown("#### Resultados de búsqueda")
            for _, row in search_df.iterrows():
                col_s1, col_s2, col_s3 = st.columns([3, 2, 1])
                col_s1.write(f"**{row['nombre']}** ({format_rut_miles(row['rut'])})")
                col_s2.write(f"📱 {row['telefono']} | 🏷️ {row.get('status_contacto', 'Pendiente')}")
                if col_s3.button("Abrir Ficha", key=f"search_btn_{row['id']}"):
                    open_lead_dialog(row.to_dict())
            st.markdown("---")
        else:
            st.warning("No se encontraron leads con ese criterio.")

    # --- MODO DE EMBUDO ---
    # Simplified to only Wealth Management pipeline
    query = """
        SELECT * FROM prospects 
        WHERE rut NOT LIKE 'DO%' 
    """
    with engine.connect() as con:
        df = pd.read_sql(query, con=con)

    # Definir Estados según el embudo patrimonial
    states = ["Prospecto HNWI", "Contacto Inicial", "Reunión Patrimonial", "Propuesta (Principal/APV)", "Cliente FV (Cerrado)"]
    
    # Simular distribución si no hay datos de estado reales o mapear antiguos
    if 'status_contacto' not in df.columns:
        df['status_contacto'] = "Prospecto HNWI"
    else:
        df['status_contacto'] = df['status_contacto'].fillna("Prospecto HNWI")
        # Mapeo de estados antiguos para asegurar retrocompatibilidad
        df.loc[df['status_contacto'].isin(['Nuevos Leads', 'Pendiente']), 'status_contacto'] = 'Prospecto HNWI'
        df.loc[df['status_contacto'].isin(['Contactado']), 'status_contacto'] = 'Contacto Inicial'
        df.loc[df['status_contacto'].isin(['Reunión Agendada', 'En Reunión']), 'status_contacto'] = 'Reunión Patrimonial'
        df.loc[df['status_contacto'].isin(['Negociación', 'Propuesta Enviada']), 'status_contacto'] = 'Propuesta (Principal/APV)'
        df.loc[df['status_contacto'].isin(['Cerrado', 'Cierre / Cliente', 'Venta Cruzada Cerrada']), 'status_contacto'] = 'Cliente FV (Cerrado)'

    cols = st.columns(len(states))

    for i, state in enumerate(states):
        with cols[i]:
            st.markdown(f"### {state}")
            state_prospects = df[df['status_contacto'] == state]
            st.caption(f"{len(state_prospects)} leads")
            
            for _, row in state_prospects.head(10).iterrows():
                with st.container():
                    score = row.get('score_liquidez', 0)
                    badge_class = "badge-hot" if score > 80 else "badge-new"
                    
                    origen = str(row.get('origen_info', 'Carga Manual'))
                    patrimonio = row.get('saldo_administrado', 0)
                    if pd.isna(patrimonio) or patrimonio == 0:
                        patrimonio_str = "S/I"
                    else:
                        patrimonio_str = f"${patrimonio:,.0f}"

                    st.markdown(f"""
                        <div class="kanban-card">
                            <div class="card-title">{str(row.get('nombre', 'Sin Nombre'))[:30]}</div>
                            <div class="card-meta">
                                🕵️ Origen: {origen}<br>
                                💰 Patrimonio: {patrimonio_str}<br>
                                <span class="badge {badge_class}">Score: {score}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Ver {row['id']}", help="Abre la ficha detallada de este prospecto.", key=f"btn_{row['id']}"):
                        open_lead_dialog(row.to_dict())

def main():
    render_kanban()

if __name__ == "__main__":
    main()
