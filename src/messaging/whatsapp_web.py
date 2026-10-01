import os
import time
from playwright.sync_api import sync_playwright

class WhatsAppBot:
    """
    Sistema autónomo de WhatsApp (Fase 5)
    Incluye compatibilidad con Pdfs y envíos duales.
    """
    def __init__(self, session_dir="data/whatsapp_session"):
        self.session_dir = session_dir
        self.browser_context = None
        self.page = None
        self.playwright = None
        
    def start(self):
        self.playwright = sync_playwright().start()
        
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)
            
        print("Abriendo Navegador de WhatsApp...")
        self.browser_context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.session_dir,
            headless=False,
            viewport={'width': 1280, 'height': 800},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        self.page = self.browser_context.new_page()
        # Aumentamos el timeout a 60s y esperamos solo al DOM para evitar bloqueos por carga de recursos
        self.page.goto("https://web.whatsapp.com/", timeout=60000, wait_until="domcontentloaded")
        print("Esperando conexión a WA Web...")
        
        try:
            self.page.wait_for_selector('div[id="pane-side"]', timeout=300000)
            print("¡✅ WhatsApp conectado!")
        except Exception as e:
            print("Timeout de sesión")
            self.close()
            raise e

    def send_attachment_and_message(self, phone: str, message: str, attachment_path: str = None, antiban=None) -> tuple[bool, str]:
        """ Envía el texto, y si existe el archivo, abre el panel de clips y envía un documento universal. """
        if not phone: return False, "Sin celular"
        
        try:
            # Limpiar caracteres no numéricos
            clean_num = ''.join(filter(str.isdigit, str(phone)))
            
            # Auto-formateo inteligente para números de Chile
            if len(clean_num) == 8:
                clean_num = f"569{clean_num}"
            elif len(clean_num) == 9:
                clean_num = f"56{clean_num}"
                
            if antiban: antiban.action_delay()
            
            # API Web para abrir el chat
            try:
                # REPARACIÓN CRÍTICA: Forzar el cierre del chat anterior presionando Escape.
                # Esto evita escribir el mensaje nuevo en el chat de la persona anterior si la red está lenta.
                self.page.keyboard.press("Escape")
                time.sleep(0.5)
                
                # El método definitivo: inyectar un link invisible y hacerle click.
                # Esto obliga a WhatsApp Web a interceptar la URL internamente (SPA routing)
                # y abre el chat de inmediato sin recargar toda la pesada página.
                self.page.evaluate(f"""
                    const link = document.createElement('a');
                    link.href = 'https://web.whatsapp.com/send?phone={clean_num}';
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                """)
            except Exception:
                pass
            
            # Múltiples alternativas por si WhatsApp actualizó su interfaz
            chat_box_selector = 'footer div[contenteditable="true"], div[title="Escribe un mensaje"], div[role="textbox"][data-lexical-editor="true"], #main div[contenteditable="true"]'
            
            # Esperamos a que aparezca la caja de chat o el popup de error
            start_wait = time.time()
            chat_ready = False
            while time.time() - start_wait < 35:
                # 1. Buscar popups de error PRIMERO
                error_texts = [
                    'URL es inválido', 'compartido a través de la URL', 'no es válido', 'invalid',
                    'no está en WhatsApp', 'is not on WhatsApp'
                ]
                for err_txt in error_texts:
                    # Usamos regex /.../i para búsqueda de substring insensible a mayúsculas
                    if self.page.locator(f'text=/{err_txt}/i').count() > 0:
                        try:
                            self.page.locator('div[role="button"]:has-text("OK")').click()
                        except:
                            pass
                        return False, "Número no registrado en WhatsApp"
                
                # 2. Intentar hacer CLICK en la caja de chat.
                try:
                    chat_box = self.page.locator(chat_box_selector).first
                    if chat_box.is_visible(timeout=1000):
                        try:
                            chat_box.click(timeout=1000)
                        except:
                            # Si algo intercepta el click (un popup de carga), forzamos el click
                            chat_box.click(force=True, timeout=1000)
                        chat_ready = True
                        break
                except Exception:
                    pass
                time.sleep(1)
                
            if not chat_ready:
                try:
                    # Tomar una captura y guardar el DOM para depurar
                    debug_path = os.path.join(os.getcwd(), f"debug_timeout_{clean_num}.png")
                    self.page.screenshot(path=debug_path)
                    with open(os.path.join(os.getcwd(), f"debug_timeout_dom_{clean_num}.html"), "w", encoding="utf-8") as f:
                        f.write(self.page.content())
                except:
                    pass
                return False, "Timeout esperando la interfaz de WhatsApp"
            
            # 1. ENVIAR TEXTO
            if message:
                # Ya le dimos click a la caja exitosamente en el bucle while
                # REPARACIÓN: Insertar texto manejando los saltos de línea correctamente con Shift+Enter
                lines = message.split('\n')
                for i, line in enumerate(lines):
                    if line:
                        self.page.keyboard.insert_text(line)
                    if i < len(lines) - 1:
                        self.page.keyboard.press("Shift+Enter")
                
                if antiban: antiban.action_delay()
                self.page.keyboard.press("Enter")
                time.sleep(1.5)
                
            # 2. ENVIAR ADJUNTO PDF/DOCUMENTO
            if attachment_path and os.path.exists(attachment_path):
                # Esperamos agresivamente a que el botón Clip/Plus sea verdaderamente interactuable
                attach_selectors = [
                    'div[title="Adjuntar"]',
                    'div[title="Añadir"]',
                    'button[aria-label="Adjuntar"]',
                    'button[aria-label="Añadir"]',
                    'div[aria-label="Adjuntar"]',
                    'div[aria-label="Añadir"]',
                    'span[data-icon="plus"]',
                    'span[data-icon="clip"]',
                    'footer button',
                    'footer div[role="button"]'
                ]
                
                clicked_plus = False
                # Reintentar hasta por 10 segundos buscando el botón visible real
                for _ in range(10):
                    for sel in attach_selectors:
                        btns = self.page.locator(sel)
                        try:
                            count = btns.count()
                            for i in range(count):
                                b = btns.nth(i)
                                if b.is_visible():
                                    b.click()
                                    clicked_plus = True
                                    break
                        except Exception:
                            pass
                        if clicked_plus: break
                    if clicked_plus: break
                    time.sleep(1)

                if not clicked_plus:
                    try: self.page.screenshot(path="data/wa_error_plus_btn.png")
                    except: pass
                    return False, "Botón '+/Clip' no encontrado o tapado (Pantallazo diagnóstico guardado)"
                    
                time.sleep(1.0)
                
                # Atrapamos el explorador de archivos invisible
                try:
                    with self.page.expect_file_chooser(timeout=10000) as fc_info:
                        doc_selectors = [
                            'span[data-icon="document"]',
                            'ul li div[role="button"]:has-text("Documento")',
                            'ul li:has-text("Documento")',
                            'span:has-text("Documento")',
                            'div:text-is("Documento")',
                            'span:has-text("Document")',
                            'span[data-icon="attach-document"]',
                            'ul li button'
                        ]
                        
                        clicked_doc = False
                        for _ in range(8):
                            for d_sel in doc_selectors:
                                btns = self.page.locator(d_sel)
                                try:
                                    count = btns.count()
                                    for i in range(count):
                                        b = btns.nth(i)
                                        if b.is_visible():
                                            b.click()
                                            clicked_doc = True
                                            break
                                except Exception:
                                    pass
                                if clicked_doc: break
                            if clicked_doc: break
                            time.sleep(1)
                        
                        if not clicked_doc:
                            try: self.page.screenshot(path="data/wa_error_doc_btn.png")
                            except: pass
                            return False, "No se encontró el botón de 'Documento' tras abrir el menú '+'"
                            
                    file_chooser = fc_info.value
                    file_chooser.set_files(os.path.abspath(attachment_path))
                except Exception as ex:
                    import traceback
                    return False, f"Fallo al invocar el cargador de Windows: {ex}"
                
                # Esperar a la pantalla emergente verde de enviar de WhatsApp (Puede tardar en renderizar el archivo)
                send_selectors = [
                    'span[data-icon="send"]',
                    'span[data-icon="wds-ic-send-filled"]',
                    'div[aria-label="Enviar"]',
                    'div[aria-label="Enviar 1 seleccionado"]',
                    'div[aria-label="Send"]',
                    'button[aria-label="Enviar"]',
                    'div[title="Enviar"]'
                ]
                
                clicked_send = False
                for _ in range(15): # Esperar hasta 15 segundos que cargue el preview
                    for s_sel in send_selectors:
                        btns = self.page.locator(s_sel)
                        try:
                            count = btns.count()
                            for i in range(count):
                                b = btns.nth(i)
                                if b.is_visible():
                                    time.sleep(1.5) # Esperar a que la animación del panel y la imagen terminen de cargar
                                    b.click()
                                    clicked_send = True
                                    break
                        except Exception:
                            pass
                        if clicked_send: break
                    if clicked_send: break
                    time.sleep(1)
                    
                if not clicked_send:
                    try:
                        with open("data/wa_debug_dom.html", "w", encoding="utf-8") as f:
                            f.write(self.page.content())
                        self.page.screenshot(path="data/wa_error_send_btn.png")
                    except Exception:
                        pass
                    return False, "Botón 'Enviar' del archivo adjunto no apareció o cambió en esta versión de WhatsApp."
                if antiban: antiban.action_delay()
                
                # Darle 10 segundos vitales para que la subida del archivo (especialmente si es pesado) cruce por la red antes de cambiar de página
                time.sleep(10)
                
            return True, "Enviado exitosamente"
            
        except Exception as e:
            import traceback
            return False, f"Crash de Interfaz WA: {traceback.format_exc()}"

    def send_message(self, phone: str, message: str, antiban=None) -> tuple[bool, str]:
        """Envía solo texto (sin adjunto). Alias simplificado para el motor de seguimiento."""
        return self.send_attachment_and_message(phone, message, attachment_path=None, antiban=antiban)

    def close(self):
        if self.browser_context:
            self.browser_context.close()
        if self.playwright:
            self.playwright.stop()
