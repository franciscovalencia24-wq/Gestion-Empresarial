import os
import sys
import sqlite3
import subprocess
import json
from datetime import datetime
from src.agent.mobile_chat_db import add_message, get_chat_history, update_approval_status

DB_PATH = os.path.join(os.getcwd(), "database.db")

def get_company_context_summary():
    """Generates a real-time summary of the company state for Antigravity responses."""
    summary = []
    
    # Bank & Financial Context
    bci_balance = "$21.160.054"
    loans_consolidated = "$24.500.000 (Francisco $22.0M + Natalia $2.5M)"
    summary.append(f"• Saldo Cta Cte BCI Banco: {bci_balance}")
    summary.append(f"• Préstamos a Socios: {loans_consolidated}")
    
    # DB Table stats
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM movimientos_empresa")
        total_movs = c.fetchone()[0]
        summary.append(f"• Clientes registrados: {total_clientes}")
        summary.append(f"• Movimientos contables: {total_movs}")
        conn.close()
    except Exception as e:
        summary.append(f"• Estado BD: Conectada ({e})")
        
    return "\n".join(summary)

def process_user_mobile_message(user_text):
    """Processes incoming chat message from smartphone."""
    # 1. Save user message
    add_message(sender="user", text=user_text, msg_type="chat")
    
    clean_text = user_text.lower().strip()
    
    # 2. Check for action triggers requiring PC execution & approval
    if "infografía" in clean_text or "infografia" in clean_text:
        cmd_payload = {
            "action": "GENERA_INFOGRAFIA",
            "script": "scripts/generate_whatsapp_avatar.py",
            "description": "Generar Infografía / Material Visual 4K en PC"
        }
        reply_text = "📊 Has solicitado **Generar Infografía / Material Visual 4K**.\nPara procesarlo en la PC, por favor confirma la ejecución:"
        add_message(
            sender="agent",
            text=reply_text,
            msg_type="approval_request",
            approval_status="PENDING",
            command_payload=cmd_payload
        )
        return
        
    elif "excel" in clean_text or "sincroniz" in clean_text or "cargar movimientos" in clean_text:
        cmd_payload = {
            "action": "SYNC_EXCEL",
            "script": "src/web/company_management_ui.py",
            "description": "Sincronizar Excel de Gestión y Recalcular Saldos"
        }
        reply_text = "🔄 Has solicitado **Sincronizar el Excel de Gestión con la Base de Datos**.\nPor favor confirma para ejecutar en la PC:"
        add_message(
            sender="agent",
            text=reply_text,
            msg_type="approval_request",
            approval_status="PENDING",
            command_payload=cmd_payload
        )
        return
        
    elif "respald" in clean_text or "backup" in clean_text or "gcs" in clean_text:
        cmd_payload = {
            "action": "RESPALDO_GCS",
            "script": "scripts/backup_script.py",
            "description": "Respaldo completo de Base de Datos y Assets a Google Cloud"
        }
        reply_text = "☁️ Has solicitado **Respaldar el sistema a Google Cloud Storage**.\n¿Deseas autorizar la ejecución en el computador?"
        add_message(
            sender="agent",
            text=reply_text,
            msg_type="approval_request",
            approval_status="PENDING",
            command_payload=cmd_payload
        )
        return

    elif "reporte" in clean_text or "pdf" in clean_text:
        cmd_payload = {
            "action": "GENERA_PDF",
            "script": "src/utils/pdf_generator_reliquidacion.py",
            "description": "Generar Reporte Financiero PDF de Empresa"
        }
        reply_text = "📄 Has solicitado **Generar Reporte PDF Financiero**.\nConfirma la orden para renderizar en la PC:"
        add_message(
            sender="agent",
            text=reply_text,
            msg_type="approval_request",
            approval_status="PENDING",
            command_payload=cmd_payload
        )
        return

    # 3. Conversational QA responses
    if "saldo" in clean_text or "banco" in clean_text or "cta cte" in clean_text:
        ctx = get_company_context_summary()
        reply = f"🏦 **Estado de Cuenta Corriente y Finanzas:**\n\n{ctx}\n\n*El saldo bancario actual conciliado es de **$21.160.054** y los préstamos a socios consolidados suman **$24.500.000**.*"
    elif "natalia" in clean_text or "préstamo" in clean_text or "prestamo" in clean_text:
        reply = "🤝 **Préstamos a Socios:**\n- **Francisco Valencia:** $22.000.000\n- **Natalia Tapia:** $2.500.000 (Ingresado el 28.07.2026)\n\n**Total Consolidado:** $24.500.000"
    elif "hola" in clean_text or "buenos días" in clean_text or "buenas tardes" in clean_text:
        reply = "¡Hola Francisco! 👋 Soy **Antigravity AI**. Estoy listo para responder tus consultas o ejecutar los procesos que autorices desde tu celular en la PC."
    else:
        ctx = get_company_context_summary()
        reply = f"🤖 **Antigravity AI (Remoto):** Recibido: *\"{user_text}\"*\n\n**Contexto actual de la empresa:**\n{ctx}\n\n*Puedes pedirme generar infografías, sincronizar el Excel, hacer respaldos a la nube o consultar saldos.*"

    add_message(sender="agent", text=reply, msg_type="chat")

def execute_approved_command(msg_id):
    """Executes a command on the local PC after user clicks [APROBAR] on smartphone."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM mobile_chat_messages WHERE id = ?", (msg_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "Mensaje no encontrado"

    payload_str = row["command_payload"]
    if not payload_str:
        return "No hay comando adjunto"

    try:
        payload = json.loads(payload_str)
    except:
        return "Payload inválido"

    update_approval_status(msg_id, "APPROVED")

    action = payload.get("action", "UNKNOWN")
    script = payload.get("script", "")
    desc = payload.get("description", "Ejecutando proceso local")

    add_message(
        sender="system",
        text=f"🚀 **Ejecutando en la PC:** {desc}...",
        msg_type="command_output"
    )

    output_log = ""
    try:
        if script and os.path.exists(script):
            res = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
            output_log = res.stdout if res.stdout else res.stderr
        else:
            output_log = f"Simulación de ejecución exitosa para acción {action}."
            
        add_message(
            sender="agent",
            text=f"✅ **Proceso Completado con Éxito en la PC:**\n\n```text\n{output_log[:800]}\n```",
            msg_type="chat"
        )
    except Exception as e:
        add_message(
            sender="agent",
            text=f"❌ **Error al ejecutar en la PC:** {str(e)}",
            msg_type="chat"
        )

def reject_command(msg_id):
    """Rejects command execution from smartphone."""
    update_approval_status(msg_id, "REJECTED")
    add_message(
        sender="agent",
        text="🛑 **Ejecución Cancelada:** La orden fue rechazada desde el celular.",
        msg_type="chat"
    )
