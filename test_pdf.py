import sys
import os
import tempfile
sys.path.append(os.path.abspath("."))
from src.utils.pdf_generator_macro import generate_macro_pdf

temp_pdf = "test_macro.pdf"
try:
    generate_macro_pdf("Guillermo", "Texto de prueba", temp_pdf)
    print("PDF generado correctamente.")
except Exception as e:
    print(f"ERROR: {e}")
