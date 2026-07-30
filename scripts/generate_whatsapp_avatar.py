import os, sys, base64, asyncio
from playwright.async_api import async_playwright

async def generate_avatar():
    brand_dir = os.path.join(os.getcwd(), "src", "web", "assets", "brand")
    svg_path = os.path.join(brand_dir, "fv_logo_negativo.svg")

    with open(svg_path, "r", encoding="utf-8") as f:
        fv_svg = f.read()

    fv_b64 = base64.b64encode(fv_svg.encode("utf-8")).decode("utf-8")

    # Render at 2160x2160px 4K Ultra HD
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800;900&family=Inter:wght@400;600;700&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            width: 2160px;
            height: 2160px;
            background: radial-gradient(circle at center, #0f172a 0%, #060b18 55%, #020617 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Outfit', sans-serif;
            overflow: hidden;
            position: relative;
        }}

        /* Gold & Emerald Radial Glow */
        .glow {{
            position: absolute;
            width: 1750px;
            height: 1750px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, rgba(245, 158, 11, 0.15) 45%, transparent 70%);
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
            padding: 100px;
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(25px);
            box-shadow: inset 0 0 140px rgba(0, 0, 0, 0.85), 0 0 100px rgba(245, 158, 11, 0.3);
            border: 6px solid rgba(245, 158, 11, 0.65);
        }}

        .logo-container {{
            width: 1650px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 65px;
        }}

        .logo-container img {{
            width: 100%;
            height: auto;
            max-height: 850px;
            filter: drop-shadow(0 35px 60px rgba(0, 0, 0, 0.9));
        }}

        .badge-text {{
            font-size: 68px;
            font-weight: 900;
            letter-spacing: 12px;
            color: #f59e0b;
            text-transform: uppercase;
            margin-top: 10px;
            text-shadow: 0 8px 24px rgba(0,0,0,0.95);
        }}

        .subtext {{
            font-size: 52px;
            font-weight: 800;
            letter-spacing: 9px;
            color: #ffffff;
            text-transform: uppercase;
            margin-top: 18px;
            text-shadow: 0 6px 18px rgba(0,0,0,0.9);
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
        <div class="subtext">DIGITAL FAMILY OFFICE</div>
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

    print(f"Created Clean 4K Avatar (DIGITAL FAMILY OFFICE): {avatar_file}")

if __name__ == "__main__":
    asyncio.run(generate_avatar())
