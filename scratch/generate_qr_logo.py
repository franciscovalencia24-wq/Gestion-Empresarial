import qrcode
from PIL import Image, ImageDraw
import os

def generate_qr_with_logo(data, logo_path, output_path):
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1e293b", back_color="white").convert('RGB')
    
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        
        logo_size = int(img.size[0] * 0.28) # 28% width
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        
        # Create a white square with rounded corners as a backdrop for the logo
        backdrop = Image.new('RGBA', (logo_size + 20, logo_size + 20), (255, 255, 255, 0))
        draw = ImageDraw.Draw(backdrop)
        draw.rounded_rectangle((0, 0, logo_size + 20, logo_size + 20), radius=10, fill="white")
        
        # Paste logo onto backdrop
        backdrop.paste(logo, (10, 10), logo)
        
        # Paste backdrop onto QR
        pos = ((img.size[0] - backdrop.size[0]) // 2, (img.size[1] - backdrop.size[1]) // 2)
        img.paste(backdrop, pos, backdrop)
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Generated QR with logo at: {output_path}")

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

generate_qr_with_logo(vcard_data, "c:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/assets/brand/fv_icono_isotipo_amplio.png", "c:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/assets/qr_vcard_fv.png")

# 2. LINKEDIN QR
generate_qr_with_logo("https://www.linkedin.com/company/111763101/", "c:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/assets/brand/fv_icono_isotipo_amplio.png", "c:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/assets/qr_linkedin_company.png")
