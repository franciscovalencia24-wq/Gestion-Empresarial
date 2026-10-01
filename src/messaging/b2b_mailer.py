import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def send_b2b_invitation_email(to_email, nombre_ejecutivo, razon_social, enlace):
    """
    Envía una invitación formal de Onboarding 360 al correo de un ejecutivo B2B.
    """
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

    if not smtp_user or not smtp_password:
        raise Exception("Las credenciales SMTP_USER/SMTP_PASSWORD no están configuradas.")

    msg = MIMEMultipart("alternative")
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = f"Invitación Exclusiva - Portal Onboarding y Reporte Patrimonial 360 (ALTUS AI)"

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
          <div style="background-color: #0f172a; padding: 20px; text-align: center;">
            <h2 style="color: #38bdf8; margin: 0;">ALTUS AI - Portal 360</h2>
          </div>
          <div style="padding: 30px;">
            <p>Estimado/a <strong>{nombre_ejecutivo}</strong>,</p>
            <p>Por encargo de la plana gerencial de <strong>{razon_social}</strong>, le extendemos una invitación exclusiva para acceder a su portal privado de Onboarding y Reporte Patrimonial 360 en ALTUS AI.</p>
            <p>Este servicio corporativo le permite realizar simulaciones de impacto tributario y consolidar su patrimonio bajo un marco de estricta confidencialidad.</p>
            <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
              <p style="margin: 0; font-size: 0.95em;"><strong>⚠️ Nota de Privacidad:</strong> La información financiera y las simulaciones tributarias generadas en esta plataforma son <strong>100% privadas y confidenciales</strong>. ALTUS AI no comparte ningún detalle o resultado patrimonial individual con su empleador ({razon_social}).</p>
            </div>
            <p>Para acceder y configurar su perfil, por favor ingrese a través de su enlace personal e intransferible:</p>
            <div style="text-align: center; margin: 30px 0;">
              <a href="{enlace}" style="background-color: #3b82f6; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Acceder a Mi Portal Confidencial</a>
            </div>
            <p style="font-size: 0.9em; color: #666;">Si el botón no funciona, copie y pegue el siguiente enlace en su navegador:<br/>{enlace}</p>
          </div>
          <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e0e0e0; font-size: 0.8em; color: #64748b;">
            © ALTUS AI SpA. Todos los derechos reservados.<br/>
            Este es un correo automático, por favor no responda a esta dirección.
          </div>
        </div>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        raise Exception(f"Fallo en servidor SMTP: {e}")
