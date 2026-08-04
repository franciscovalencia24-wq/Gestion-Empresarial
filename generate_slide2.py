import base64
import os
import shutil
from html2image import Html2Image

# Read Base64 logos (Negative/White versions)
with open('base64_fv_negativo.txt', 'r') as f:
    b64_logo_fv = f.read().strip()

with open('base64_altus_negativo.txt', 'r') as f:
    b64_logo_altus = f.read().strip()

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Infografía Megarreforma - Slide 2</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;700;800&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
        }}
        :root {{
            --bg-color: #0d1321;
            --card-bg: #1d2d44;
            --accent-gold: #f0ebd8;
            --accent-gold-strong: #e5b154;
            --accent-cyan: #74b3ce;
            --text-main: #ffffff;
            --text-muted: #b0c4de;
            --green-success: #2ec4b6;
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
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }}
        .header {{
            padding: 50px 80px 10px 80px;
            text-align: center;
        }}
        .tag {{
            background: var(--accent-gold-strong);
            color: #000;
            padding: 6px 14px;
            border-radius: 20px;
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 2px;
            display: inline-block;
            margin-bottom: 15px;
        }}
        h1 {{
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 52px;
            margin: 0 0 15px 0;
            line-height: 1.1;
            background: -webkit-linear-gradient(45deg, #ffffff, var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{
            font-size: 22px;
            color: var(--text-muted);
            margin: 0;
            font-weight: 300;
            line-height: 1.4;
            padding: 0 20px;
        }}
        
        .content-area {{
            padding: 20px 80px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .profile-card {{
            background: linear-gradient(90deg, rgba(29, 45, 68, 0.9), rgba(29, 45, 68, 0.4));
            border-left: 6px solid var(--accent-gold-strong);
            border-radius: 16px;
            padding: 25px 40px;
            display: flex;
            align-items: center;
            gap: 30px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        .profile-icon {{
            font-size: 70px;
        }}
        .profile-info h2 {{
            font-family: 'Outfit', sans-serif;
            font-size: 32px;
            color: var(--accent-gold);
            margin: 0 0 5px 0;
        }}
        .profile-info p {{
            font-size: 20px;
            margin: 5px 0;
            color: #d8e2ea;
        }}
        .profile-info strong {{
            color: #fff;
        }}

        .steps-container {{
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 10px;
        }}

        .step-row {{
            display: flex;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(116, 179, 206, 0.15);
            border-radius: 16px;
            padding: 25px 30px;
            align-items: flex-start;
            gap: 25px;
            backdrop-filter: blur(5px);
        }}
        .step-number {{
            background: rgba(116, 179, 206, 0.15);
            color: var(--accent-cyan);
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 28px;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        .step-content {{
            flex-grow: 1;
        }}
        .step-content h3 {{
            font-family: 'Outfit', sans-serif;
            font-size: 24px;
            margin: 0 0 10px 0;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .step-content p {{
            margin: 0 0 8px 0;
            font-size: 18px;
            color: var(--text-muted);
            line-height: 1.4;
        }}
        .highlight-text {{
            color: var(--accent-gold-strong);
            font-weight: 700;
        }}

        .results {{
            margin-top: auto;
            background: rgba(46, 196, 182, 0.1);
            border: 1px solid rgba(46, 196, 182, 0.3);
            border-radius: 16px;
            padding: 25px;
            display: flex;
            justify-content: space-around;
            align-items: center;
        }}
        .result-item {{
            text-align: center;
        }}
        .result-item .icon {{
            font-size: 32px;
            margin-bottom: 5px;
            display: block;
        }}
        .result-item .text {{
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 18px;
            color: var(--green-success);
        }}
        
        .footer {{
            padding: 30px 60px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(13, 19, 33, 0.95);
            border-top: 1px solid rgba(255,255,255,0.05);
        }}
        .contact-info {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .contact-name {{
            font-family: 'Outfit', sans-serif;
            font-size: 22px;
            font-weight: 700;
            color: var(--accent-cyan);
            margin: 0;
        }}
        .contact-role {{
            font-size: 16px;
            color: var(--text-muted);
            font-weight: 400;
            margin: 0;
        }}
        .contact-details {{
            font-size: 14px;
            color: #fff;
            font-weight: 300;
            margin-top: 5px;
        }}
        .logos-container {{
            display: flex;
            align-items: center;
            gap: 30px;
        }}
        .logo-fv {{
            height: 90px;
            object-fit: contain;
        }}
        .logo-altus {{
            height: 85px;
            object-fit: contain;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="tag">CASO DE ESTUDIO</div>
        <h1>Maximizando el Beneficio</h1>
        <p class="subtitle">¿Cómo se ven las <b>ventanas temporales</b> en la práctica para un inversionista chileno?</p>
    </div>

    <div class="content-area">
        <div class="profile-card">
            <div class="profile-icon">👤</div>
            <div class="profile-info">
                <h2>Roberto (60 años)</h2>
                <p>Posee <strong>USD 2.000.000</strong> en cuentas en el extranjero sin regularizar.</p>
                <p><strong>Objetivo:</strong> Regularizar fondos, invertirlos eficientemente para renta y estructurar la herencia a sus 2 hijos.</p>
            </div>
        </div>

        <div class="steps-container">
            <div class="step-row">
                <div class="step-number">1</div>
                <div class="step-content">
                    <h3>🌍 Repatriación Estratégica</h3>
                    <p>Roberto declara sus USD 2M acogiéndose a la Megarreforma. Decide inyectar el capital a Chile con compromiso de mantenerlo por 8 años.</p>
                    <p>👉 Su impuesto de regularización <strong>baja del 10% al <span class="highlight-text">7%</span></strong>.</p>
                </div>
            </div>

            <div class="step-row">
                <div class="step-number">2</div>
                <div class="step-content">
                    <h3>📈 Inversión Exenta (Art. 107 y DFL2)</h3>
                    <p>Los USD 2M ya repatriados los divide: Compra propiedades DFL2 para renta pagando un <span class="highlight-text">impuesto único de solo el 5%</span>, e invierte el resto en un Fondo Mutuo local bajo el <strong>Art. 107 LIR</strong>.</p>
                    <p>👉 Todo su crecimiento y ganancias de capital quedan <strong>exentas de tributación</strong>.</p>
                </div>
            </div>

            <div class="step-row">
                <div class="step-number">3</div>
                <div class="step-content">
                    <h3>👨‍👩‍👧‍👦 Herencia en Vida (Donaciones)</h3>
                    <p>Roberto aprovecha la ventana de 1 año y decide donar en vida USD 1M de este portafolio a sus 2 hijos (aprovechando que ya están estructurados en Chile).</p>
                    <p>👉 Evita el trámite de insinuación judicial y accede a una <span class="highlight-text">rebaja transitoria del 50%</span> en el Impuesto a las Donaciones.</p>
                </div>
            </div>
        </div>

        <div class="results">
            <div class="result-item">
                <span class="icon">✅</span>
                <span class="text">Ahorro Fiscal Masivo</span>
            </div>
            <div class="result-item">
                <span class="icon">💼</span>
                <span class="text">Renta Estructurada Limpia</span>
            </div>
            <div class="result-item">
                <span class="icon">🛡️</span>
                <span class="text">Sucesión Asegurada</span>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="contact-info">
            <h3 class="contact-name">Francisco Valencia</h3>
            <p class="contact-role">Managing Partner | Asesor Financiero Senior</p>
            <p class="contact-details">📩 contacto@fv-inversiones.com • 📱 +56 9 6677 9662</p>
        </div>
        <div class="logos-container">
            <img class="logo-fv" src="data:image/svg+xml;base64,{b64_logo_fv}" alt="Logo FV">
            <img class="logo-altus" src="data:image/svg+xml;base64,{b64_logo_altus}" alt="Logo Altus">
        </div>
    </div>
</body>
</html>
"""

with open('infografia_slide2.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

hti = Html2Image(size=(2160, 2700))
source_path = 'infografia_slide2.png'
hti.screenshot(html_file='infografia_slide2.html', save_as=source_path)

# Copy to artifacts so the user can easily see it
artifact_dir = r"C:\Users\franc\.gemini\antigravity-ide\brain\e0a740f0-6d0f-448b-98b0-162b61f9b6b0"
dest_path = os.path.join(artifact_dir, source_path)
shutil.copy2(source_path, dest_path)

print(f"Infografía Slide 2 generada y copiada a: {{dest_path}}")
