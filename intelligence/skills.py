import os
from datetime import datetime, timedelta

class AgentSkills:
    """
    Caja de herramientas para que los agentes ejecuten acciones en el mundo real.
    """
    
    @staticmethod
    def prepare_whatsapp(phone, message):
        """Prepara el link de WhatsApp para disparo rápido."""
        import urllib.parse
        clean_phone = str(phone).replace("+", "").replace(" ", "")
        url_encoded_msg = urllib.parse.quote(message)
        return f"https://wa.me/{clean_phone}?text={url_encoded_msg}"

    @staticmethod
    def generate_calendar_invite(subject, date_str, time_str, duration_mins=30):
        """Genera un archivo .ics para agendar reuniones rápidas."""
        try:
            # Ejemplo: date_str '2026-05-20', time_str '10:00'
            start_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            end_time = start_time + timedelta(minutes=duration_mins)
            
            ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//BD SENIOR AGENT//ES
BEGIN:VEVENT
SUMMARY:{subject}
DTSTART:{start_time.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_time.strftime('%Y%m%dT%H%M%S')}
DESCRIPTION:Reunión de Auditoría Patrimonial Estratégica.
END:VEVENT
END:VCALENDAR"""
            
            file_path = f"intelligence/invites/invite_{datetime.now().strftime('%H%M%S')}.ics"
            if not os.path.exists("intelligence/invites"): os.makedirs("intelligence/invites")
            
            with open(file_path, "w") as f:
                f.write(ics_content)
            return file_path
        except Exception as e:
            return f"Error generando invitación: {e}"

    @staticmethod
    def draft_email(to_email, subject, body):
        """Prepara un borrador de correo electrónico."""
        # Por ahora devolvemos el draft; integrar con SMTP o Gmail API luego.
        draft = {
            "to": to_email,
            "subject": subject,
            "body": body,
            "timestamp": str(datetime.now())
        }
        return draft
