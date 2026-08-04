import os
import fitz  # PyMuPDF
import cv2
import numpy as np

def enhance_image(img_array):
    # Convert RGB to Grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Apply slightly blur to remove noise (optional, but helps with old scanners)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Adaptive Thresholding: This is the best technique for scanned documents
    # It calculates the threshold for small regions of the image, dealing with uneven lighting/shadows.
    enhanced = cv2.adaptiveThreshold(
        blurred, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 2
    )
    
    # Optional: Morphological operations to thicken text if it's too thin
    # kernel = np.ones((2,2),np.uint8)
    # enhanced = cv2.erode(enhanced, kernel, iterations = 1)
    
    return enhanced

def process_pdfs(input_dir):
    output_dir = os.path.join(input_dir, "Mejorados")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Find all PDFs in the directory (excluding the 'Mejorados' folder)
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No se encontraron archivos PDF en la carpeta.")
        return

    print(f"Procesando {len(pdf_files)} archivos PDF...")

    for pdf_filename in pdf_files:
        input_pdf_path = os.path.join(input_dir, pdf_filename)
        output_pdf_path = os.path.join(output_dir, f"{os.path.splitext(pdf_filename)[0]}_Mejorado.pdf")
        
        print(f"Mejorando: {pdf_filename}")
        
        # Open the original PDF
        doc = fitz.open(input_pdf_path)
        
        # Create a new empty PDF for the output
        new_doc = fitz.open()
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Render page to an image (zoom factor determines resolution, 2.0 or 3.0 is good for OCR/reading)
            zoom = 2.0    
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert PyMuPDF pixmap to numpy array for OpenCV
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
            
            # Enhance the image
            enhanced_img = enhance_image(img_array)
            
            # Convert enhanced grayscale image back to a format PyMuPDF can use
            # We need to encode it back to an image format like PNG or JPEG in memory
            _, buffer = cv2.imencode('.png', enhanced_img)
            
            # Insert the processed image as a new page in the new PDF
            img_rect = fitz.Rect(0, 0, enhanced_img.shape[1], enhanced_img.shape[0])
            new_page = new_doc.new_page(width=img_rect.width, height=img_rect.height)
            new_page.insert_image(img_rect, stream=buffer.tobytes())
            
        # Save the new document
        new_doc.save(output_pdf_path)
        new_doc.close()
        doc.close()
        
        print(f"Guardado exitosamente: {output_pdf_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    process_pdfs(current_dir)
    print("\n¡Proceso de mejora de calidad terminado!")
