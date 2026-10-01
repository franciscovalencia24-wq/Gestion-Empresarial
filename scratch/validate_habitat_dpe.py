import pdfplumber
import sys

pdf_path = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\scratch\CertificadoAfpHabitat.pdf"

print("Extrayendo texto del PDF...")
try:
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for i, page in enumerate(pdf.pages):
            text += f"\n--- Página {i+1} ---\n"
            text += page.extract_text() or ""
            
            # Extract tables to see if they are easily parsed
            tables = page.extract_tables()
            if tables:
                text += f"\n--- Tablas detectadas en Página {i+1} ---\n"
                for table in tables:
                    for row in table:
                        text += str(row) + "\n"

    with open(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\scratch\habitat_extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Texto extraído guardado en scratch/habitat_extracted_text.txt")
except Exception as e:
    print(f"Error: {e}")
