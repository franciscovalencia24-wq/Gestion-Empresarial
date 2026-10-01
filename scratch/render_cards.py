import os
import base64
import re
from playwright.sync_api import sync_playwright

def get_base64_of_file(filepath):
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Strip the dark rect background from Altus SVG
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
    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
    return f"data:{mime};base64,{encoded}"

fv_logo_svg = get_base64_of_file("assets/Icono_FV_Principal.svg")
altus_logo_svg = get_base64_of_image("assets/brand/altus_ai_logo_negativo.png")

# Slogans
slogans = [
    "Innovación y Respaldo para tu Patrimonio",
    "Estrategia Financiera, Precisión Tecnológica",
    "El Nuevo Estándar en Gestión Patrimonial"
]

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600&display=swap');
        
        body {{
            margin: 0;
            padding: 50px;
            background-color: #111;
            font-family: 'Montserrat', sans-serif;
            display: flex;
            flex-direction: column;
            gap: 50px;
            zoom: 2; /* 4K Rendering Scale */
        }}
        
        .card-container {{
            width: 1011px;
            height: 638px;
            position: relative;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            border-radius: 30px;
            overflow: hidden;
            box-sizing: border-box;
            background: #1a1a1a;
            border: 2px solid #333;
        }}
        
        .front {{ color: #D4AF37; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
        .back {{ color: #ffffff; padding: 60px; display: flex; justify-content: space-between; align-items: center; }}

        /* FV LOGO STYLING */
        .fv-logo-container {{ display: flex; flex-direction: column; align-items: center; }}
        .logo-img {{ height: 280px; object-fit: contain; filter: brightness(0) sepia(1) hue-rotate(10deg) saturate(3) invert(0.8); margin-bottom: 10px; }}
        .fv-text {{ font-family: 'Montserrat', sans-serif; font-size: 24px; font-weight: 500; letter-spacing: 14px; color: #D4AF37; margin-left: 14px; }}
        
        .name {{ font-size: 42px; font-weight: 700; margin-bottom: 5px; letter-spacing: 1px; color:#D4AF37; }}
        .title {{ font-size: 18px; font-weight: 400; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 40px; color:#aaa; }}
        
        .contact-item {{ font-size: 18px; display: flex; align-items: center; margin-bottom: 15px; font-weight: 400; }}
        .contact-icon {{ margin-right: 15px; font-size: 22px; width: 30px; text-align: center; color: #D4AF37; }}
        
        .slogan {{ font-size: 22px; font-weight: 300; margin-top: 60px; letter-spacing: 3px; text-align: center; color: #FFFFFF; }}
        
        .qr-placeholder {{ width: 180px; height: 180px; background: #1a1a1a; border-radius: 10px; display: flex; justify-content: center; align-items: center; border: 2px solid #D4AF37; }}
        
        .powered-by {{ font-size: 12px; font-weight: 600; letter-spacing: 5px; color: #777; margin-bottom: 15px; }}
        /* Increased Altus logo size significantly */
        .altus-logo-gold {{ height: 140px; object-fit: contain; filter: brightness(0) sepia(1) hue-rotate(10deg) saturate(3) invert(0.8); margin-left: -5px; }}
        .altus-logo-white {{ height: 140px; object-fit: contain; filter: brightness(0) invert(1); opacity: 0.9; margin-left: -5px; }}
        
        .linkedin-cta {{ margin-top:15px; font-size:12px; color:#D4AF37; letter-spacing:2px; font-weight: 600; text-align:center; display: flex; align-items: center; justify-content: center; gap: 8px; }}
        
    </style>
</head>
<body>

    <!-- FRONT (Reference) -->
    <div class="card-container front" id="d2-front">
        <div class="fv-logo-container">
            <img src="{fv_logo_svg}" class="logo-img">
            <div class="fv-text">ASESORÍAS E INVERSIONES</div>
        </div>
        <div class="slogan">{slogans[0]}</div>
    </div>
    
    <!-- BACK 1: Altus in GOLD -->
    <div class="card-container back" id="back-gold">
        <div style="flex-grow: 1;">
            <div class="name">FRANCISCO VALENCIA</div>
            <div class="title">Managing Partner | Asesor Financiero Senior</div>
            <div style="height: 30px;"></div>
            <div class="contact-item"><span class="contact-icon">📞</span> +56 9 6677 9662</div>
            <div class="contact-item"><span class="contact-icon">✉️</span> contacto@fv-inversiones.com</div>
            <div class="contact-item"><span class="contact-icon">🌐</span> www.fv-inversiones.com</div>
            <div style="height: 30px;"></div>
            <div>
                <div class="powered-by">POWERED BY ALTUS CORE</div>
                <img src="{altus_logo_svg}" class="altus-logo-gold">
            </div>
        </div>
        <div style="display:flex; flex-direction:column; align-items:center; width: 220px;">
            <div class="qr-placeholder"><span style="font-size:40px;">📱</span></div>
            <div class="linkedin-cta">
                <span>Conecta conmigo</span>
                <span style="font-size: 16px;">in</span>
            </div>
            <div style="margin-top:15px; font-size:10px; color:#aaa; letter-spacing:2px; text-align:center;">ESCANEA PARA CONECTAR</div>
        </div>
    </div>

    <!-- BACK 2: Altus in WHITE -->
    <div class="card-container back" id="back-white">
        <div style="flex-grow: 1;">
            <div class="name">FRANCISCO VALENCIA</div>
            <div class="title">Managing Partner | Asesor Financiero Senior</div>
            <div style="height: 30px;"></div>
            <div class="contact-item"><span class="contact-icon">📞</span> +56 9 6677 9662</div>
            <div class="contact-item"><span class="contact-icon">✉️</span> contacto@fv-inversiones.com</div>
            <div class="contact-item"><span class="contact-icon">🌐</span> www.fv-inversiones.com</div>
            <div style="height: 30px;"></div>
            <div>
                <div class="powered-by">POWERED BY ALTUS CORE</div>
                <img src="{altus_logo_svg}" class="altus-logo-white">
            </div>
        </div>
        <div style="display:flex; flex-direction:column; align-items:center; width: 220px;">
            <div class="qr-placeholder" style="border: none; padding: 5px; background: white;"><img src="{get_base64_of_image('assets/qr_vcard_fv.png')}" style="width: 100%; height: 100%; border-radius: 5px;"></div>
            <div class="linkedin-cta">
                <span>Conecta conmigo</span>
                <span style="font-size: 16px; font-weight: bold;">in</span>
            </div>
            <div style="margin-top:15px; font-size:10px; color:#aaa; letter-spacing:2px; text-align:center;">ESCANEA PARA CONECTAR</div>
        </div>
    </div>

</body>
</html>
"""

with open("tarjetas_presentacion/tarjetas_v3.html", "w", encoding="utf-8") as f:
    f.write(html_content)

def render_cards():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Increase viewport and device_scale_factor for massive resolution
        page = browser.new_page(viewport={'width': 4400, 'height': 4800}, device_scale_factor=2)
        page.goto(f"file://{os.path.abspath('tarjetas_presentacion/tarjetas_v3.html')}")
        page.wait_for_timeout(1000) 
        
        cards = ['d2-front', 'back-gold', 'back-white']
        for cid in cards:
            el = page.locator(f"#{cid}")
            # scale="device" combined with device_scale_factor=2 gives 4X total output size
            el.screenshot(path=f"tarjetas_presentacion/{cid}.png", scale="device")
            
        browser.close()

if __name__ == "__main__":
    render_cards()
    print("Render complete.")
