import zipfile
import xml.etree.ElementTree as ET

file_path = r'C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\Archivo de audio_ONE VISION.docx'
out_path = r'C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\audio_one_vision.txt'

document = zipfile.ZipFile(file_path)
xml_content = document.read('word/document.xml')
document.close()

tree = ET.XML(xml_content)
paragraphs = []
for paragraph in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    texts = [node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
    if texts:
        paragraphs.append(''.join(texts))

with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(paragraphs))
