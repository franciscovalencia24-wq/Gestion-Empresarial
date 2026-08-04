import os
import fitz
import cv2
import numpy as np

def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def enhance_image(img_array):
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    # Corrección Gamma agresiva
    darkened = adjust_gamma(gray, gamma=0.35)
    return darkened

def process_pdfs(input_dir):
    output_dir = os.path.join(input_dir, "Mejorados")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No se encontraron archivos PDF en la carpeta.")
        return

    print(f"Procesando {len(pdf_files)} archivos PDF con Correccion Gamma...")

    for pdf_filename in pdf_files:
        input_pdf_path = os.path.join(input_dir, pdf_filename)
        output_pdf_path = os.path.join(output_dir, f"{os.path.splitext(pdf_filename)[0]}_Mejorado.pdf")
        
        print(f"Mejorando: {pdf_filename}")
        
        doc = fitz.open(input_pdf_path)
        new_doc = fitz.open()
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Zoom alto
            zoom = 3.0    
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
            enhanced_img = enhance_image(img_array)
            
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
    process_pdfs(current_dir)
    print("\n¡Proceso masivo terminado!")
