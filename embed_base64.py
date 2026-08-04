import os
import base64

html_file = 'firma_correo_altus.html'
output_file = 'firma_correo_altus_embedded.html'

img1_path = 'src/web/assets/NUEVO LOGO FV.png'
img2_path = 'altus_logo_minimalist_1780936005587.png'

# Convert images to base64
with open(img1_path, "rb") as f:
    b64_img1 = base64.b64encode(f.read()).decode('utf-8')
    
with open(img2_path, "rb") as f:
    b64_img2 = base64.b64encode(f.read()).decode('utf-8')

with open(html_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace paths with base64
content = content.replace('src="src/web/assets/NUEVO LOGO FV.png"', f'src="data:image/png;base64,{b64_img1}"')
content = content.replace('src="altus_logo_minimalist_1780936005587.png"', f'src="data:image/png;base64,{b64_img2}"')

with open(output_file, "w", encoding="utf-8") as f:
    f.write(content)

print("HTML guardado con imágenes incrustadas en Base64 en", output_file)
