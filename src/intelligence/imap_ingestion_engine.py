import imaplib
import email
import os
import openpyxl
from email.header import decode_header
import logging
import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IMAPIngestionEngine")

class IMAPIngestionEngine:
    def __init__(self, username, password, imap_url="imap.gmail.com"):
        self.username = username
        self.password = password
        self.imap_url = imap_url
        self.mail = None

    def connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_url)
            self.mail.login(self.username, self.password)
            logger.info("Conectado exitosamente al servidor IMAP.")
            return True
        except Exception as e:
            logger.error(f"Error conectando a IMAP: {e}")
            return False

    def close(self):
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass

    def check_new_inventory_emails(self):
        """Revisa la bandeja de entrada buscando correos con el asunto 'Inventario MFO' o similares."""
        if not self.mail:
            return

        try:
            self.mail.select("inbox")
            
            # Buscar correos no leídos que contengan 'Inventario' en el asunto
            status, messages = self.mail.search(None, '(UNSEEN SUBJECT "Inventario")')
            
            if status != "OK":
                logger.info("No se encontraron correos nuevos de inventario.")
                return

            email_ids = messages[0].split()
            for e_id in email_ids:
                status, msg_data = self.mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        
                        sender = msg.get("From")
                        logger.info(f"Procesando correo de: {sender}, Asunto: {subject}")
                        
                        self._process_attachments(msg, sender)
        
        except Exception as e:
            logger.error(f"Error revisando correos MFO: {e}")

    def check_market_research_emails(self):
        """Revisa la bandeja buscando correos de Research Institucional (Cuerpo o PDF adjunto)."""
        if not self.mail:
            return

        try:
            self.mail.select("inbox")
            # Buscar correos no leídos generales para filtrarlos programáticamente
            status, messages = self.mail.search(None, 'UNSEEN')
            
            if status != "OK" or not messages[0]:
                return

            email_ids = messages[0].split()
            
            # Palabras clave heurísticas para detectar reportes de mercado
            keywords = ["research", "market", "mercado", "visión", "vision", "estrategia", "update", "informe", "morning", "daily"]
            domains = ["larrainvial", "jpmorgan", "morganstanley", "btg", "banchile", "credicorp", "santander", "bci", "scotiabank"]

            for e_id in email_ids:
                status, msg_data = self.mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                            
                        sender = msg.get("From", "")
                        
                        # Convertir a minúsculas para evaluar
                        subj_lower = subject.lower()
                        sender_lower = sender.lower()
                        
                        # Evaluar si es un correo de mercado
                        is_market = any(k in subj_lower for k in keywords) or any(d in sender_lower for d in domains)
                        
                        if is_market:
                            logger.info(f"Detectado correo de Mercado de: {sender} | Asunto: {subject}")
                            self._extract_market_content(msg, sender, subject)
                            
        except Exception as e:
            logger.error(f"Error revisando correos de mercado: {e}")

    def _extract_market_content(self, msg, sender, subject):
        """Extrae el cuerpo del correo o el PDF adjunto y lo guarda para el motor de Consenso."""
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "market_research_raw")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%md_%H%M%S")
        safe_sender = "".join(c for c in sender if c.isalnum() or c in "@.-_")
        base_filename = f"{timestamp}_{safe_sender}"
        
        has_pdf = False
        
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Extraer PDF adjunto
            if "attachment" in content_disposition and "pdf" in content_type:
                filename = part.get_filename()
                if filename:
                    filepath = os.path.join(output_dir, f"{base_filename}.pdf")
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    logger.info(f"PDF de mercado guardado: {filepath}")
                    has_pdf = True
                    
            # Si no es adjunto y es texto, extraemos el cuerpo por si acaso
            elif content_type == "text/plain" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True).decode(errors="ignore")
                # Solo guardamos el txt si el cuerpo es sustancial (> 200 caracteres)
                if len(body) > 200:
                    filepath = os.path.join(output_dir, f"{base_filename}.txt")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f"SENDER: {sender}\nSUBJECT: {subject}\n\n{body}")
                    logger.info(f"Cuerpo de correo de mercado guardado: {filepath}")

    def _process_attachments(self, msg, sender):
        """Busca adjuntos Excel y los procesa."""
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if filename:
                if "Inventario" in filename and filename.endswith((".xlsx", ".xls")):
                    logger.info(f"Encontrado Excel de inventario: {filename}")
                    
                    # Guardar temporalmente
                    temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "temp_uploads")
                    os.makedirs(temp_dir, exist_ok=True)
                    filepath = os.path.join(temp_dir, filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                        
                    # Parsear Excel
                    self._parse_mfo_inventory(filepath, sender)
                    
                    # Cleanup
                    if os.path.exists(filepath):
                        os.remove(filepath)

    def _parse_mfo_inventory(self, filepath, sender):
        """Lee el Excel y extrae los datos para actualizar la DB (mock por ahora)."""
        logger.info(f"Iniciando parseo del inventario MFO recibido de {sender}...")
        try:
            wb = openpyxl.load_workbook(filepath, data_only=True)
            if "Inventario Patrimonial" in wb.sheetnames:
                ws = wb["Inventario Patrimonial"]
                
                # Ejemplo de extracción simple:
                # Normalmente aquí leeríamos cada sección basándonos en los títulos
                # Para simplificar, registramos el evento.
                
                logger.info(f"Inventario parseado exitosamente para el cliente.")
                # TODO: Guardar en la DB real
        except Exception as e:
            logger.error(f"Error parseando el Excel de inventario: {e}")

if __name__ == "__main__":
    # Soporte para múltiples cuentas (ej: IMAP_USER, IMAP_USER_1, IMAP_USER_2...)
    cuentas_a_procesar = []
    
    # Revisar IMAP_USER clásico
    if os.getenv("IMAP_USER") and os.getenv("IMAP_PASS"):
        cuentas_a_procesar.append((os.getenv("IMAP_USER"), os.getenv("IMAP_PASS")))
        
    # Revisar IMAP_USER_X
    for i in range(1, 10):
        u = os.getenv(f"IMAP_USER_{i}")
        p = os.getenv(f"IMAP_PASS_{i}")
        if u and p:
            cuentas_a_procesar.append((u, p))
            
    if not cuentas_a_procesar:
        logger.warning("No hay credenciales IMAP configuradas en el .env. Ignorando conexión real.")
    else:
        logger.info(f"Iniciando demonio IMAP para {len(cuentas_a_procesar)} cuenta(s)...")
        for user, pwd in set(cuentas_a_procesar):
            logger.info(f"--- Conectando a {user} ---")
            engine = IMAPIngestionEngine(user, pwd)
            if engine.connect():
                engine.check_new_inventory_emails()
                engine.check_market_research_emails()
                engine.close()
