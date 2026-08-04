import re
import xml.etree.ElementTree as ET

tree = ET.parse(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\NUEVO LOGO FV.svg")
root = tree.getroot()
ns = {'svg': 'http://www.w3.org/2000/svg'}

def extract(path_d):
    # Find all coordinates
    # We will just find all floats
    nums = [float(x) for x in re.findall(r'-?\d+\.\d+|-?\d+', path_d)]
    return nums

paths = root.findall('.//svg:path', ns)
for idx, path in enumerate(paths):
    style = path.get('style', '')
    if '000000' in style: continue
    if '383838' in style or '363636' in style or '016a53' in style:
        nums = extract(path.get('d', ''))
        print(f"Path {idx}: {len(nums)} numbers")
        print(nums[:20], "...")
