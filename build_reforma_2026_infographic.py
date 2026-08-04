import os
import shutil
import base64
from html2image import Html2Image

# Cargar logos vectoriales en Base64
with open('base64_fv_negativo.txt', 'r') as f:
    b64_logo_fv = f.read().strip()

with open('base64_altus_negativo.txt', 'r') as f:
    b64_logo_altus = f.read().strip()

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Infografía Reforma Tributaria 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        :root {{
            --bg-gradient: linear-gradient(135deg, #070c18 0%, #0d172a 40%, #111d35 100%);
            --card-bg: rgba(18, 30, 52, 0.85);
            --card-border: rgba(229, 177, 84, 0.28);
            --gold-main: #e5b154;
            --gold-light: #f0ebd8;
            --cyan-bright: #38bdf8;
            --cyan-glow: rgba(56, 189, 248, 0.15);
            --text-main: #ffffff;
            --text-muted: #94a3b8;
            --text-sub: #cbd5e1;
        }}
        body {{
            width: 1080px;
            height: 1350px;
            zoom: 2;
            background: var(--bg-gradient);
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 35px 50px 30px 50px;
            position: relative;
            overflow: hidden;
        }}
        
        /* Glow Accents Background */
        .bg-glow-1 {{
            position: absolute;
            top: -100px;
            right: -100px;
            width: 550px;
            height: 550px;
            background: radial-gradient(circle, rgba(229, 177, 84, 0.15) 0%, rgba(0,0,0,0) 70%);
            pointer-events: none;
        }}
        .bg-glow-2 {{
            position: absolute;
            bottom: -100px;
            left: -100px;
            width: 550px;
            height: 550px;
            background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, rgba(0,0,0,0) 70%);
            pointer-events: none;
        }}

        /* Header (Compact & High-Impact) */
        .header {{
            text-align: center;
            position: relative;
            z-index: 2;
            margin-bottom: 15px;
        }}
        .tag {{
            background: linear-gradient(90deg, #e5b154 0%, #f3c77c 100%);
            color: #070c18;
            padding: 6px 20px;
            border-radius: 30px;
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 13.5px;
            text-transform: uppercase;
            letter-spacing: 2.5px;
            display: inline-block;
            margin-bottom: 10px;
            box-shadow: 0 4px 15px rgba(229, 177, 84, 0.35);
        }}
        h1 {{
            font-family: 'Outfit', sans-serif;
            font-weight: 900;
            font-size: 44px;
            line-height: 1.08;
            margin-bottom: 8px;
            background: linear-gradient(180deg, #ffffff 0%, #e2e8f0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }}
        .subtitle {{
            font-size: 16.5px;
            color: var(--text-muted);
            font-weight: 400;
            max-width: 900px;
            margin: 0 auto;
            line-height: 1.35;
        }}

        /* Grid */
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
            position: relative;
            z-index: 2;
            flex-grow: 1;
            align-content: stretch;
            margin: 10px 0;
        }}

        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 24px 26px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            backdrop-filter: blur(12px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
            position: relative;
            overflow: hidden;
        }}
        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 5px;
            height: 100%;
            background: var(--gold-main);
        }}
        .card.highlight::before {{
            background: var(--cyan-bright);
        }}

        .card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        .card-title {{
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 20px;
            color: var(--gold-light);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .badge {{
            font-size: 11.5px;
            font-weight: 800;
            padding: 4px 12px;
            border-radius: 12px;
            background: rgba(229, 177, 84, 0.18);
            color: var(--gold-main);
            border: 1px solid rgba(229, 177, 84, 0.35);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .badge.cyan {{
            background: rgba(56, 189, 248, 0.18);
            color: var(--cyan-bright);
            border-color: rgba(56, 189, 248, 0.35);
        }}

        .stat-container {{
            display: flex;
            align-items: baseline;
            gap: 12px;
            margin: 8px 0 10px 0;
        }}
        .stat-value {{
            font-family: 'Outfit', sans-serif;
            font-weight: 900;
            font-size: 36px;
            color: #ffffff;
            line-height: 1;
        }}
        .stat-value.gold {{
            color: var(--gold-main);
        }}
        .stat-value.cyan {{
            color: var(--cyan-bright);
        }}
        .stat-label {{
            font-size: 13.5px;
            color: var(--text-sub);
            font-weight: 500;
            line-height: 1.25;
        }}

        .card-body {{
            font-size: 14px;
            color: var(--text-sub);
            line-height: 1.45;
            margin-bottom: 12px;
        }}
        .card-body ul {{
            list-style: none;
            padding-left: 0;
        }}
        .card-body li {{
            position: relative;
            padding-left: 18px;
            margin-bottom: 6px;
        }}
        .card-body li::before {{
            content: '•';
            position: absolute;
            left: 0;
            color: var(--gold-main);
            font-size: 18px;
            top: -2px;
        }}

        .takeaway {{
            background: rgba(15, 23, 42, 0.75);
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 12.5px;
            color: var(--gold-light);
            border-left: 3px solid var(--gold-main);
            font-weight: 500;
            line-height: 1.35;
        }}
        .takeaway.cyan-border {{
            border-left-color: var(--cyan-bright);
        }}

        /* Footer & Logos (ALTUS IS EXACTLY 10% SMALLER THAN FV: 90px vs 81px) */
        .footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 18px;
            border-top: 1.5px solid rgba(229, 177, 84, 0.3);
            position: relative;
            z-index: 2;
        }}
        .author-info {{
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        .author-name {{
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 20px;
            color: #ffffff;
            letter-spacing: 0.2px;
        }}
        .author-title {{
            font-size: 14px;
            color: var(--gold-main);
            font-weight: 700;
            letter-spacing: 0.3px;
        }}
        .author-contact {{
            font-size: 12.5px;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        /* LOGO ALTUS EXACTAMENTE UN 10% MÁS PEQUEÑO QUE FV (FV: 90px, ALTUS: 81px) */
        .logos-wrapper {{
            display: flex;
            align-items: center;
            gap: 32px;
        }}
        .logo-fv {{
            height: 90px;
            width: auto;
            filter: drop-shadow(0 4px 12px rgba(0,0,0,0.6));
        }}
        .logo-altus {{
            height: 81px;
            width: auto;
            opacity: 0.95;
        }}
        .logo-divider {{
            width: 1.5px;
            height: 75px;
            background: rgba(255,255,255,0.25);
        }}
    </style>
</head>
<body>
    <div class="bg-glow-1"></div>
    <div class="bg-glow-2"></div>

    <!-- Header -->
    <div class="header">
        <div class="tag">REFORMA TRIBUTARIA CHILE 2026</div>
        <h1>CAMBIOS, OPORTUNIDADES Y DECISIONES CLAVE</h1>
        <p class="subtitle">Análisis Estratégico de Impacto en Empresas, Mercado de Capitales y Patrimonio Familiar</p>
    </div>

    <!-- 6 Core Pillars Grid -->
    <div class="grid">
        <!-- 1. Impuesto Corporativo -->
        <div class="card">
            <div>
                <div class="card-header">
                    <div class="card-title">🏢 Impuesto 1ª Categoría</div>
                    <div class="badge">Rebaja Gradual</div>
                </div>
                <div class="stat-container">
                    <div class="stat-value gold">23%</div>
                    <div class="stat-label">Tasa General al 2029<br>(2027: 25.5%)</div>
                </div>
                <div class="card-body">
                    <ul>
                        <li>Reducción gradual desde la tasa actual del 27%.</li>
                        <li>Exige revisar cierres de año, políticas de dividendos y depreciación acelerada.</li>
                    </ul>
                </div>
            </div>
            <div class="takeaway">
                💡 <strong>Clave:</strong> Evaluar conveniencia de acumular o retirar créditos tributarios.
            </div>
        </div>

        <!-- 2. Mercado de Capitales -->
        <div class="card highlight">
            <div>
                <div class="card-header">
                    <div class="card-title">📈 Mercado de Capitales</div>
                    <div class="badge cyan">Art. 107 LIR</div>
                </div>
                <div class="stat-container">
                    <div class="stat-value cyan">0%</div>
                    <div class="stat-label">Ingreso No Renta<br>(Desde Ene 2027)</div>
                </div>
                <div class="card-body">
                    <ul>
                        <li>Reemplaza el impuesto único del 10% en venta de acciones y cuotas con presencia bursátil.</li>
                        <li>Beneficio para personas naturales, Fondos e Inversionistas.</li>
                    </ul>
                </div>
            </div>
            <div class="takeaway cyan-border">
                💡 <strong>Clave:</strong> Reestructurar portafolios bursátiles antes de la entrada en vigencia.
            </div>
        </div>

        <!-- 3. Donaciones & Sucesión -->
        <div class="card">
            <div>
                <div class="card-header">
                    <div class="card-title">🎁 Sucesión & Donaciones</div>
                    <div class="badge">Ventana 1 Año</div>
                </div>
                <div class="stat-container">
                    <div class="stat-value gold">-50%</div>
                    <div class="stat-label">Rebaja en Impuesto<br>a las Donaciones</div>
                </div>
                <div class="card-body">
                    <ul>
                        <li>Ventana transitoria por 1 sola vez para donar a legitimarios.</li>
                        <li>Sin trámite de insinuación judicial (Límite: 50% del patrimonio del donante).</li>
                    </ul>
                </div>
            </div>
            <div class="takeaway">
                💡 <strong>Clave:</strong> Oportunidad única para adelantar la sucesión familiar de forma ordenada.
            </div>
        </div>

        <!-- 4. Integración del Sistema -->
        <div class="card highlight">
            <div>
                <div class="card-header">
                    <div class="card-title">🔄 Integración Tributaria</div>
                    <div class="badge cyan">Sin Restitución</div>
                </div>
                <div class="stat-container">
                    <div class="stat-value cyan">100%</div>
                    <div class="stat-label">Crédito IDPC<br>Aprovechable</div>
                </div>
                <div class="card-body">
                    <ul>
                        <li>Eliminación gradual del débito de 35% de restitución del crédito por IDPC.</li>
                        <li>Reduce significativamente el costo efectivo de retirar o remesar utilidades.</li>
                    </ul>
                </div>
            </div>
            <div class="takeaway cyan-border">
                💡 <strong>Clave:</strong> Impacto directo en flujo de caja de retiros y dividendos familiares.
            </div>
        </div>

        <!-- 5. Patrimonio Inmobiliario -->
        <div class="card">
            <div>
                <div class="card-header">
                    <div class="card-title">🏠 Bienes Raíces & DFL 2</div>
                    <div class="badge">Nuevo Régimen</div>
                </div>
                <div class="stat-container">
                    <div class="stat-value gold">5%</div>
                    <div class="stat-label">Impuesto Único Arriendo<br>(Desde 3ª Vivienda)</div>
                </div>
                <div class="card-body">
                    <ul>
                        <li>DFL 2 se limita a las 2 propiedades más antiguas. Desde la 3ª, tasa fija 5% bruto.</li>
                        <li>Exención 100% de contribuciones para vivienda principal (65+ años).</li>
                    </ul>
                </div>
            </div>
            <div class="takeaway">
                💡 <strong>Clave:</strong> Revaluar rentabilidad neta de carteras habitacionales en arriendo.
            </div>
        </div>

        <!-- 6. Bienes en el Extranjero -->
        <div class="card highlight">
            <div>
                <div class="card-header">
                    <div class="card-title">🌐 Activos Internacionales</div>
                    <div class="badge cyan">Ventana 12 Meses</div>
                </div>
                <div class="stat-container">
                    <div class="stat-value cyan">10%</div>
                    <div class="stat-label">Impuesto Sustitutivo<br>(Regularización)</div>
                </div>
                <div class="card-body">
                    <ul>
                        <li>Declaración voluntaria extraordinaria de cuentas, inmuebles, trusts y criptoactivos.</li>
                        <li>Condonación de multas/intereses históricas (100% pago contado).</li>
                    </ul>
                </div>
            </div>
            <div class="takeaway cyan-border">
                💡 <strong>Clave:</strong> Diagnóstico preventivo de trazabilidad y prescripción contingente.
            </div>
        </div>
    </div>

    <!-- Footer -->
    <div class="footer">
        <div class="author-info">
            <div class="author-name">Francisco Valencia</div>
            <div class="author-title">Managing Partner | Asesor Financiero Senior</div>
            <div class="author-contact">📩 contacto@fv-inversiones.com &nbsp;•&nbsp; 📱 +56 9 6677 9662</div>
        </div>
        <div class="logos-wrapper">
            <img class="logo-fv" src="data:image/svg+xml;base64,{b64_logo_fv}" alt="Logo FV">
            <div class="logo-divider"></div>
            <img class="logo-altus" src="data:image/svg+xml;base64,{b64_logo_altus}" alt="Logo Altus">
        </div>
    </div>
</body>
</html>
"""

html_filename = 'infografia_reforma_2026.html'
png_filename = 'infografia_reforma_2026.png'

with open(html_filename, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML guardado en {html_filename}")

# Renderizar a PNG 4K con Html2Image (2160x2700 px)
hti = Html2Image(size=(2160, 2700))
hti.screenshot(html_file=html_filename, save_as=png_filename)
print(f"Imagen PNG 4K generada en {png_filename}")

# Copiar al directorio de artefactos
artifact_dir = r"C:\Users\franc\.gemini\antigravity-ide\brain\e0a740f0-6d0f-448b-98b0-162b61f9b6b0"
artifact_dest = os.path.join(artifact_dir, png_filename)
shutil.copy2(png_filename, artifact_dest)
print(f"Copiado exitosamente a artefactos: {artifact_dest}")
