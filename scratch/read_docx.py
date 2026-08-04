import sys
from docx import Document

try:
    doc = Document("Informe Técnico Family Office Digital.docx")
    for p in doc.paragraphs:
        if p.text.strip():
            print(p.text)
except Exception as e:
    print("Error:", e)
