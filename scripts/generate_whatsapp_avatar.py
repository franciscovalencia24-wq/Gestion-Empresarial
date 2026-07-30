import os, sys, base64, asyncio
from playwright.async_api import async_playwright

async def generate_avatar():
    brand_dir = os.path.join(os.getcwd(), "src", "web", "assets", "brand")
    svg_path = os.path.join(brand_dir, "fv_logo_negativo.svg")
    altus_svg_path = os.path.join(brand_dir, "altus_ai_logo_principal.svg")

    with open(svg_path, "r", encoding="utf-8") as f:
        fv_svg = f.read()

    with open(altus_svg_path, "r", encoding="utf-8") as f:
        altus_svg = f.read()

    fv_b64 = base64.b64encode(fv_svg.encode("utf-8")).decode("utf-8")
    altus_b64 = base64.b64encode(altus_svg.encode("utf-8")).decode("utf-8")

    # 4K Ultra HD 2160x2160 resolution rendering
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&family=Inter:wght@400;600;700&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            width: 2160px;
            height: 2160px;
            background: radial-gradient(circle at center, #0f172a 0%, #080d1a 60%, #020617 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Outfit', sans-serif;
            overflow: hidden;
            position: relative;
        }}

        /* Subtle Gold Glow Background */
        .glow {{
            position: absolute;
            width: 1800px;
            height: 1800px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.18) 0%, rgba(245, 158, 11, 0.15) 50%, transparent 70%);
            z-index: 1;
        }}

        /* Safe Circle Container for WhatsApp Avatar */
        .safe-circle {{
            width: 1960px;
            height: 1960px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 2;
            padding: 90px;
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(25px);
            box-shadow: inset 0 0 140px rgba(0, 0, 0, 0.8), 0 0 100px rgba(245, 158, 11, 0.25);
            border: 5px solid rgba(245, 158, 11, 0.6);
        }}

        .logo-container {{
            width: 1600px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 45px;
        }}

        .logo-container img {{
            width: 100%;
            height: auto;
            max-height: 800px;
            filter: drop-shadow(0 30px 50px rgba(0, 0, 0, 0.85));
        }}

        .badge-text {{
            font-size: 64px;
            font-weight: 900;
            letter-spacing: 12px;
            color: #f59e0b;
            text-transform: uppercase;
            margin-top: 10px;
            text-shadow: 0 8px 24px rgba(0,0,0,0.95);
        }}

        .subtext {{
            font-size: 44px;
            font-weight: 700;
            letter-spacing: 7px;
            color: #f8fafc;
            text-transform: uppercase;
            margin-top: 14px;
        }}

        /* Highly Prominent Altus AI Tag */
        .altus-tag {{
            margin-top: 65px;
            display: flex;
            align-items: center;
            gap: 26px;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
            padding: 28px 70px;
            border-radius: 70px;
            border: 4px solid #f59e0b;
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.75), 0 0 35px rgba(245, 158, 11, 0.4);
        }}

        .altus-tag .powered-label {{
            font-size: 34px;
            font-weight: 800;
            color: #94a3b8;
            letter-spacing: 5px;
            text-transform: uppercase;
        }}

        .altus-tag img.altus-icon {{
            height: 80px;
            width: auto;
            filter: drop-shadow(0 4px 12px rgba(0,0,0,0.6));
        }}

        .altus-tag .altus-name {{
            font-size: 50px;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: 4px;
            font-family: 'Outfit', sans-serif;
            text-shadow: 0 4px 14px rgba(0,0,0,0.9);
        }}
    </style>
</head>
<body>
    <div class="glow"></div>
    <div class="safe-circle">
        <div class="logo-container">
            <img src="data:image/svg+xml;base64,{fv_b64}" alt="FV Logo"/>
        </div>
        <div class="badge-text">ASESORÍA PATRIMONIAL</div>
        <div class="subtext">SENIOR FAMILY OFFICE</div>
        <div class="altus-tag">
            <span class="powered-label">POWERED BY</span>
            <img src="data:image/svg+xml;base64,{altus_b64}" alt="ALTUS AI Emblem" class="altus-icon"/>
            <span class="altus-name">ALTUS AI</span>
        </div>
    </div>
</body>
</html>
"""

    output_dir = os.path.join(os.getcwd(), "assets", "whatsapp")
    os.makedirs(output_dir, exist_ok=True)
    avatar_file = os.path.join(output_dir, "perfil_whatsapp_fv_oficial.png")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 2160, "height": 2160, "device_scale_factor": 1})
        await page.set_content(html_content)
        await page.screenshot(path=avatar_file, type="png")
        await browser.close()

    print(f"Created 4K Avatar: {avatar_file}")

if __name__ == "__main__":
    asyncio.run(generate_avatar())
