import qrcode
from PIL import Image, ImageDraw
import os

def generate_qr_with_logo(data, logo_path, output_path):
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15, # slightly larger for better resolution
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Use dark slate blue color for the QR blocks
    qr_color = "#1e293b"
    img = qr.make_image(fill_color=qr_color, back_color="white").convert('RGBA')
    
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        
        # Crop transparent padding
        bbox = logo.getbbox()
        if bbox:
            logo = logo.crop(bbox)
            
        # Target logo size: ~22% of the QR code
        qr_width, qr_height = img.size
        target_logo_width = int(qr_width * 0.22)
        
        # Calculate resize ratio
        aspect_ratio = logo.size[1] / logo.size[0]
        new_width = target_logo_width
        new_height = int(new_width * aspect_ratio)
        logo = logo.resize((new_width, new_height), Image.LANCZOS)
        
        # Create the white backdrop (padding of 15% around the logo)
        padding = int(new_width * 0.20)
        bg_width = new_width + (padding * 2)
        bg_height = new_height + (padding * 2)
        
        # Create a blank image for the backdrop
        backdrop = Image.new('RGBA', (bg_width, bg_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(backdrop)
        
        # Draw a white rounded rectangle
        radius = int(bg_width * 0.15)
        draw.rounded_rectangle((0, 0, bg_width, bg_height), radius=radius, fill="white")
        
        # Paste the tight logo onto the center of the backdrop
        logo_x = padding
        logo_y = padding
        backdrop.paste(logo, (logo_x, logo_y), logo)
        
        # Paste the final combined backdrop onto the center of the QR code
        pos_x = (qr_width - bg_width) // 2
        pos_y = (qr_height - bg_height) // 2
        
        # We paste using the backdrop itself as the mask so the rounded corners are transparent
        img.paste(backdrop, (pos_x, pos_y), backdrop)
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Generated elegant QR at: {output_path}")

# 1. VCARD QR
vcard_data = """BEGIN:VCARD
VERSION:3.0
N:Valencia;Francisco;;;
FN:Francisco Valencia
ORG:FV Asesorías / ALTUS AI
TITLE:Managing Partner | Asesor Financiero Senior
TEL;TYPE=WORK,VOICE:+56966779662
EMAIL;TYPE=PREF,INTERNET:contacto@fv-inversiones.com
URL:https://www.fv-inversiones.com
NOTE:Generado por Altus Core
END:VCARD"""

logo_file = "c:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/assets/brand/fv_icono_isotipo_amplio.png"
out1 = "c:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/assets/qr_vcard_fv.png"
out2 = "c:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/assets/qr_linkedin_company.png"

generate_qr_with_logo(vcard_data, logo_file, out1)
generate_qr_with_logo("https://www.linkedin.com/company/111763101/", logo_file, out2)

