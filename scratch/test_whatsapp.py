import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.messaging.whatsapp_web import WhatsAppBot

def run_test():
    bot = WhatsAppBot(session_dir="data/whatsapp_session_test")
    try:
        print("Iniciando bot de WhatsApp. Si es primera vez, tendrás que escanear el QR.")
        bot.start()
        
        phone = "+56966779662"
        message = (
            "Hola Francisco, mi nombre es Francisco Valencia, Asesor Financiero Senior en Principal Financial Group.\n\n"
            "Me especializo en entregar una asesoría patrimonial integral a personas y empresas, operando con un nivel de servicio y exclusividad equivalente al de un *Family Office*.\n\n"
            "Más allá de la gestión tradicional de inversiones, me enfoco en la *planificación patrimonial estratégica* y construir para mis clientes un *Reporte Patrimonial 360°*. Todo esto es impulsado por *ALTUS AI*, un software cuantitativo privado que he diseñado para consolidar las inversiones, bienes raíces, seguros, deudas, beneficiarios y sociedades en una sola vista inteligente. Esto nos permite *detectar ineficiencias fiscales*, *determinar el impuesto a la herencia*, optimizar tu rentabilidad global, entre muchas otras cosas.\n\n"
            "¿Tendrás 10 minutos en los próximos días para explicarte y mostrarte un ejemplo real de cómo se ve este nivel de asesoría?\n\n"
            "Saludos cordiales,\n\n"
            "*Francisco Valencia*\n\n"
            "Asesor Financiero Senior | Principal Financial Group\n\n"
            "www.linkedin.com/in/francisco-javier-valencia-aguila"
        )
        
        print(f"Enviando mensaje de prueba a {phone}...")
        success, msg = bot.send_message(phone, message)
        
        if success:
            print("✅ Prueba exitosa: El mensaje fue enviado.")
        else:
            print(f"❌ Fallo en la prueba: {msg}")
            
    except Exception as e:
        print(f"Error crítico en la prueba: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    run_test()
