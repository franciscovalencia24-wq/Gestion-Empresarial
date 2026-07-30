import os, sys, base64, asyncio
from playwright.async_api import async_playwright

async def generate_whatsapp_state(title="APV & Reliquidación Tributaria", topic="Optimización de Impuestos 2026", bullet1="Gana hasta 15% de Bonificación Fiscal Directa con Régimen A", bullet2="Rebaja hasta 54 UF anuales de Impuesto Global Complementario en Régimen B", bullet3="Recupera retenciones por crédito hipotecario de dividendos", cta="Escríbeme por WhatsApp para evaluar tu tramo tributario sin costo.", filename="estado_whatsapp_1.png"):
    brand_dir = os.path.join(os.getcwd(), "src", "web", "assets", "brand")
    fv_svg_path = os.path.join(brand_dir, "fv_logo_negativo.svg")
    altus_svg_path = os.path.join(brand_dir, "altus_ai_logo_negativo.svg")

    with open(fv_svg_path, "r", encoding="utf-8") as f:
        fv_svg = f.read()
    with open(altus_svg_path, "r", encoding="utf-8") as f:
        altus_svg = f.read()

    fv_b64 = base64.b64encode(fv_svg.encode("utf-8")).decode("utf-8")
    altus_b64 = base64.b64encode(altus_svg.encode("utf-8")).decode("utf-8")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            width: 1080px;
            height: 1920px;
            background: linear-gradient(180deg, #020617 0%, #0f172a 40%, #1e293b 100%);
            font-family: 'Outfit', sans-serif;
            padding: 100px 80px;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }}
        .bg-glow-1 {{
            position: absolute;
            top: -100px;
            right: -100px;
            width: 800px;
            height: 800px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, transparent 70%);
            z-index: 1;
        }}
        .bg-glow-2 {{
            position: absolute;
            bottom: 200px;
            left: -200px;
            width: 900px;
            height: 900px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(217, 119, 6, 0.15) 0%, transparent 70%);
            z-index: 1;
        }}
        .header {{
            z-index: 2;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            padding-bottom: 40px;
        }}
        .header img.fv-logo {{
            height: 85px;
            width: auto;
        }}
        .tag {{
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 4px;
            color: #10b981;
            background: rgba(16, 185, 129, 0.1);
            padding: 14px 28px;
            border-radius: 40px;
            border: 1px solid rgba(16, 185, 129, 0.4);
            text-transform: uppercase;
        }}
        .hero {{
            z-index: 2;
            margin-top: 40px;
        }}
        .topic {{
            font-size: 24px;
            font-weight: 700;
            color: #d97706;
            letter-spacing: 5px;
            text-transform: uppercase;
            margin-bottom: 20px;
        }}
        .title {{
            font-size: 68px;
            font-weight: 800;
            line-height: 1.15;
            color: #ffffff;
            letter-spacing: -1.5px;
            margin-bottom: 60px;
            text-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        .card-box {{
            z-index: 2;
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 36px;
            padding: 50px;
            backdrop-filter: blur(20px);
            box-shadow: 0 20px 50px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            gap: 35px;
        }}
        .bullet-item {{
            display: flex;
            align-items: flex-start;
            gap: 25px;
        }}
        .bullet-icon {{
            font-size: 36px;
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            width: 70px;
            height: 70px;
            border-radius: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        .bullet-text {{
            font-size: 28px;
            color: #e2e8f0;
            font-weight: 500;
            line-height: 1.4;
        }}
        .footer {{
            z-index: 2;
            display: flex;
            flex-direction: column;
            gap: 30px;
        }}
        .cta-card {{
            background: linear-gradient(135deg, rgba(217, 119, 6, 0.2) 0%, rgba(16, 185, 129, 0.2) 100%);
            border: 2px solid #d97706;
            border-radius: 30px;
            padding: 40px;
            text-align: center;
        }}
        .cta-title {{
            font-size: 32px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 10px;
        }}
        .cta-sub {{
            font-size: 22px;
            color: #cbd5e1;
            font-weight: 500;
        }}
        .brand-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 10px;
        }}
        .author {{
            font-size: 22px;
            color: #94a3b8;
            font-weight: 600;
        }}
        .author b {{
            color: #ffffff;
        }}
        .altus-tag {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .altus-tag span {{
            font-size: 16px;
            font-weight: 600;
            color: #94a3b8;
            letter-spacing: 2px;
        }}
        .altus-tag img {{
            height: 32px;
            width: auto;
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
                <span>POWERED BY</span>
                <img src="data:image/svg+xml;base64,{altus_b64}" alt="ALTUS AI"/>
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
        page = await browser.new_page(viewport={"width": 1080, "height": 1920, "device_scale_factor": 2})
        await page.set_content(html_content)
        await page.screenshot(path=out_file, type="png")
        await browser.close()

    print(f"Generated WhatsApp State: {out_file}")

if __name__ == "__main__":
    asyncio.run(generate_whatsapp_state())
