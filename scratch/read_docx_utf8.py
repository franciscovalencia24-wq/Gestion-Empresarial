import sys
from docx import Document

try:
    doc = Document("Informe Técnico Family Office Digital.docx")
    with open("scratch/docx_content_utf8.txt", "w", encoding="utf-8") as f:
        for p in doc.paragraphs:
            if p.text.strip():
                f.write(p.text + "\n")
except Exception as e:
    print("Error:", e)
