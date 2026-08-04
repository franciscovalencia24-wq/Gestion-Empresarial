from PIL import Image
import os

input_path = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\NUEVO_LOGO_FV_BLANCO.png"
output_path = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\LOGO_FINAL_GAMMA.png"

try:
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        r, g, b = item[:3]
        
        # Detectar la flecha verde: El canal Verde (g) es notablemente mayor que Rojo (r) y Azul (b)
        if g > r + 15 and g > b + 15:
            # Mantener la flecha verde intacta
            newData.append(item)
        else:
            # Todo lo demás (el fondo blanco y las letras grises/negras)
            # Lo convertimos a color BLANCO, pero ajustamos su transparencia.
            # Si el pixel original era blanco (fondo), será 100% transparente.
            # Si el pixel original era oscuro (texto), será 100% sólido (texto blanco puro).
            # Esto mantiene los bordes suaves perfectos.
            brightness = (r + g + b) / 3.0
            alpha = int(255 - brightness)
            
            # Para evitar que el fondo casi blanco deje una mancha blanca:
            if alpha < 20: 
                alpha = 0
                
            newData.append((255, 255, 255, alpha))

    img.putdata(newData)
    img.save(output_path, "PNG")
    print("ÉXITO PERFECTO")
except Exception as e:
    print("Error:", str(e))
