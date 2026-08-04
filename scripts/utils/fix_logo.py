from PIL import Image
import os

input_path = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\NUEVO_LOGO_FV_BLANCO.png"
output_path = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\LOGO_FINAL_GAMMA.png"

try:
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        # Si el pixel es blanco o casi blanco (fondo), hacerlo transparente
        if item[0] > 230 and item[1] > 230 and item[2] > 230:
            newData.append((255, 255, 255, 0))
        # Si el pixel es oscuro/negro (letras y forma FV), hacerlo blanco puro
        elif item[0] < 120 and item[1] < 120 and item[2] < 120:
            newData.append((255, 255, 255, 255))
        # Si es cualquier otro color (tu flecha verde), dejarlo igual
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(output_path, "PNG")
    print("ÉXITO")
except Exception as e:
    print("Error:", str(e))
