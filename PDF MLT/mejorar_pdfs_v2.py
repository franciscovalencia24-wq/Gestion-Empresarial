import os
import fitz
import cv2
import numpy as np

def enhance_image_clahe(img_array):
    # Convert RGB to Grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # 1. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # This enhances contrast locally without washing out faint text or turning shadows into black blocks.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl1 = clahe.apply(gray)
    
    # 2. Simple Normalization (Stretch contrast from 0 to 255)
    normalized = cv2.normalize(cl1, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    
    # 3. Optional slight unsharp masking to sharpen text
    gaussian_3 = cv2.GaussianBlur(normalized, (0, 0), 2.0)
    unsharp_image = cv2.addWeighted(normalized, 1.5, gaussian_3, -0.5, 0, normalized)
    
    return unsharp_image

def process_single_pdf(input_pdf_path, output_pdf_path):
    print(f"Mejorando con CLAHE (Contraste Suave): {input_pdf_path}")
    doc = fitz.open(input_pdf_path)
    new_doc = fitz.open()
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Higher zoom for better clarity
        zoom = 3.0    
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        enhanced_img = enhance_image_clahe(img_array)
        
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
    output_file = os.path.join(current_dir, "Mejorados", "PRUEBA_CLAHE_4530949-5 (2).pdf")
    
    if os.path.exists(input_file):
        process_single_pdf(input_file, output_file)
    else:
        print(f"No se encontro el archivo de prueba: {input_file}")
