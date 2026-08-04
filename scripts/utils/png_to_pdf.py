from PIL import Image
import os

def convert_to_pdf():
    # Rutas de las imágenes
    anuncio_path = os.path.abspath("assets/anuncio_revista_altus.png")
    infografia_path = os.path.abspath("assets/infografia_seguro.png")
    
    # Abrir imágenes y asegurar que estén en RGB (requerido por PDF)
    img1 = Image.open(anuncio_path).convert('RGB')
    img2 = Image.open(infografia_path).convert('RGB')
    
    # 1. Guardar cada una como PDF individual
    img1.save("assets/anuncio_revista_altus.pdf")
    img2.save("assets/infografia_seguro.pdf")
    print("PDFs individuales generados con éxito.")
    
    # 2. Guardar ambas en un solo documento PDF (como una presentación de 2 slides)
    img1.save("assets/FV_Presentacion_Institucional.pdf", save_all=True, append_images=[img2])
    print("PDF combinado (2 páginas) generado con éxito en assets/FV_Presentacion_Institucional.pdf")

if __name__ == "__main__":
    convert_to_pdf()
