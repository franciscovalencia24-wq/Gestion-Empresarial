import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def send_onboarding_email(cliente_nombre, excel_filepath, attachments=None):
    """
    Envía un correo con el Excel adjunto y los documentos.
    Para que funcione en producción, es necesario definir las variables de entorno o Secrets en Streamlit:
    SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD.
    """
    # Streamlit Cloud usa st.secrets preferentemente
    try:
        import streamlit as st
        smtp_server = os.environ.get("SMTP_SERVER") or st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT") or st.secrets.get("SMTP_PORT", 587))
        smtp_user = os.environ.get("SMTP_USER") or st.secrets.get("SMTP_USER", "")
        smtp_password = os.environ.get("SMTP_PASSWORD") or st.secrets.get("SMTP_PASSWORD", "")
    except Exception:
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        smtp_user = os.environ.get("SMTP_USER", "")
        smtp_password = os.environ.get("SMTP_PASSWORD", "")

    to_email = "contacto@fv-inversiones.com"

    if not smtp_user or not smtp_password:
        raise Exception("Las credenciales de correo (SMTP_USER o SMTP_PASSWORD) no están configuradas en los Secrets de Streamlit.")

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = f"Nuevo Onboarding StoneX Completado - {cliente_nombre}"

    body = f"""
    Hola Francisco,
    
    Un cliente ha completado exitosamente el proceso de Onboarding de StoneX a través del Portal Público.
    
    Cliente: {cliente_nombre}
    
    Adjunto encontrarás el formulario de StoneX pre-llenado en formato Excel, junto a la documentación aportada.
    
    Saludos,
    Portal de Onboarding
    """
    msg.attach(MIMEText(body, 'plain'))

    # Adjuntar el Excel
    if os.path.exists(excel_filepath):
        with open(excel_filepath, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(excel_filepath))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(excel_filepath)}"'
            msg.attach(part)
    
    # Adjuntar otros documentos subidos por el cliente (pdfs, imagenes)
    if attachments:
        for attachment in attachments:
            if 'path' in attachment and os.path.exists(attachment['path']):
                with open(attachment['path'], "rb") as f:
                    part = MIMEApplication(f.read(), Name=attachment['filename'])
                    part['Content-Disposition'] = f'attachment; filename="{attachment["filename"]}"'
                    msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        raise Exception(f"Fallo en servidor SMTP: {e}")
