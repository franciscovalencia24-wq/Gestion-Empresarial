import os
import base64
import re
import qrcode
from playwright.sync_api import sync_playwright

# 1. Generate QR Code
qr_data = "https://www.linkedin.com/company/111763101/"
qr = qrcode.QRCode(version=1, box_size=10, border=1)
qr.add_data(qr_data)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
os.makedirs("assets", exist_ok=True)
qr_path = "assets/qr_linkedin_company.png"
img.save(qr_path)

# 2. Helper functions
def get_base64_of_file(filepath):
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "ALTUS" in filepath:
        content = re.sub(r'<rect[^>]*fill:#1c2224[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<rect\s+style="fill:#1c2224;.*?>', '', content)
    
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    ext = filepath.split(".")[-1].lower()
    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
    return f"data:{mime};base64,{encoded}"

def get_base64_of_image(filepath):
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    ext = filepath.split(".")[-1].lower()
    mime = "image/png"
    return f"data:{mime};base64,{encoded}"

fv_logo_svg = get_base64_of_file("assets/Icono_FV_Principal.svg")
altus_logo_svg = get_base64_of_file("assets/Logo_ALTUS AI_Principal_Fondo oscuro.svg")
qr_b64 = get_base64_of_image(qr_path)

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');
        
        body {{
            margin: 0;
            padding: 0;
            background-color: #1a1a1a;
            font-family: 'Montserrat', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 2480px;
            height: 1748px;
            zoom: 4;
        }}
        
        .ad-container {{
            width: 2480px;
            height: 1748px;
            position: relative;
            box-sizing: border-box;
            background: #1a1a1a;
            display: flex;
            border: 2px solid #333;
        }}
        
        /* Left Column: Branding */
        .left-col {{
            flex: 1.2;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-right: 2px solid rgba(255, 255, 255, 0.05);
            padding: 100px;
        }}
        
        .logo-img {{ 
            height: 380px; 
            filter: brightness(0) sepia(1) hue-rotate(10deg) saturate(3) invert(0.8); 
            margin-bottom: 40px; 
            margin-left: 20px;
        }}
        
        .fv-text {{
            font-size: 36px; 
            font-weight: 500; 
            letter-spacing: 14px; 
            color: #D4AF37; 
            text-align: center;
            white-space: nowrap;
            text-transform: uppercase;
            margin-left: 0;
            margin-top: 10px;
        }}
        
        .slogan {{
            font-size: 32px;
            font-weight: 300;
            color: #CCC;
            letter-spacing: 4px;
            margin-top: 60px;
            text-align: center;
        }}
        
        /* Right Column: Contact Info & QR */
        .right-col {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 180px 100px 180px 150px;
        }}
        
        .contact-list {{
            display: flex;
            flex-direction: column;
            gap: 60px;
            margin-top: 50px;
        }}
        
        .contact-item {{
            display: flex;
            align-items: center;
            font-size: 36px;
            color: #FFF;
            font-weight: 400;
            letter-spacing: 2px;
        }}
        
        .contact-icon {{
            font-size: 45px;
            color: #D4AF37;
            margin-right: 40px;
            width: 55px;
            text-align: center;
            filter: grayscale(100%) brightness(200%);
            /* Using standard emojis but styled cleanly, or just standard text icons */
        }}
        
        /* Bottom Section of Right Column */
        .bottom-section {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 50px;
        }}
        
        .altus-section {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }}
        
        .powered-by {{ 
            font-size: 20px; 
            font-weight: 600; 
            letter-spacing: 8px; 
            color: #777; 
            margin-bottom: 20px; 
            text-transform: uppercase; 
        }}
        
        .altus-logo {{ 
            height: 320px; 
            filter: brightness(0) invert(1); 
            opacity: 0.9; 
            margin-left: -10px; 
        }}
        
        .qr-section {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .qr-box {{
            width: 250px;
            height: 250px;
            background: white;
            border-radius: 20px;
            padding: 15px;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            margin-bottom: 30px;
        }}
        
        .qr-box img {{
            width: 100%;
            height: 100%;
            border-radius: 10px;
        }}
        
        .linkedin-cta {{
            font-size: 24px;
            color: #D4AF37;
            letter-spacing: 2px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .linkedin-in {{
            font-size: 28px;
            font-weight: 800;
        }}
        
        .scan-text {{
            font-size: 18px;
            color: #777;
            letter-spacing: 4px;
        }}

    </style>
</head>
<body>

    <div class="ad-container">
        <!-- Left: Logo & Slogan -->
        <div class="left-col">
            <img src="{fv_logo_svg}" class="logo-img">
            <div class="fv-text">ASESORÍAS E INVERSIONES</div>
            <div class="slogan">Innovación y Respaldo para tu Patrimonio</div>
        </div>
        
        <!-- Right: Contact -->
        <div class="right-col">
            <div class="contact-list">
                <div class="contact-item">
                    <span class="contact-icon" style="color: #FF3366; filter: none;">📞</span> +56 9 6677 9662
                </div>
                <div class="contact-item">
                    <span class="contact-icon" style="color: #E2D1F9; filter: none;">✉️</span> contacto@fv-inversiones.com
                </div>
                <div class="contact-item">
                    <span class="contact-icon" style="color: #66CCFF; filter: none;">🌐</span> www.fv-inversiones.com
                </div>
            </div>
            
            <div class="bottom-section">
                <div class="altus-section">
                    <div class="powered-by">POWERED BY</div>
                    <img src="{altus_logo_svg}" class="altus-logo">
                </div>
                
                <div class="qr-section">
                    <div class="qr-box">
                        <img src="{qr_b64}">
                    </div>
                    <div class="linkedin-cta">
                        <span>Conecta con nosotros</span>
                        <span class="linkedin-in">in</span>
                    </div>
                    <div class="scan-text">ESCANEA PARA CONECTAR</div>
                </div>
            </div>
        </div>
    </div>

</body>
</html>
"""

html_path = "scratch/temp_ad_print.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(device_scale_factor=1)
    page.set_viewport_size({"width": 9920, "height": 6992})
    
    page.goto(f"file://{os.path.abspath(html_path)}")
    page.wait_for_timeout(1000)
    
    ad_element = page.locator(".ad-container")
    ad_element.screenshot(path="assets/revista_miradaclave_ad_210x148_8k.png")
    
    browser.close()

print("Print ad generated successfully at assets/revista_miradaclave_ad_210x148_8k.png")
