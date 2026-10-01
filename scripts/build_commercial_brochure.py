import os
import base64

def get_base64_of_file(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(file_path)[1].lower().strip('.')
    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
    b64_data = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64_data}"

def build_brochure():
    altus_logo_b64 = get_base64_of_file("assets/brand/altus_ai_logo_dark.svg")
    fv_logo_b64 = get_base64_of_file("assets/brand/fv_logo_principal.svg")
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brochure Comercial ALTUS CORE</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0A2342;
            --primary: #0A2342;
            --primary-light: #17375e;
            --accent: #D4AF37;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --card-bg: rgba(255, 255, 255, 0.05);
            --border-glow: rgba(212, 175, 55, 0.3);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Montserrat', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            background-image: radial-gradient(circle at 15% 50%, rgba(212, 175, 55, 0.05), transparent 50%),
                              radial-gradient(circle at 85% 30%, rgba(212, 175, 55, 0.1), transparent 50%);
            background-attachment: fixed;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 0 40px;
        }}

        /* Hero Section */
        .hero {{
            text-align: center;
            padding: 100px 0 80px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            position: relative;
        }}
        
        .hero::after {{
            content: '';
            position: absolute;
            bottom: -1px;
            left: 20%;
            right: 20%;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
        }}

        .logos-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 50px;
            margin-bottom: 40px;
        }}

        .logos-container img {{
            height: 70px;
            object-fit: contain;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5));
        }}
        
        .divider-vertical {{
            width: 1px;
            height: 50px;
            background: var(--accent);
            opacity: 0.5;
        }}

        .hero h1 {{
            font-family: 'Playfair Display', serif;
            font-size: 3.5rem;
            line-height: 1.1;
            margin-bottom: 20px;
            font-weight: 800;
            background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero p {{
            font-size: 1.25rem;
            color: var(--text-muted);
            max-width: 700px;
            margin: 0 auto;
            font-weight: 300;
        }}
        
        .highlight-gold {{
            color: var(--accent);
            font-weight: 600;
        }}

        /* Cost of Inaction / Dolor */
        .urgency-section {{
            padding: 60px 0;
            text-align: center;
        }}
        
        .urgency-box {{
            background: linear-gradient(145deg, rgba(23, 55, 94, 0.4) 0%, rgba(10, 35, 66, 0.8) 100%);
            border: 1px solid rgba(255, 99, 71, 0.2);
            border-radius: 12px;
            padding: 40px;
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .urgency-box::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ff4d4d, #ff8c00);
        }}

        .urgency-box h2 {{
            font-family: 'Playfair Display', serif;
            font-size: 1.8rem;
            margin-bottom: 20px;
            color: #fff;
        }}

        .urgency-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 30px;
        }}

        .urgency-item {{
            text-align: left;
            padding: 25px;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            border-left: 3px solid #ff4d4d;
        }}
        
        .urgency-item h4 {{
            color: #ffb3b3;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }}
        
        .urgency-item p {{
            font-size: 0.9rem;
            color: #cbd5e1;
            font-weight: 300;
        }}

        /* Pilares Tecnológicos */
        .features-section {{
            padding: 80px 0;
        }}

        .section-title {{
            text-align: center;
            font-size: 2.2rem;
            margin-bottom: 50px;
            font-family: 'Playfair Display', serif;
            color: #fff;
        }}

        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
        }}

        .feature-card {{
            background: var(--card-bg);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 35px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
        }}
        
        .feature-card::after {{
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 16px;
            padding: 1px;
            background: linear-gradient(135deg, var(--border-glow) 0%, transparent 50%, rgba(255,255,255,0.05) 100%);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            pointer-events: none;
        }}

        .feature-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
            border-color: rgba(212, 175, 55, 0.4);
        }}

        .icon-wrapper {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.2) 0%, rgba(212, 175, 55, 0.05) 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            border: 1px solid rgba(212, 175, 55, 0.4);
            font-size: 28px;
        }}

        .feature-card h3 {{
            font-size: 1.25rem;
            margin-bottom: 15px;
            color: #fff;
            line-height: 1.3;
        }}

        .feature-card p {{
            font-size: 0.95rem;
            color: var(--text-muted);
            margin-bottom: 25px;
            flex-grow: 1;
        }}
        
        .feature-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: auto;
        }}
        
        .tag {{
            font-size: 0.75rem;
            padding: 5px 12px;
            background: rgba(212, 175, 55, 0.15);
            color: var(--accent);
            border-radius: 20px;
            border: 1px solid rgba(212, 175, 55, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}

        /* CTA Exclusivo */
        .cta-section {{
            padding: 40px 0 100px 0;
        }}

        .cta-box {{
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(10, 35, 66, 0.9) 100%);
            border-radius: 16px;
            padding: 50px;
            text-align: center;
            border: 1px solid var(--accent);
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5), inset 0 0 60px rgba(212, 175, 55, 0.05);
        }}

        .cta-box h2 {{
            font-family: 'Playfair Display', serif;
            font-size: 2.2rem;
            margin-bottom: 20px;
            color: var(--accent);
        }}

        .cta-box p {{
            font-size: 1.1rem;
            color: #e2e8f0;
            max-width: 800px;
            margin: 0 auto 30px auto;
            line-height: 1.8;
        }}

        .badge-exclusive {{
            display: inline-block;
            background: #fff;
            color: var(--primary);
            padding: 12px 30px;
            border-radius: 30px;
            font-weight: 800;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            box-shadow: 0 4px 15px rgba(255,255,255,0.2);
        }}
        
        .footer {{
            text-align: center;
            padding: 30px 0;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 50px;
        }}

        /* Print Optimizations & xhtml2pdf */
        @page {{
            size: a4 portrait;
            background-color: #0A2342;
            margin: 1.5cm;
        }}

        @media print {{
            body {{
                background-color: #0A2342 !important;
                background-image: none !important;
                color: #f8fafc !important;
            }}
            .feature-card, .urgency-box, .cta-box {{
                page-break-inside: avoid;
                break-inside: avoid;
            }}
            .container {{
                padding: 0;
            }}
            .hero {{
                padding: 40px 0;
            }}
        }}
    </style>
