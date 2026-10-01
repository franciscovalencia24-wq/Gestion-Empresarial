import os
import time
from src.messaging.whatsapp_web import WhatsAppBot

def test_full_wa():
    print("Testing WhatsAppBot with 2.5MB image...")
    bot = WhatsAppBot()
    bot.start()
    
    # We use the user's phone number and the uploaded image
    phone = "+56966779662"
    msg = "Test message"
    
    attachment_path = "scratch/infografia_test.png"
    # Copy the test image from some big file, or just use the test_image
    
    try:
        exito, error = bot.send_attachment_and_message(phone, msg, attachment_path="data/test_image.png")
        print(f"Result: {exito}, {error}")
    finally:
        bot.close()

if __name__ == "__main__":
    test_full_wa()
