import os, sys, base64, asyncio
from playwright.async_api import async_playwright

async def generate_avatar():
    brand_dir = os.path.join(os.getcwd(), "src", "web", "assets", "brand")
    svg_path = os.path.join(brand_dir, "fv_logo_negativo.svg")
    altus_svg_path = os.path.join(brand_dir, "altus_ai_logo_negativo.svg")

    with open(svg_path, "r", encoding="utf-8") as f:
        fv_svg = f.read()

    with open(altus_svg_path, "r", encoding="utf-8") as f:
        altus_svg = f.read()

    # Convert SVGs to base64
    fv_b64 = base64.b64encode(fv_svg.encode("utf-8")).decode("utf-8")
    altus_b64 = base64.b64encode(altus_svg.encode("utf-8")).decode("utf-8")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            width: 1080px;
            height: 1080px;
            background: radial-gradient(circle at center, #1e293b 0%, #0f172a 70%, #020617 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Outfit', sans-serif;
            overflow: hidden;
            position: relative;
        }}

        /* Subtle Gold & Teal Radial Glow */
        .glow {{
            position: absolute;
            width: 800px;
            height: 800px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, rgba(217, 119, 6, 0.1) 40%, transparent 70%);
            z-index: 1;
        }}

        /* Circular Safe Guide Line */
        .safe-circle {{
            width: 960px;
            height: 960px;
            border-radius: 50%;
            border: 2px solid rgba(217, 119, 6, 0.3);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 2;
            padding: 80px;
            background: rgba(15, 23, 42, 0.4);
            backdrop-filter: blur(10px);
            box-shadow: inset 0 0 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(16, 185, 129, 0.1);
        }}

        .logo-container {{
            width: 720px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
        }}

        .logo-container img {{
            width: 100%;
            height: auto;
            max-height: 480px;
            filter: drop-shadow(0 15px 25px rgba(0, 0, 0, 0.6));
        }}

        .badge-text {{
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 6px;
            color: #d97706;
            text-transform: uppercase;
            margin-top: 10px;
            text-shadow: 0 4px 12px rgba(0,0,0,0.8);
        }}

        .subtext {{
            font-size: 20px;
            font-weight: 500;
            letter-spacing: 3px;
            color: #94a3b8;
            text-transform: uppercase;
            margin-top: 6px;
        }}

        .altus-tag {{
            margin-top: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(30, 41, 59, 0.8);
            padding: 8px 24px;
            border-radius: 30px;
            border: 1px solid rgba(217, 119, 6, 0.4);
        }}

        .altus-tag span {{
            font-size: 16px;
            font-weight: 600;
            color: #cbd5e1;
            letter-spacing: 2px;
        }}

        .altus-tag img {{
            height: 24px;
            width: auto;
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
            <span>POWERED BY</span>
            <img src="data:image/svg+xml;base64,{altus_b64}" alt="ALTUS AI"/>
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
        page = await browser.new_page(viewport={"width": 1080, "height": 1080, "device_scale_factor": 2})
        await page.set_content(html_content)
        await page.screenshot(path=avatar_file, type="png")
        await browser.close()

    print(f"✅ Created WhatsApp Avatar Image: {avatar_file}")

if __name__ == "__main__":
    asyncio.run(generate_avatar())
