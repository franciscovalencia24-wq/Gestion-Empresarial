import os
import base64
from html2image import Html2Image
from PIL import Image, ImageChops

def get_b64(path):
    mime = "image/svg+xml" if path.lower().endswith(".svg") else "image/png"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("utf-8")

def build():
    out_dir = "PRINCIPAL/PRODUCTOS/SEGURO DE VIDA CON AHORRO PREFERENTE"
    
    logo_fv = get_b64("assets/brand/fv_logo_vector_negativo.svg")
    logo_altus = get_b64("assets/Logo_ALTUS AI_Negativo.svg")
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --navy: #002E5D; --accent-gold: #B89650; }}
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0f172a; margin: 0; padding: 0; }}
        .export-container {{ width: 1080px; background: #0f172a; overflow: hidden; position: relative; }}
        .content-box {{ padding: 60px; background-color: #0f172a; }}
        .card {{ background: #1e293b; border-radius: 20px; padding: 40px; border-top: 6px solid #B89650; position: relative; height: 100%; }}
        .card h3 {{ color: #f8fafc; font-size: 28px; font-weight: 800; margin-bottom: 20px; text-transform: uppercase; display: flex; align-items: center; gap: 15px; }}
        .card ul {{ list-style: none; padding: 0; margin: 0; }}
        .card li {{ color: #cbd5e1; font-size: 22px; line-height: 1.5; margin-bottom: 15px; position: relative; padding-left: 25px; }}
        .card li::before {{ content: "•"; color: #B89650; position: absolute; left: 0; top: 0; font-size: 28px; }}
        .premium-badge {{ display: flex; justify-content: center; align-items: center; gap: 15px; background: linear-gradient(90deg, #000000 0%, #1a1a1a 100%); color: #B89650; padding: 15px; font-size: 18px; font-weight: 800; letter-spacing: 0.2em; text-transform: uppercase; border-bottom: 2px solid #334155; }}
        .fa-solid {{ color: #B89650; font-size: 32px; }}
    </style>
</head>
<body style="zoom: 2;">
    <div class="export-container" id="capture-area">
        <div class="premium-badge">
            <i class="fa-solid fa-shield"></i> Producto Estratégico <i class="fa-solid fa-shield"></i>
        </div>
        <div class="bg-[var(--navy)] px-12 py-16 relative overflow-hidden border-b border-slate-700">
            <div class="relative z-10 text-white flex justify-between items-start">
                <div style="max-width: 65%;">
                    <div class="inline-flex items-center gap-3 text-lg font-black uppercase tracking-wider mb-6 text-[#B89650]">
                        <i class="fa-solid fa-star"></i>
                        <span>Soluciones Patrimoniales</span>
                    </div>
                    <h1 class="text-6xl font-extrabold tracking-tight mb-6 uppercase leading-tight">
                        ¿Por qué tener un <br><span class="text-[#B89650]">Seguro de Vida con Ahorro?</span>
                    </h1>
                    <p class="text-blue-100/80 text-2xl font-medium">Conoce las 8 ventajas estratégicas del Seguro de Vida Patrimonial Preferente</p>
                </div>
                <div class="flex flex-col items-center justify-center gap-4 -mt-4">
                    <img src="{logo_fv}" alt="FV" style="height: 175px; width: auto;">
                    <span class="text-white font-light opacity-60 leading-none -mt-4" style="font-size: 65px;">+</span>
                    <img src="{logo_altus}" alt="Altus AI" style="height: 160px; width: auto;">
                </div>
            </div>
        </div>

        <div class="content-box">
            <div class="grid grid-cols-2 gap-8">
                <div class="card">
                    <h3><i class="fa-solid fa-users"></i> 1. Sucesión</h3>
                    <ul>
                        <li>Rápida liquidez a los Herederos o Terceros ante fin de la vida del Contratante/Asegurado.</li>
                        <li>Sin trámite de posesión efectiva, siendo único en la industria financiera.</li>
                        <li>Complementario a un testamento.</li>
                    </ul>
                </div>
                <div class="card">
                    <h3><i class="fa-solid fa-wallet"></i> 2. Desacumulación</h3>
                    <ul>
                        <li>Permite retirar "inversión en UF" antes que la utilidad o ganancia (cuenta caja).</li>
                        <li>Ideal para complementar un programa de desacumulación eficiente.</li>
                    </ul>
                </div>
                <div class="card">
                    <h3><i class="fa-solid fa-file-invoice-dollar"></i> 3. Tributación</h3>
                    <ul>
                        <li>No se debe presentar DDJJ N°1929 (Junio), por inversiones en el exterior.</li>
                        <li>Retiros de la inversión no se registran en la declaración de renta.</li>
                    </ul>
                </div>
                <div class="card">
                    <h3><i class="fa-solid fa-scale-balanced"></i> 4. Pérdidas Tributarias</h3>
                    <ul>
                        <li>Permite compensar con ganancias tributarias otros instrumentos financieros.</li>
                    </ul>
                </div>
                <div class="card">
                    <h3><i class="fa-solid fa-shield-halved"></i> 5. Protección</h3>
                    <ul>
                        <li>Tiene componente de Protección y Ahorro.</li>
                        <li>Permite libre designación de beneficiarios.</li>
                        <li>Inembargable según código de procedimiento civil.</li>
                        <li>Bajos costos de administración.</li>
                    </ul>
                </div>
                <div class="card">
                    <h3><i class="fa-solid fa-earth-americas"></i> 6. Inversión</h3>
                    <ul>
                        <li>Inversión en activos Chilenos o Extranjeros.</li>
                        <li>Permite gran diversificación en una cartera de inversión y mitigar riesgos del mercado.</li>
                    </ul>
                </div>
                <div class="card">
                    <h3><i class="fa-solid fa-arrow-trend-up"></i> 7. Acumulación</h3>
                    <ul>
                        <li>Reinversiones de activos financieros dentro del seguro de vida no generan hecho gravado de tributación.</li>
                        <li>Otorga una administración activa del portafolio.</li>
                    </ul>
                </div>
                <div class="card">
                    <h3><i class="fa-solid fa-coins"></i> 8. Ingreso No Renta</h3>
                    <ul>
                        <li>17 UTM sobre la ganancia de capital, para pólizas desde 5 años y retiros totales.</li>
                        <li>Opción de dejar utilidad para herencia.</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="bg-[#0f172a] px-12 pb-12">
            <div class="bg-[#1e293b] border-2 border-[#334155] rounded-2xl p-6 flex gap-10 text-sm text-slate-400 leading-relaxed justify-between">
                <div class="flex-1 text-justify">
                    <div class="text-white font-extrabold uppercase mb-2 text-base">Sobre FV Asesorías e Inversiones</div>
                    FV Asesorías e Inversiones somos un Multi-Family Office Digital impulsado por nuestro software cuantitativo privado de Inteligencia Artificial (ALTUS AI). Combinamos la agilidad tecnológica de una WealthTech con la exclusividad de una oficina patrimonial privada, auditando en 360° la situación tributaria, inmobiliaria, composición familiar, seguros e inversiones para proteger su legado a través de las generaciones.
                </div>
                <div class="flex-1 text-justify">
                    <div class="text-white font-extrabold uppercase mb-2 text-base">Aviso Legal</div>
                    Este informe es generado por ALTUS AI y tiene fines exclusivamente informativos y educativos. La conveniencia de adquirir deuda o rescatar inversiones depende de la situación financiera, perfil de riesgo y objetivos de cada cliente.
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

    html_path = f"{out_dir}/infografia_seguro_mobile.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("HTML generado. Capturando imagen...")
    hti = Html2Image(output_path=out_dir, custom_flags=['--virtual-time-budget=6000', '--allow-file-access-from-files', '--hide-scrollbars'])
    temp_png = "temp_mobile.png"
    
    print("Capturando HTML...")
    hti.screenshot(html_str=html_content, save_as=temp_png, size=(2160, 8000))
    
    img_path = f"{out_dir}/{temp_png}"
    
    if os.path.exists(img_path):
        print("Recortando y guardando imagen final...")
        Image.init()
        img = Image.open(img_path).convert('RGB')
        
        bg_color = img.getpixel((0, img.height - 1))
        
        pixels = img.load()
        width, height = img.size
        bottom_y = height - 1
        found = False
        for y in range(height - 1, 0, -1):
            for x in range(width):
                if pixels[x, y] != bg_color:
                    bottom_y = y
                    found = True
                    break
            if found:
                break
                
        final_height = min(height, bottom_y + 20)
        img_cropped = img.crop((0, 0, width, final_height))
        
        # Guardar como PNG para máxima calidad sin artefactos de compresión
        png_path = f"{out_dir}/infografia_seguro_unahoja.png"
        img_cropped.save(png_path, 'PNG')
        print(f"PNG final guardado en {png_path}")
        
        pdf_path = f"{out_dir}/infografia_seguro_unahoja.pdf"
        img_cropped.save(pdf_path, 'PDF', resolution=100.0)
        print(f"PDF final guardado en {pdf_path}")
        
        img.close()
        os.remove(img_path)
        print("Proceso completo.")

if __name__ == "__main__":
    build()
