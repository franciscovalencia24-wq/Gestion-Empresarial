import os
import base64
import re
from playwright.sync_api import sync_playwright

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

fv_logo_svg = get_base64_of_file("assets/Icono_FV_Principal.svg")
altus_logo_svg = get_base64_of_file("assets/Logo_ALTUS AI_Principal_Fondo oscuro.svg")

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
        
        body {{
            margin: 0;
            padding: 50px;
            background-color: #111;
            font-family: 'Montserrat', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            zoom: 2; /* 4K Rendering Scale */
        }}
        
        .ad-container {{
            width: 1200px;
            height: 800px;
            position: relative;
            box-shadow: 0 30px 60px rgba(0,0,0,0.8);
            border-radius: 20px;
            overflow: hidden;
            box-sizing: border-box;
            background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
            border: 1px solid #333;
            display: flex;
            padding: 60px;
        }}
        
        /* Left Column: Branding and Message */
        .left-col {{
            flex: 1.2;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border-right: 1px solid rgba(212, 175, 55, 0.2);
            padding-right: 40px;
        }}
        
        .logos-top {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .fv-logo-container {{ display: flex; flex-direction: row; align-items: center; }}
        .logo-img {{ height: 120px; filter: brightness(0) sepia(1) hue-rotate(10deg) saturate(3) invert(0.8); margin-right: 15px; }}
        .fv-text {{ font-size: 28px; font-weight: 600; letter-spacing: 10px; color: #D4AF37; }}
        
        .main-message {{
            margin-top: 40px;
        }}
        
        .headline {{
            font-size: 42px;
            font-weight: 700;
            color: #FFF;
            line-height: 1.2;
            margin-bottom: 20px;
        }}
        
        .subheadline {{
            font-size: 22px;
            font-weight: 300;
            color: #AAA;
            line-height: 1.5;
            letter-spacing: 1px;
        }}
        
        .highlight {{
            color: #D4AF37;
            font-weight: 600;
        }}
        
        .altus-section {{
            margin-top: 40px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }}
        .powered-by {{ font-size: 14px; font-weight: 600; letter-spacing: 4px; color: #777; margin-bottom: 10px; text-transform: uppercase; }}
        .altus-logo {{ height: 80px; filter: brightness(0) invert(1); opacity: 0.9; margin-left: -5px; }}
        
        /* Right Column: Contact Info */
        .right-col {{
            flex: 0.8;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding-left: 50px;
        }}
        
        .name {{ font-size: 38px; font-weight: 700; margin-bottom: 5px; color:#D4AF37; }}
        .title {{ font-size: 16px; font-weight: 500; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 50px; color:#888; }}
        
        .contact-list {{
            display: flex;
            flex-direction: column;
            gap: 25px;
        }}
        
        .contact-item {{
            display: flex;
            align-items: center;
            font-size: 18px;
            color: #EEE;
            font-weight: 400;
            letter-spacing: 0.5px;
        }}
        
        .contact-icon {{
            font-size: 24px;
            color: #D4AF37;
            margin-right: 20px;
            width: 30px;
            text-align: center;
        }}
        
        .website {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            font-size: 20px;
            letter-spacing: 4px;
            color: #D4AF37;
            font-weight: 600;
        }}

    </style>
</head>
<body>

    <div class="ad-container">
        <!-- Izquierda: Mensaje y Marca -->
        <div class="left-col">
            <div class="logos-top">
                <div class="fv-logo-container">
                    <img src="{fv_logo_svg}" class="logo-img">
                    <div class="fv-text">ASESORÍAS</div>
                </div>
            </div>
            
            <div class="main-message">
                <div class="headline">Tu patrimonio no es una plantilla genérica.</div>
                <div class="subheadline">Combinamos el <span class="highlight">juicio y experiencia humana</span> con el poder de la Inteligencia Artificial para diseñar una estrategia 100% a tu medida.</div>
            </div>
            
            <div class="altus-section">
                <div class="powered-by">Impulsado por la precisión de</div>
                <img src="{altus_logo_svg}" class="altus-logo">
            </div>
        </div>
        
        <!-- Derecha: Datos de Contacto -->
        <div class="right-col">
            <div class="name">Francisco Valencia</div>
            <div class="title">Asesor Financiero Senior</div>
            
            <div class="contact-list">
                <div class="contact-item">
                    <span class="contact-icon">📱</span> +56 9 8249 9789
                </div>
                <div class="contact-item">
                    <span class="contact-icon">✉️</span> fvalencia@asesoriasfv.cl
                </div>
                <div class="contact-item">
                    <span class="contact-icon">📍</span> Las Condes, Santiago | La Serena
                </div>
                <div class="contact-item">
                    <span class="contact-icon">💼</span> linkedin.com/in/francisco-valencia
                </div>
            </div>
            
            <div class="website">
                WWW.ASESORIASFV.CL
            </div>
        </div>
    </div>

</body>
</html>
"""

os.makedirs("assets", exist_ok=True)
html_path = "scratch/temp_ad.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(device_scale_factor=2) # 4K scaling
    page.set_viewport_size({"width": 1300, "height": 900})
    
    # Load HTML
    page.goto(f"file://{os.path.abspath(html_path)}")
    page.wait_for_timeout(1000) # Wait for fonts/SVGs
    
    # Take screenshot of the ad-container element
    ad_element = page.locator(".ad-container")
    ad_element.screenshot(path="assets/revista_miradaclave_ad.png")
    
    browser.close()

print("Ad generated successfully at assets/revista_miradaclave_ad.png")
