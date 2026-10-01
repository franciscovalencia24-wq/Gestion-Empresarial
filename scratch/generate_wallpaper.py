from PIL import Image, ImageDraw, ImageFont
import os

def create_wallpaper(qr_path, output_path):
    # Samsung A54 dimensions
    WIDTH = 1080
    HEIGHT = 2340
    
    # Create the base image (dark slate blue background)
    wallpaper = Image.new('RGB', (WIDTH, HEIGHT), '#0f172a')
    
    # Open the QR code
    if not os.path.exists(qr_path):
        print(f"Error: QR code {qr_path} not found.")
        return
        
    qr_img = Image.open(qr_path).convert("RGBA")
    
    # We want the QR code to be big enough to easily scan, but leave margins.
    # Say, 75% of the screen width
    qr_size = int(WIDTH * 0.75)
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    
    # Let's add a soft rounded border to the QR code to make it look premium
    # Create a rounded mask for the QR code
    mask = Image.new('L', (qr_size, qr_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, qr_size, qr_size), radius=30, fill=255)
    
    # Calculate position (dead center)
    x = (WIDTH - qr_size) // 2
    # Place it slightly below center to leave room for the lockscreen clock at the top
    y = (HEIGHT - qr_size) // 2 + 100 
    
    # Paste the QR code onto the wallpaper using the rounded mask
    wallpaper.paste(qr_img, (x, y), mask)
    
    # Add a nice little text or branding at the bottom?
    # Or just leave it clean. Let's just leave it clean to be safe, or add a subtle text.
    
    # Save the wallpaper
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wallpaper.save(output_path, quality=100)
    print(f"Wallpaper saved to {output_path}")

create_wallpaper("c:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/assets/qr_vcard_fv.png", "c:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/assets/wallpaper_a54_vcard.png")
