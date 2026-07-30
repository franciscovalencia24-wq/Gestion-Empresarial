import streamlit as st
import time
from src.agent.mobile_chat_db import get_chat_history, clear_chat_history
from src.agent.mobile_agent_bridge import (
    process_user_mobile_message,
    execute_approved_command,
    reject_command,
    get_company_context_summary
)

def render_mobile_chat_ui():
    st.markdown("""
    <style>
        .chat-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 18px 24px;
            border-radius: 16px;
            border: 1px solid rgba(245, 158, 11, 0.4);
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-title {
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
            margin: 0;
        }
        .chat-status {
            font-size: 13px;
            color: #10b981;
            font-weight: 600;
            background: rgba(16, 185, 129, 0.15);
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }
        .user-bubble {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: #ffffff;
            padding: 14px 18px;
            border-radius: 18px 18px 2px 18px;
            margin: 8px 0 8px auto;
            max-width: 85%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            font-size: 15px;
            line-height: 1.4;
        }
        .agent-bubble {
            background: #1e293b;
            color: #f8fafc;
            padding: 16px 20px;
            border-radius: 18px 18px 18px 2px;
            margin: 8px auto 8px 0;
            max-width: 88%;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            font-size: 15px;
            line-height: 1.4;
        }
        .approval-card {
            background: rgba(15, 23, 42, 0.95);
            border: 2px solid #f59e0b;
            border-radius: 16px;
            padding: 18px;
            margin: 12px 0;
            box-shadow: 0 8px 24px rgba(245, 158, 11, 0.2);
        }
        .system-bubble {
            background: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
            padding: 10px 16px;
            border-radius: 12px;
            font-size: 13px;
            text-align: center;
            margin: 8px auto;
            border: 1px dashed rgba(245, 158, 11, 0.4);
        }
    </style>
    """, unsafe_allow_html=True)

    # 1. Header UI
    st.markdown("""
    <div class="chat-header">
        <div>
            <div class="chat-title">📱 Antigravity Remote Chat</div>
            <div style="color: #94a3b8; font-size: 13px;">Asistente Conversacional & Ejecutor Remoto</div>
        </div>
        <div class="chat-status">🟢 PC ONLINE & CONECTADA</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. PIN Authentication Guard
    if "remote_auth_ok" not in st.session_state:
        st.session_state["remote_auth_ok"] = False

    if not st.session_state["remote_auth_ok"]:
        st.warning("🔒 **Acceso Remoto Protegido**")
        pin = st.text_input("Ingresa tu PIN de Seguridad (ej. 2026):", type="password", key="remote_pin_input")
        if st.button("🔓 Desbloquear Chat Móvil", use_container_width=True):
            if pin in ["2026", "2024", "1234"]:
                st.session_state["remote_auth_ok"] = True
                st.success("¡PIN Correcto! Conectado a Antigravity.")
                st.rerun()
            else:
                st.error("PIN incorrecto.")
        return

    # 3. Sidebar Quick Info & Controls
    with st.sidebar:
        st.subheader("⚡ Accesos Rápidos de 1-Tap")
        if st.button("📊 Generar Infografía 4K", use_container_width=True):
            process_user_mobile_message("Generar Infografía 4K")
            st.rerun()
        if st.button("🔄 Sincronizar Excel de Gestión", use_container_width=True):
            process_user_mobile_message("Sincronizar Excel de Gestión")
            st.rerun()
        if st.button("📄 Generar Reporte PDF", use_container_width=True):
            process_user_mobile_message("Generar Reporte PDF")
            st.rerun()
        if st.button("☁️ Respaldo a Google Cloud", use_container_width=True):
            process_user_mobile_message("Respaldo a Google Cloud")
            st.rerun()

        st.divider()
        if st.button("🗑️ Limpiar Historial de Chat", use_container_width=True):
            clear_chat_history()
            st.success("Historial borrado.")
            st.rerun()

    # 4. Render Conversation History
    history = get_chat_history(limit=100)

    if not history:
        st.info("👋 **¡Bienvenido a Antigravity Remote!** Puedes preguntarme saldos, solicitar infografías, reportes PDF o dar instrucciones en lenguaje natural.")

    chat_container = st.container()

    with chat_container:
        for msg in history:
            sender = msg["sender"]
            text = msg["text"]
            msg_type = msg["msg_type"]
            msg_id = msg["id"]
            approval_status = msg["approval_status"]

            if sender == "user":
                st.markdown(f'<div class="user-bubble">👤 <b>Tú:</b><br/>{text}</div>', unsafe_allow_html=True)
            elif sender == "system":
                st.markdown(f'<div class="system-bubble">⚙️ {text}</div>', unsafe_allow_html=True)
            elif sender == "agent":
                if msg_type == "approval_request":
                    st.markdown(f"""
                    <div class="approval-card">
                        <div style="font-weight: 800; color: #f59e0b; font-size: 16px; margin-bottom: 8px;">
                            🛡️ Solicitud de Permiso de Ejecución
                        </div>
                        <div style="color: #cbd5e1; margin-bottom: 12px;">{text}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if approval_status == "PENDING":
                        col_acc, col_rej = st.columns(2)
                        with col_acc:
                            if st.button("✅ APROBAR EN PC", key=f"btn_acc_{msg_id}", use_container_width=True, type="primary"):
                                execute_approved_command(msg_id)
                                st.rerun()
                        with col_rej:
                            if st.button("❌ RECHAZAR", key=f"btn_rej_{msg_id}", use_container_width=True):
                                reject_command(msg_id)
                                st.rerun()
                    elif approval_status == "APPROVED":
                        st.success("✅ **ORDEN APROBADA:** Ejecutada en el computador.")
                    elif approval_status == "REJECTED":
                        st.error("🛑 **ORDEN RECHAZADA:** Cancelada por el usuario.")
                else:
                    st.markdown(f'<div class="agent-bubble">🤖 <b>Antigravity:</b><br/>{text}</div>', unsafe_allow_html=True)

    # 5. Input Bar at Bottom
    st.divider()
    with st.form(key="mobile_chat_form", clear_on_submit=True):
        col_txt, col_send = st.columns([5, 1])
        with col_txt:
            user_input = st.text_input(
                "Escribe tu consulta o instrucción para la PC:",
                placeholder="Ej: ¿Cuál es el saldo del banco? o Genera una infografía...",
                label_visibility="collapsed"
            )
        with col_send:
            submitted = st.form_submit_button("Enviar 📤", use_container_width=True)

        if submitted and user_input.strip():
            process_user_mobile_message(user_input.strip())
            st.rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="Antigravity Remote Chat", page_icon="📱", layout="wide")
    render_mobile_chat_ui()
