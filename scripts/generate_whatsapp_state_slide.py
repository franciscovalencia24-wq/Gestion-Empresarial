import os, sys, base64, asyncio
from playwright.async_api import async_playwright

async def generate_whatsapp_state(title="APV & Reliquidación Tributaria", topic="Optimización de Impuestos 2026", bullet1="Gana hasta 15% de Bonificación Fiscal Directa con Régimen A", bullet2="Rebaja hasta 54 UF anuales de Impuesto Global Complementario en Régimen B", bullet3="Recupera retenciones por crédito hipotecario de dividendos", cta="Escríbeme por WhatsApp para evaluar tu tramo tributario sin costo.", filename="estado_whatsapp_1.png"):
    brand_dir = os.path.join(os.getcwd(), "src", "web", "assets", "brand")
    fv_svg_path = os.path.join(brand_dir, "fv_logo_negativo.svg")
    altus_svg_path = os.path.join(brand_dir, "altus_ai_logo_principal.svg")

    with open(fv_svg_path, "r", encoding="utf-8") as f:
        fv_svg = f.read()
    with open(altus_svg_path, "r", encoding="utf-8") as f:
        altus_svg = f.read()

    fv_b64 = base64.b64encode(fv_svg.encode("utf-8")).decode("utf-8")
    altus_b64 = base64.b64encode(altus_svg.encode("utf-8")).decode("utf-8")

    # Render at 2160x3840px 4K Ultra HD (2x 1080x1920)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&family=Inter:wght@400;500;600;700&display=swap');
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            width: 2160px;
            height: 3840px;
            background: linear-gradient(180deg, #020617 0%, #0f172a 40%, #1e293b 100%);
            font-family: 'Outfit', sans-serif;
            padding: 180px 140px;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }}
        .bg-glow-1 {{
            position: absolute;
            top: -200px;
            right: -200px;
            width: 1600px;
            height: 1600px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.22) 0%, transparent 70%);
            z-index: 1;
        }}
        .bg-glow-2 {{
            position: absolute;
            bottom: 400px;
            left: -400px;
            width: 1800px;
            height: 1800px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(245, 158, 11, 0.18) 0%, transparent 70%);
            z-index: 1;
        }}
        .header {{
            z-index: 2;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid rgba(255,255,255,0.15);
            padding-bottom: 70px;
        }}
        .header img.fv-logo {{
            height: 170px;
            width: auto;
            filter: drop-shadow(0 10px 20px rgba(0,0,0,0.6));
        }}
        .tag {{
            font-size: 34px;
            font-weight: 800;
            letter-spacing: 6px;
            color: #10b981;
            background: rgba(16, 185, 129, 0.12);
            padding: 24px 50px;
            border-radius: 60px;
            border: 2px solid rgba(16, 185, 129, 0.45);
            text-transform: uppercase;
        }}
        .hero {{
            z-index: 2;
            margin-top: 60px;
        }}
        .topic {{
            font-size: 44px;
            font-weight: 800;
            color: #f59e0b;
            letter-spacing: 8px;
            text-transform: uppercase;
            margin-bottom: 35px;
        }}
        .title {{
            font-size: 120px;
            font-weight: 900;
            line-height: 1.15;
            color: #ffffff;
            letter-spacing: -3px;
            margin-bottom: 100px;
            text-shadow: 0 15px 40px rgba(0,0,0,0.6);
        }}
        .card-box {{
            z-index: 2;
            background: rgba(15, 23, 42, 0.85);
            border: 3px solid rgba(255,255,255,0.15);
            border-radius: 60px;
            padding: 90px;
            backdrop-filter: blur(30px);
            box-shadow: 0 30px 80px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            gap: 65px;
        }}
        .bullet-item {{
            display: flex;
            align-items: flex-start;
            gap: 45px;
        }}
        .bullet-icon {{
            font-size: 64px;
            background: rgba(16, 185, 129, 0.18);
            color: #10b981;
            width: 120px;
            height: 120px;
            border-radius: 36px;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
            border: 2px solid rgba(16, 185, 129, 0.4);
        }}
        .bullet-text {{
            font-size: 48px;
            color: #e2e8f0;
            font-weight: 500;
            line-height: 1.4;
        }}
        .footer {{
            z-index: 2;
            display: flex;
            flex-direction: column;
            gap: 50px;
        }}
        .cta-card {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(16, 185, 129, 0.25) 100%);
            border: 4px solid #f59e0b;
            border-radius: 50px;
            padding: 70px;
            text-align: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        }}
        .cta-title {{
            font-size: 56px;
            font-weight: 900;
            color: #ffffff;
            margin-bottom: 16px;
        }}
        .cta-sub {{
            font-size: 38px;
            color: #e2e8f0;
            font-weight: 600;
        }}
        .brand-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }}
        .author {{
            font-size: 38px;
            color: #94a3b8;
            font-weight: 600;
        }}
        .author b {{
            color: #ffffff;
        }}
        .altus-tag {{
            display: flex;
            align-items: center;
            gap: 20px;
            background: rgba(30, 41, 59, 0.85);
            padding: 16px 40px;
            border-radius: 50px;
            border: 2px solid #f59e0b;
        }}
        .altus-tag .p-lbl {{
            font-size: 24px;
            font-weight: 800;
            color: #94a3b8;
            letter-spacing: 4px;
        }}
        .altus-tag img {{
            height: 50px;
            width: auto;
        }}
        .altus-tag .a-txt {{
            font-size: 34px;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: 2px;
        }}
    </style>
</head>
<body>
    <div class="bg-glow-1"></div>
    <div class="bg-glow-2"></div>

    <div class="header">
        <img class="fv-logo" src="data:image/svg+xml;base64,{fv_b64}" alt="FV Logo"/>
        <div class="tag">💡 ESTADO WHATSAPP</div>
    </div>

    <div class="hero">
        <div class="topic">📈 {topic}</div>
        <div class="title">{title}</div>

        <div class="card-box">
            <div class="bullet-item">
                <div class="bullet-icon">💡</div>
                <div class="bullet-text">{bullet1}</div>
            </div>
            <div class="bullet-item">
                <div class="bullet-icon">📊</div>
                <div class="bullet-text">{bullet2}</div>
            </div>
            <div class="bullet-item">
                <div class="bullet-icon">🎯</div>
                <div class="bullet-text">{bullet3}</div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="cta-card">
            <div class="cta-title">💬 {cta}</div>
            <div class="cta-sub">FV Asesorías e Inversiones • Senior Family Office</div>
        </div>
        <div class="brand-row">
            <div class="author"><b>Francisco Valencia</b> | Managing Partner</div>
            <div class="altus-tag">
                <span class="p-lbl">POWERED BY</span>
                <img src="data:image/svg+xml;base64,{altus_b64}" alt="ALTUS AI"/>
                <span class="a-txt">ALTUS AI</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

    output_dir = os.path.join(os.getcwd(), "assets", "whatsapp_status")
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, filename)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 2160, "height": 3840, "device_scale_factor": 1})
        await page.set_content(html_content)
        await page.screenshot(path=out_file, type="png")
        await browser.close()

    print(f"Generated 4K WhatsApp State: {out_file}")

if __name__ == "__main__":
    asyncio.run(generate_whatsapp_state())
