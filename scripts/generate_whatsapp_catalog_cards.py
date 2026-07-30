import os, sys, base64, asyncio
from playwright.async_api import async_playwright

async def generate_catalog_cards():
    brand_dir = os.path.join(os.getcwd(), "src", "web", "assets", "brand")
    fv_svg_path = os.path.join(brand_dir, "fv_logo_negativo.svg")
    altus_svg_path = os.path.join(brand_dir, "altus_ai_logo_negativo.svg")

    with open(fv_svg_path, "r", encoding="utf-8") as f:
        fv_svg = f.read()
    with open(altus_svg_path, "r", encoding="utf-8") as f:
        altus_svg = f.read()

    fv_b64 = base64.b64encode(fv_svg.encode("utf-8")).decode("utf-8")
    altus_b64 = base64.b64encode(altus_svg.encode("utf-8")).decode("utf-8")

    cards = [
        {
            "filename": "catalogo_1_apv.png",
            "tag": "PLANIFICACIÓN PREVISIONAL & BENEFICIO FISCAL",
            "title": "Asesoría en APV & Optimización Tributaria",
            "desc": "Aprovecha la bonificación estatal del 15% (Régimen A) o rebaja hasta 54 UF en tu impuesto global complementario (Régimen B).",
            "stats": [
                {"k": "+15%", "v": "Bonificación Fiscal Directa"},
                {"k": "hasta 54 UF", "v": "Rebaja Tributaria Anual"},
                {"k": "100%", "v": "Personalizado a tu tramo"}
            ],
            "accent": "#10b981"
        },
        {
            "filename": "catalogo_2_reliquidacion.png",
            "tag": "RECUPERACIÓN DE IMPUESTOS CMF / SII",
            "title": "Reliquidación Tributaria Global Complementario",
            "desc": "Recupera las retenciones en exceso por dividendos de créditos hipotecarios, gastos educacionales y aportes de APV.",
            "stats": [
                {"k": "Devolución", "v": "Directa a tu Cuenta Bancaria"},
                {"k": "Art. 55 bis", "v": "Intereses Crédito Hipotecario"},
                {"k": "Auditado", "v": "Sin riesgos ante el SII"}
            ],
            "accent": "#d97706"
        },
        {
            "filename": "catalogo_3_inmobiliario.png",
            "tag": "ARBITRAJE DE TASAS & ESTRATEGIA DE DEUDA",
            "title": "Evaluación Créditos vs Inversión Financiera",
            "desc": "Compara la rentabilidad real de un pie inmobiliario vs instrumentos financieros eficientes (Renta Fija / Renta Variable).",
            "stats": [
                {"k": "Simulador", "v": "Modelación Cuantitativa 4K"},
                {"k": "VAN / TIR", "v": "Evaluación Financiera Real"},
                {"k": "Tasa vs Renta", "v": "Arbitraje Patrimonial"}
            ],
            "accent": "#3b82f6"
        },
        {
            "filename": "catalogo_4_family_office.png",
            "tag": "MULTI-FAMILY OFFICE DIGITAL CON INTELIGENCIA ARTIFICIAL",
            "title": "Gestión Patrimonial Integral & Copilot AI",
            "desc": "Arquitectura de arquitectura abierta con monitoreo continuo de portafolios alimentada por el motor ALTUS AI.",
            "stats": [
                {"k": "Omni AI", "v": "Monitoreo 24/7 de Portafolios"},
                {"k": "Senior", "v": "Asesoría Experta de Partners"},
                {"k": "360°", "v": "Visión Consolidada de Activos"}
            ],
            "accent": "#8b5cf6"
        }
    ]

    output_dir = os.path.join(os.getcwd(), "assets", "whatsapp_catalog")
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        for c in cards:
            stats_html = "".join([f"""
            <div class="stat-box">
                <div class="stat-num" style="color: {c['accent']};">{s['k']}</div>
                <div class="stat-lbl">{s['v']}</div>
            </div>
            """ for s in c["stats"]])

            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            width: 1080px;
            height: 1080px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            font-family: 'Outfit', sans-serif;
            padding: 70px;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }}
        .bg-glow {{
            position: absolute;
            top: -200px;
            right: -200px;
            width: 700px;
            height: 700px;
            border-radius: 50%;
            background: radial-gradient(circle, {c['accent']}22 0%, transparent 70%);
            z-index: 1;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 2;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            padding-bottom: 30px;
        }}
        .header img.fv-logo {{
            height: 65px;
            width: auto;
        }}
        .header .tag {{
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 3px;
            color: {c['accent']};
            background: rgba(30, 41, 59, 0.8);
            padding: 10px 20px;
            border-radius: 30px;
            border: 1px solid {c['accent']}55;
        }}
        .content {{
            z-index: 2;
            margin-top: 20px;
        }}
        .title {{
            font-size: 52px;
            font-weight: 800;
            line-height: 1.15;
            color: #ffffff;
            margin-bottom: 20px;
            letter-spacing: -1px;
        }}
        .desc {{
            font-size: 26px;
            font-weight: 400;
            color: #cbd5e1;
            line-height: 1.45;
            margin-bottom: 40px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-box {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        .stat-num {{
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 8px;
        }}
        .stat-lbl {{
            font-size: 16px;
            color: #94a3b8;
            font-weight: 500;
            line-height: 1.2;
        }}
        .footer {{
            z-index: 2;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(217, 119, 6, 0.3);
            border-radius: 24px;
            padding: 24px 35px;
        }}
        .cta {{
            display: flex;
            flex-direction: column;
        }}
        .cta-main {{
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
        }}
        .cta-sub {{
            font-size: 16px;
            color: #d97706;
            font-weight: 600;
        }}
        .altus-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .altus-brand span {{
            font-size: 14px;
            font-weight: 600;
            color: #94a3b8;
            letter-spacing: 2px;
        }}
        .altus-brand img {{
            height: 28px;
            width: auto;
        }}
    </style>
</head>
<body>
    <div class="bg-glow"></div>
    <div class="header">
        <img class="fv-logo" src="data:image/svg+xml;base64,{fv_b64}" alt="FV Logo"/>
        <div class="tag">{c['tag']}</div>
    </div>
    
    <div class="content">
        <div class="title">{c['title']}</div>
        <div class="desc">{c['desc']}</div>
        <div class="stats-grid">
            {stats_html}
        </div>
    </div>

    <div class="footer">
        <div class="cta">
            <div class="cta-main">Solicita tu Evaluación Patrimonial Gratuita</div>
            <div class="cta-sub">💬 Escríbenos directamente por WhatsApp</div>
        </div>
        <div class="altus-brand">
            <span>POWERED BY</span>
            <img src="data:image/svg+xml;base64,{altus_b64}" alt="ALTUS AI"/>
        </div>
    </div>
</body>
</html>
"""
            page = await browser.new_page(viewport={"width": 1080, "height": 1080, "device_scale_factor": 2})
            await page.set_content(html_content)
            out_file = os.path.join(output_dir, c["filename"])
            await page.screenshot(path=out_file, type="png")
            print(f"Generated: {out_file}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(generate_catalog_cards())
