import pdfplumber

with pdfplumber.open(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\scratch\cotizaciones historicas.pdf") as pdf:
    print(pdf.pages[0].extract_text())
