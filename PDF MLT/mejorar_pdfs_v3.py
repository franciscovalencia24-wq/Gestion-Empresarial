import os
import fitz
import cv2
import numpy as np

def enhance_faint_text(img_array):
    # Convert to Grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # 1. Contrast Stretching (Make darks darker and lights lighter)
    # We clip the histogram so that any light gray becomes pure white, and any dark gray becomes pure black.
    # This is better than adaptive thresholding for very faint text.
    alpha = 1.5 # Contrast control (1.0-3.0)
    beta = -50  # Brightness control (0-100)
    adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
    
    # 2. Morphological Erosion (Thickens black text on white background)
    # The text in the screenshot is "dotted" and faint. 
    # Erosion shrinks the bright regions (white paper) and expands the dark regions (black text).
    kernel = np.ones((2,2), np.uint8) # Small 2x2 kernel to not make it too bold
    thickened = cv2.erode(adjusted, kernel, iterations=1)
    
    # 3. Final Binarization to force it to black and white
    # Anything darker than 200 becomes 0 (black), everything else becomes 255 (white)
    _, binary = cv2.threshold(thickened, 200, 255, cv2.THRESH_BINARY)
    
    return binary

def process_single_pdf(input_pdf_path, output_pdf_path):
    print(f"Mejorando texto débil: {input_pdf_path}")
    doc = fitz.open(input_pdf_path)
    new_doc = fitz.open()
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Super high resolution to catch every faint dot of ink
        zoom = 4.0    
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        enhanced_img = enhance_faint_text(img_array)
        
        _, buffer = cv2.imencode('.png', enhanced_img)
        
        img_rect = fitz.Rect(0, 0, enhanced_img.shape[1], enhanced_img.shape[0])
        new_page = new_doc.new_page(width=img_rect.width, height=img_rect.height)
        new_page.insert_image(img_rect, stream=buffer.tobytes())
        
    new_doc.save(output_pdf_path)
    new_doc.close()
    doc.close()
    print(f"Guardado exitosamente: {output_pdf_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, "4530949-5 (2).PDF")
    output_file = os.path.join(current_dir, "Mejorados", "PRUEBA_ENGROSADO_4530949-5 (2).pdf")
    
    if os.path.exists(input_file):
        process_single_pdf(input_file, output_file)
    else:
        print(f"No se encontro el archivo de prueba: {input_file}")