</head>
<body>

    <div class="container">
        <!-- HERO -->
        <div class="hero">
            <div class="logos-container">
                <img src="{altus_logo_b64}" alt="Altus Core">
                <div class="divider-vertical"></div>
                <img src="{fv_logo_b64}" alt="FV Asesorías e Inversiones">
            </div>
            <h1>Inteligencia Patrimonial 360°<br>al Nivel de un <span class="highlight-gold">Family Office</span> Digital</h1>
            <p>Conoce <b>ALTUS CORE</b>: La suite tecnológica exclusiva para clientes de FV Asesorías e Inversiones a través de PRINCIPAL.</p>
        </div>

        <!-- URGENCIA / DOLOR -->
        <div class="urgency-section">
            <div class="urgency-box">
                <h2>El Alto Costo de No Planificar</h2>
                <p style="color: #cbd5e1; max-width: 800px; margin: 0 auto; font-size: 1.05rem;">
                    Sin una estrategia cuantitativa, el patrimonio acumulado queda expuesto a fricciones normativas y fiscales. Nuestro diagnóstico integral detecta y mitiga estos riesgos.
                </p>
                
                <div class="urgency-grid">
                    <div class="urgency-item">
                        <h4>Fuga Tributaria</h4>
                        <p>Sobrepago de impuestos por falta de reliquidaciones y desaprovechamiento de excesos de cotización.</p>
                    </div>
                    <div class="urgency-item">
                        <h4>Impuesto a la Herencia</h4>
                        <p>Desconocimiento de la masa hereditaria y exposición a la Ley 16.271 sin planificación de liquidez post-mortem.</p>
                    </div>
                    <div class="urgency-item">
                        <h4>Desorden en Flujo de Caja</h4>
                        <p>Descoordinación entre activos inmobiliarios, carga financiera y rentabilidad, mermando el estándar de vida.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- PILARES TECNOLÓGICOS -->
        <div class="features-section">
            <h2 class="section-title">Soluciones Integradas en ALTUS CORE</h2>
            <div class="cards-grid">
                
                <!-- Tarjeta 1 -->
                <div class="feature-card">
                    <div class="icon-wrapper">🏛️</div>
                    <h3>Auditoría Patrimonial 360° & Sucesoria</h3>
                    <p>Diagnóstico de bienes raíces, Cap Rate, masa hereditaria y cálculo avanzado del flujo de supervivencia post-mortem para tu familia.</p>
                    <div class="feature-tags">
                        <span class="tag">Bienes Raíces</span>
                        <span class="tag">Cap Rate</span>
                        <span class="tag">Herencia</span>
                    </div>
                </div>

                <!-- Tarjeta 2 -->
                <div class="feature-card">
                    <div class="icon-wrapper">⚖️</div>
                    <h3>Optimización Tributaria & Rescate</h3>
                    <p>Recuperación de liquidez inmediata mediante la detección de Devolución de Pagos en Exceso (DPE) y estrategias de Reliquidación de Impuestos.</p>
                    <div class="feature-tags">
                        <span class="tag">DPE</span>
                        <span class="tag">Reliquidación</span>
                        <span class="tag">Eficiencia</span>
                    </div>
                </div>

                <!-- Tarjeta 3 -->
                <div class="feature-card">
                    <div class="icon-wrapper">📈</div>
                    <h3>Inteligencia de Inversiones</h3>
                    <p>Análisis algorítmico de riesgo/retorno, simulación de regímenes tributarios (APV Inteligente Régimen A/B) y optimización de portafolios a la medida.</p>
                    <div class="feature-tags">
                        <span class="tag">APV Inteligente</span>
                        <span class="tag">Riesgo/Retorno</span>
                        <span class="tag">Portafolios</span>
                    </div>
                </div>

            </div>
        </div>

        <!-- CTA EXCLUSIVO -->
        <div class="cta-section">
            <div class="cta-box">
                <h2>Exclusividad Institucional</h2>
                <p>El acceso integral a la suite algorítmica <b>ALTUS CORE</b> y a nuestra ingeniería de planificación 360° no se comercializa en el mercado abierto ni se vende por separado.</p>
                <p>Es un beneficio exclusivo e ilimitado, reservado estrictamente para los clientes que confían su gestión patrimonial a <b>FV Asesorías e Inversiones</b> a través de la arquitectura de <b>PRINCIPAL</b>.</p>
                
                <div style="margin-top: 40px;">
                    <div class="badge-exclusive">Uso Exclusivo Clientes FV / PRINCIPAL</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><b>ALTUS CORE</b> es propiedad intelectual de ALTUS AI SpA.</p>
            <p>Documento Generado Automáticamente — Confidencialidad y Uso Restringido</p>
        </div>

    </div>
</body>
</html>"""

    os.makedirs("dist", exist_ok=True)
    out_path = "dist/brochure_comercial_altus.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Brochure generado exitosamente en {out_path}")

if __name__ == "__main__":
    build_brochure()
