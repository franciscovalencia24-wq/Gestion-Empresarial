from PIL import Image, ImageDraw, ImageFont
import os

def create_modern_ad():
    width, height = 2480, 1748
    # Fondo minimalista gris ultra claro/plata
    img = Image.new('RGB', (width, height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)
    
    # Barra lateral de color verde oscuro para dar el toque moderno
    draw.rectangle([0, 0, 80, height], fill=(16, 75, 60))

    try:
        font_xl = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 160)
        font_medium = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 75)
        font_small = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 60)
        font_bold = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 60)
    except:
        font_xl = ImageFont.load_default()
        font_medium = font_xl
        font_small = font_xl
        font_bold = font_xl

    # Logo transparente sin recuadro (¡ahora más grande!)
    if os.path.exists('src/web/assets/NUEVO LOGO FV.png'):
        logo = Image.open('src/web/assets/NUEVO LOGO FV.png').convert('RGBA')
        basewidth = 1000  # Logo más grande
        wpercent = (basewidth / float(logo.size[0]))
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.LANCZOS)
        img.paste(logo, (200, 150), logo)

    # Textos con verde corporativo y gris oscuro
    draw.text((200, 750), "DIGITAL FAMILY OFFICE", font=font_xl, fill=(16, 75, 60))
    # Tilde agregada a Tecnológica
    draw.text((200, 950), "Arquitectura Tecnológica Aplicada a su Patrimonio.", font=font_medium, fill=(50, 50, 50))
    draw.text((200, 1050), "Protegiendo su legado con claridad, tiempo y tranquilidad.", font=font_medium, fill=(50, 50, 50))
    
    # Texto clave dividido en dos líneas para evitar que salga cortado
    draw.text((200, 1220), "• Inversiones en Instrumentos Financieros •", font=font_bold, fill=(16, 75, 60))
    draw.text((200, 1300), "• Seguros con Ahorro • Planificación Sucesoria •", font=font_bold, fill=(16, 75, 60))
    
    # Linea separadora elegante
    draw.line((200, 1450, width - 200, 1450), fill=(200, 200, 200), width=4)
    
    # Contacto separado correctamente
    draw.text((200, 1520), "contacto@fv-inversiones.com", font=font_bold, fill=(16, 75, 60))
    draw.text((1300, 1520), "+56 9 6677 9662", font=font_bold, fill=(16, 75, 60))

    img.save('anuncio_moderno.png')

def create_elegant_ad():
    width, height = 2480, 1748
    # Fondo claro
    img = Image.new('RGB', (width, height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)
    
    # Borde verde
    draw.rectangle([0, 0, width-1, height-1], outline=(16, 75, 60), width=40)
    
    # Panel derecho verde
    draw.rectangle([1400, 0, width, height], fill=(16, 75, 60))

    try:
        font_xl = ImageFont.truetype("C:\\Windows\\Fonts\\georgiab.ttf", 130)
        font_large = ImageFont.truetype("C:\\Windows\\Fonts\\georgiai.ttf", 80)
        font_medium = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 60)
        font_small = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 60)
    except:
        font_xl = ImageFont.load_default()
        font_large = font_xl
        font_medium = font_xl
        font_small = font_xl

    # Logo
    if os.path.exists('src/web/assets/NUEVO LOGO FV.png'):
        logo = Image.open('src/web/assets/NUEVO LOGO FV.png').convert('RGBA')
        basewidth = 800
        wpercent = (basewidth / float(logo.size[0]))
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.LANCZOS)
        img.paste(logo, (150, 200), logo)

    # Textos izquierda
    draw.text((150, 750), "El Futuro de la\nGestion Patrimonial", font=font_xl, fill=(16, 75, 60))
    draw.text((150, 1150), "Garantizando la proteccion intergeneracional\nde su capital con inteligencia, solidez\ny absoluto respaldo institucional.", font=font_medium, fill=(74, 85, 104))

    # Textos derecha
    import textwrap
    quote = '"Nuestro negocio no es vender productos. Es entregarle claridad, tiempo y paz mental."'
    lines = textwrap.wrap(quote, width=22)
    y_text = 400
    for line in lines:
        draw.text((1500, y_text), line, font=font_large, fill=(255, 255, 255))
        y_text += 100
        
    draw.text((1500, 1200), "contacto@fv-inversiones.com", font=font_small, fill=(255, 255, 255))
    draw.text((1500, 1300), "+56 9 6677 9662", font=font_small, fill=(255, 255, 255))

    img.save('anuncio_elegante.png')

try:
    create_modern_ad()
    create_elegant_ad()
    print("PNGs creados exitosamente")
except Exception as e:
    print(f"Error: {e}")
