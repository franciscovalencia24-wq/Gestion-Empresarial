import base64
import os
from html2image import Html2Image

# Read Base64 logo
with open('base64_logo.txt', 'r') as f:
    b64_logo = f.read().strip()

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Infografía Megarreforma</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0d1321;
            --card-bg: #1d2d44;
            --accent-gold: #f0ebd8;
            --accent-gold-strong: #e5b154;
            --accent-cyan: #74b3ce;
            --text-main: #ffffff;
            --text-muted: #b0c4de;
        }}
        body {{
            margin: 0;
            padding: 0;
            width: 1080px;
            height: 1350px;
            zoom: 2;
            background: linear-gradient(135deg, var(--bg-color) 0%, #172a3a 100%);
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
            display: flex;
            flex-direction: column;
            box-sizing: border-box;
            position: relative;
        }}
        .header {{
            padding: 80px 80px 40px 80px;
            text-align: center;
        }}
        .tag {{
            background: var(--accent-gold-strong);
            color: #000;
            padding: 8px 16px;
            border-radius: 20px;
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 18px;
            text-transform: uppercase;
            letter-spacing: 2px;
            display: inline-block;
            margin-bottom: 20px;
        }}
        h1 {{
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 64px;
            margin: 0 0 20px 0;
            line-height: 1.1;
            background: -webkit-linear-gradient(45deg, #ffffff, var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{
            font-size: 26px;
            color: var(--text-muted);
            margin: 0;
            font-weight: 300;
            line-height: 1.4;
            padding: 0 40px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            padding: 0 80px;
            flex-grow: 1;
        }}
        .card {{
            background: rgba(29, 45, 68, 0.6);
            border: 1px solid rgba(116, 179, 206, 0.2);
            border-radius: 24px;
            padding: 40px;
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }}
        .card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 4px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-gold-strong));
        }}
        .card-icon {{
            font-size: 48px;
            margin-bottom: 20px;
        }}
        .card-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 32px;
            font-weight: 700;
            margin: 0 0 20px 0;
            color: var(--accent-gold);
        }}
        .card-list {{
            list-style: none;
            padding: 0;
            margin: 0 0 20px 0;
            font-size: 20px;
            line-height: 1.5;
            flex-grow: 1;
        }}
        .card-list li {{
            margin-bottom: 12px;
            padding-left: 30px;
            position: relative;
        }}
        .card-list li::before {{
            content: '→';
            position: absolute;
            left: 0;
            color: var(--accent-cyan);
            font-weight: bold;
        }}
        .opportunity {{
            background: rgba(229, 177, 84, 0.1);
            border-left: 4px solid var(--accent-gold-strong);
            padding: 15px 20px;
            border-radius: 0 12px 12px 0;
            font-size: 18px;
            font-weight: 500;
            color: #fff;
        }}
        .opportunity strong {{
            color: var(--accent-gold-strong);
        }}
        .footer {{
            padding: 60px 80px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255,255,255,0.05);
            margin-top: 40px;
        }}
        .cta {{
            font-family: 'Outfit', sans-serif;
            font-size: 24px;
            font-weight: 600;
            color: var(--accent-cyan);
            max-width: 600px;
        }}
        .logo {{
            height: 180px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="tag">ALERTA TRIBUTARIA 2026</div>
        <h1>Impacto de la Megarreforma en tu Patrimonio</h1>
        <p class="subtitle">La nueva Ley de Reconstrucción abre <b>ventanas temporales únicas</b>. Conoce las 4 medidas clave que redefinirán la estructuración patrimonial y cómo puedes aprovecharlas.</p>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-icon">🌍</div>
            <h2 class="card-title">1. Repatriación de Capitales</h2>
            <ul class="card-list">
                <li>Tasa única transitoria del <b>10%</b> para declarar bienes o rentas en el extranjero.</li>
                <li>La tasa <b>baja al 7%</b> si mantienes la inversión en Chile por 8 años en instrumentos específicos (DFL2, Art. 107).</li>
            </ul>
            <div class="opportunity">
                <strong>Oportunidad:</strong> Regulariza y trae tus activos al país con la tasa más baja históricamente disponible.
            </div>
        </div>

        <div class="card">
            <div class="card-icon">👨‍👩‍👧‍👦</div>
            <h2 class="card-title">2. Ley de Donaciones</h2>
            <ul class="card-list">
                <li>Rebaja transitoria del <b>50% al Impuesto a las Donaciones</b> para el círculo familiar directo.</li>
                <li>Válido solo por 1 año y se libera del engorroso trámite judicial de insinuación.</li>
            </ul>
            <div class="opportunity">
                <strong>Oportunidad:</strong> Es el mejor momento en décadas para planificar la herencia en vida y traspasar patrimonio.
            </div>
        </div>

        <div class="card">
            <div class="card-icon">🏢</div>
            <h2 class="card-title">3. Nuevo Régimen DFL2</h2>
            <ul class="card-list">
                <li>Se acaba la restricción de solo 2 viviendas favorecidas para rentistas.</li>
                <li><b>Impuesto único fijo del 5%</b> a las rentas de arriendo para la 3ra vivienda y siguientes (hasta 90 m2).</li>
            </ul>
            <div class="opportunity">
                <strong>Oportunidad:</strong> Fomenta la creación de un gran portafolio de renta inmobiliaria con carga tributaria baja y predecible.
            </div>
        </div>

        <div class="card">
            <div class="card-icon">📈</div>
            <h2 class="card-title">4. Inversiones Art. 107 LIR</h2>
            <ul class="card-list">
                <li>Exenciones sobre ganancias de capital en instrumentos de oferta pública local bajo ciertos requisitos.</li>
                <li>Vehículo ideal para inyectar los capitales repatriados y acceder a la tasa del 7%.</li>
            </ul>
            <div class="opportunity">
                <strong>Oportunidad:</strong> Estructurar portafolios a través de Fondos Mutuos o de Inversión locales optimizando el impacto fiscal.
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="cta">
            Las ventanas de oportunidad son transitorias.<br>
            <span style="color: #fff; font-weight: 300;">Anticípate y asesórate hoy para blindar y hacer crecer tu patrimonio.</span>
        </div>
        <img class="logo" src="data:image/svg+xml;base64,{b64_logo}" alt="Logo FV">
    </div>
</body>
</html>
"""

with open('infografia.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

hti = Html2Image(size=(2160, 2700))
hti.screenshot(html_file='infografia.html', save_as='infografia_megarreforma.png')
print("Infografía generada exitosamente.")
