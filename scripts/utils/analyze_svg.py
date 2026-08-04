import xml.etree.ElementTree as ET

tree = ET.parse(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\NUEVO LOGO FV.svg")
root = tree.getroot()
ns = {'svg': 'http://www.w3.org/2000/svg'}

print("Paths in original SVG:")
for idx, path in enumerate(root.findall('.//svg:path', ns)):
    d = path.get('d', '')
    style = path.get('style', '')
    if d:
        print(f"Path {idx}: {d[:100]}... (Style: {style[:50]})")
