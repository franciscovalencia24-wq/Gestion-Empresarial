import os
import base64
import re

ROOT = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR"
ASSETS = os.path.join(ROOT, "assets")

logo_fv_path = os.path.join(ASSETS, "Logo_FV_Principal.png")
logo_altus_path = os.path.join(ASSETS, "altus_logo_minimalist_1780936005587.png")
html_path = os.path.join(ASSETS, "firma_correo_altus.html")
out_path = os.path.join(ASSETS, "firma_correo_actualizada.html")

# Read FV logo and encode to base64
with open(logo_fv_path, "rb") as image_file:
    fv_encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# Read Altus logo and encode to base64
with open(logo_altus_path, "rb") as image_file:
    altus_encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# Read original HTML
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace the FV logo source
new_fv_src = f"data:image/png;base64,{fv_encoded_string}"
html_content = re.sub(r'src="[^"]*NUEVO LOGO FV\.png"', f'src="{new_fv_src}"', html_content)

# Replace the Altus logo source
new_altus_src = f"data:image/png;base64,{altus_encoded_string}"
html_content = re.sub(r'src="altus_logo_minimalist_1780936005587\.png"', f'src="{new_altus_src}"', html_content)

# Save new HTML
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Firma actualizada guardada en: {out_path}")
