from PIL import Image, ImageEnhance
import os

def desvanecer_logo_antiguo():
    try:
        # Abrir la imagen original
        img = Image.open('Transicion_Logos.png').convert('RGBA')
        width, height = img.size
        
        # Crear una imagen nueva con fondo blanco
        fondo = Image.new('RGBA', (width, height), (255, 255, 255, 255))
        
        # Cortar la imagen por la mitad
        mitad = width // 2
        logo_antiguo = img.crop((0, 0, mitad, height))
        logo_nuevo = img.crop((mitad, 0, width, height))
        
        # Aplicar transparencia (desvanecimiento) al logo antiguo
        # Extraemos el canal alfa (si no tiene, lo crea RGBA)
        r, g, b, a = logo_antiguo.split()
        
        # Reducimos la opacidad al 30% (desvanecido)
        a_desvanecido = a.point(lambda p: int(p * 0.3))
        logo_antiguo.putalpha(a_desvanecido)
        
        # Pegar el logo antiguo desvanecido en el fondo blanco
        fondo.paste(logo_antiguo, (0, 0), logo_antiguo)
        
        # Pegar el logo nuevo (100% opacidad) en la otra mitad
        fondo.paste(logo_nuevo, (mitad, 0), logo_nuevo)
        
        # Guardar la nueva imagen
        output_path = 'Transicion_Logos_Final.png'
        fondo.save(output_path, 'PNG')
        print(f"Éxito: Imagen guardada en {output_path}")
        
    except Exception as e:
        print(f"Error procesando la imagen: {e}")

if __name__ == '__main__':
    desvanecer_logo_antiguo()
