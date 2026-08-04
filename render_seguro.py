import os
from html2image import Html2Image
from PIL import Image

def render_seguro():
    out_dir = "PRINCIPAL/PRODUCTOS/SEGURO DE VIDA CON AHORRO PREFERENTE"
    html_path = f"{out_dir}/infografia_seguro.html"
    
    abs_html_path = os.path.abspath(html_path)
    
    hti = Html2Image(output_path=out_dir, custom_flags=['--virtual-time-budget=4000', '--allow-file-access-from-files'])
    temp_png = "temp_seguro.png"
    
    print("Capturando HTML...")
    hti.screenshot(html_file=abs_html_path, save_as=temp_png, size=(2160, 8640))
    
    img_path = f"{out_dir}/{temp_png}"
    
    if os.path.exists(img_path):
        print("Procesando imagen...")
        Image.init()
        img = Image.open(img_path).convert('RGB')
        
        # Generar PDF en alta resolución (páginas separadas)
        pages = []
        for i in range(4):
            box = (0, i*2160, 2160, (i+1)*2160)
            page = img.crop(box)
            pages.append(page)
            
        pdf_path = f"{out_dir}/infografia_seguro_whatsapp.pdf"
        pages[0].save(pdf_path, save_all=True, append_images=pages[1:])
        print(f"PDF generado: {pdf_path}")
        
        # Generar JPG largo optimizado para WhatsApp (ancho 1080px)
        ratio = 1080 / 2160
        new_height = int(8640 * ratio)
        img_resized = img.resize((1080, new_height), Image.Resampling.LANCZOS)
        
        jpg_path = f"{out_dir}/infografia_seguro_whatsapp.jpg"
        img_resized.save(jpg_path, 'JPEG', quality=85)
        print(f"JPG generado: {jpg_path}")
        
        img.close()
        os.remove(img_path)
        print("Renderizado exitoso!")

if __name__ == "__main__":
    render_seguro()
