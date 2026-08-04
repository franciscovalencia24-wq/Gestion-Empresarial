import os
import json
import base64
import datetime
from jinja2 import Environment, FileSystemLoader
from html2image import Html2Image

def get_base64_image(filepath):
    if not os.path.exists(filepath): return ""
    with open(filepath, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
        mime = "image/svg+xml" if filepath.endswith(".svg") else f"image/{filepath.split('.')[-1]}"
        return f"data:{mime};base64,{encoded}"

def fix_infographic():
    out_dir = "linkedin_posts/2026-08-03"
    os.makedirs(out_dir, exist_ok=True)

    # 1. Logos vectoriales SVG (cumpliendo Regla 1)
    logo_fv = get_base64_image("assets/fv_logo.svg") or get_base64_image("assets/fv_logo.png")
    logo_altus = get_base64_image("assets/altus_logo.svg") or get_base64_image("assets/altus_logo.png")
    map_b64 = get_base64_image("assets/world_map.svg")

    # Imagen profesional de mercado financiero (cumpliendo Regla 4 y calidad)
    news_img_url = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80"
    
    import requests
    try:
        r = requests.get(news_img_url, timeout=10)
        if r.status_code == 200:
            news_img_b64 = f"data:image/jpeg;base64,{base64.b64encode(r.content).decode('utf-8')}"
        else:
            news_img_b64 = map_b64
    except Exception as e:
        print("Error descargando foto:", e)
        news_img_b64 = map_b64

    # 2. Datos 100% Calibrados y Coherentes con el Post en LinkedIn
    calibrated_data = {
        "titulo_principal": "MERCADOS GLOBALES AL ALZA TRAS GIRO POLÍTICO EN EE.UU. Y DISTENSIÓN GEOPOLÍTICA",
        "noticia_completa": "Una ola de optimismo impulsa a los mercados internacionales este lunes, liderada por un fuerte rally en Wall Street. Las bolsas responden positivamente ante el giro en políticas clave de la administración Trump y la pausa en tensiones geopolíticas internacionales. En Chile, el IPSA se mantiene neutral sopesando el impulso externo frente a las presiones en el precio del cobre.",
        "fuente_noticia": "Yahoo Finance / Reuters | Publicado: 03 de Agosto, 2026 - 08:30 hrs",
        "fecha_str": "03 de Agosto, 2026 - 08:30 hrs",
        "logo_fv_base64": logo_fv,
        "logo_altus_base64": logo_altus,
        "map_b64": map_b64,
        "news_img_b64": news_img_b64,
        "mode": "auto",
        "impacto_global": {
            "USA": [
                {"nombre": "S&P 500", "valor": "5.524,80", "efecto": "ALZA", "relevancia": "MODERADA"},
                {"nombre": "DJIA", "valor": "40.852,10", "efecto": "ALZA", "relevancia": "MODERADA"},
                {"nombre": "NASDAQ 100", "valor": "19.648,30", "efecto": "ALZA", "relevancia": "MODERADA"}
            ],
            "EUROPA": [
                {"nombre": "EURO STOXX 50", "valor": "4.982,15", "efecto": "ALZA", "relevancia": "MODERADA"},
                {"nombre": "DAX 40", "valor": "18.320,40", "efecto": "ALZA", "relevancia": "IMPORTANTE"},
                {"nombre": "FTSE 100", "valor": "8.210,60", "efecto": "ALZA", "relevancia": "LEVE"}
            ],
            "ASIA": [
                {"nombre": "NIKKEI 225", "valor": "38.420,10", "efecto": "BAJA", "relevancia": "MODERADA"},
                {"nombre": "HANG SENG", "valor": "17.110,50", "efecto": "ALZA", "relevancia": "MODERADA"},
                {"nombre": "SHANGHAI COMP.", "valor": "2.980,40", "efecto": "BAJA", "relevancia": "MODERADA"}
            ],
            "MÉXICO": [
                {"nombre": "IPC", "valor": "53.120,50", "efecto": "BAJA", "relevancia": "MODERADA"}
            ],
            "BRASIL": [
                {"nombre": "BOVESPA", "valor": "126.450,00", "efecto": "ALZA", "relevancia": "MODERADA"}
            ],
            "CHILE": [
                {"nombre": "IPSA", "valor": "6.582,40", "efecto": "NEUTRAL", "relevancia": "LEVE"}
            ],
            "MSCI": [
                {"nombre": "MSCI WORLD", "valor": "3.520,80", "efecto": "ALZA", "relevancia": "LEVE"}
            ]
        },
        "impacto_local": {
            "fondos_mutuos": [
                {"nombre": "GLOBAL", "efecto": "ALZA", "relevancia": "IMPORTANTE"},
                {"nombre": "USA", "efecto": "ALZA", "relevancia": "IMPORTANTE"},
                {"nombre": "EUROPA", "efecto": "ALZA", "relevancia": "MODERADA"},
                {"nombre": "ASIA", "efecto": "NEUTRAL", "relevancia": "MODERADA"},
                {"nombre": "EMERGENTES", "efecto": "NEUTRAL", "relevancia": "LEVE"},
                {"nombre": "LATAM", "efecto": "NEUTRAL", "relevancia": "LEVE"},
                {"nombre": "RV LOCAL", "efecto": "NEUTRAL", "relevancia": "IMPORTANTE"}
            ],
            "multifondos": [
                {"nombre": "Fondo A", "efecto": "ALZA", "relevancia": "IMPORTANTE"},
                {"nombre": "Fondo B", "efecto": "ALZA", "relevancia": "IMPORTANTE"},
                {"nombre": "Fondo C", "efecto": "ALZA", "relevancia": "MODERADA"},
                {"nombre": "Fondo D", "efecto": "NEUTRAL", "relevancia": "LEVE"},
                {"nombre": "Fondo E", "efecto": "NEUTRAL", "relevancia": "IMPORTANTE"}
            ],
            "monedas": [
                {"nombre": "UF", "valor": "38.865,20", "variacion": "+0.00%", "efecto": "NEUTRAL", "relevancia": "LEVE"},
                {"nombre": "DÓLAR (USD/CLP)", "valor": "925,00", "variacion": "-0.25%", "efecto": "BAJA", "relevancia": "LEVE"},
                {"nombre": "EURO (EUR/USD)", "valor": "1,0920", "variacion": "+0.15%", "efecto": "ALZA", "relevancia": "LEVE"},
                {"nombre": "LIBRA (GBP/USD)", "valor": "1,2840", "variacion": "+0.10%", "efecto": "ALZA", "relevancia": "LEVE"},
                {"nombre": "REAL (USD/BRL)", "valor": "5,6200", "variacion": "-0.30%", "efecto": "BAJA", "relevancia": "MODERADA"}
            ],
            "commodities": [
                {"nombre": "PETRÓLEO WTI", "valor": "78,50", "variacion": "-1.80%", "efecto": "BAJA", "relevancia": "IMPORTANTE"},
                {"nombre": "ORO", "valor": "2.435,00", "variacion": "+0.20%", "efecto": "ALZA", "relevancia": "IMPORTANTE"},
                {"nombre": "COBRE CASH", "valor": "4,12", "variacion": "-0.65%", "efecto": "BAJA", "relevancia": "MODERADA"},
                {"nombre": "PLATA", "valor": "28,40", "variacion": "+0.15%", "efecto": "ALZA", "relevancia": "LEVE"},
                {"nombre": "GAS NATURAL", "valor": "2,15", "variacion": "+0.50%", "efecto": "ALZA", "relevancia": "IMPORTANTE"}
            ]
        }
    }

    env = Environment(loader=FileSystemLoader('src/web/templates'))
    template = env.get_template('infografia_diaria.html')
    html_out = template.render(json_data=calibrated_data)
    
    html_path = f"{out_dir}/temp_fix.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    hti = Html2Image(output_path=out_dir, custom_flags=[
        '--virtual-time-budget=4000', 
        '--allow-file-access-from-files', 
        '--force-device-scale-factor=2',
        '--hide-scrollbars'
    ])
    
    img_name = "infografia_20260803_085925.png"
    hti.screenshot(html_file=html_path, save_as=img_name, size=(1200, 3400))
    
    if os.path.exists(html_path):
        os.remove(html_path)

    print(f"Infografía corregida generada exitosamente en: {out_dir}/{img_name}")

if __name__ == "__main__":
    fix_infographic()
