import base64
import os
from bs4 import BeautifulSoup

def update_signature():
    assets_dir = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\assets"
    html_path = os.path.join(assets_dir, "firma_correo_altus_embedded.html")
    fv_logo_path = os.path.join(assets_dir, "Logo_FV_Principal.png")
    altus_logo_path = os.path.join(assets_dir, "Logo_ALTUS AI_Principal_Fondo oscuro.png")
    output_path = os.path.join(assets_dir, "firma_correo_final.html")

    # Read the images and encode to base64
    with open(fv_logo_path, "rb") as f:
        fv_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    with open(altus_logo_path, "rb") as f:
        altus_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Parse HTML
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    for img in soup.find_all("img"):
        alt_text = img.get('alt', '')
        if alt_text == 'FV Asesorías e Inversiones':
            img['src'] = f"data:image/png;base64,{fv_b64}"
            img['width'] = "180"
        elif alt_text == 'Altus AI':
            img['src'] = f"data:image/png;base64,{altus_b64}"
            img['width'] = "120"

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
        
    print(f"Signature successfully generated at {output_path}")

if __name__ == '__main__':
    update_signature()
