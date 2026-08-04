import re
import xml.etree.ElementTree as ET

tree = ET.parse(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\NUEVO LOGO FV.svg")
root = tree.getroot()
ns = {'svg': 'http://www.w3.org/2000/svg'}
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')
ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')

def snap_val(val_str):
    try:
        val = float(val_str)
        # Snap to nearest 5
        snapped = round(val / 5.0) * 5.0
        return str(snapped)
    except:
        return val_str

for path in root.findall('.//svg:path', ns):
    d = path.get('d', '')
    if not d: continue
    
    # Let's completely flatten the path by replacing 'c' (bezier curves) with straight lines!
    # But wait, 'c' uses relative coordinates for 3 points (dx1, dy1, dx2, dy2, dx, dy).
    # If we just replace 'c' with 'l' and take the last pair of coordinates, it becomes a straight line!
    # Example: c dx1,dy1 dx2,dy2 dx,dy -> l dx,dy
    
    # Replace relative cubic beziers 'c' with relative lines 'l'
    d = re.sub(r'c\s+([-\d.]+),([-\d.]+)\s+([-\d.]+),([-\d.]+)\s+([-\d.]+),([-\d.]+)', r'l \5,\6', d)
    # Replace absolute cubic beziers 'C' with absolute lines 'L'
    d = re.sub(r'C\s+([-\d.]+),([-\d.]+)\s+([-\d.]+),([-\d.]+)\s+([-\d.]+),([-\d.]+)', r'L \5,\6', d)
    
    # Now, round all numbers to nearest 1 pixel to clean up
    def round_match(m):
        val = float(m.group(0))
        return str(round(val))
        
    d_rounded = re.sub(r'[-\d.]+', round_match, d)
    path.set('d', d_rounded)
    
    # If this is the background black block (path 30), let's delete it completely!
    # style="fill:#000000"
    style = path.get('style', '')
    if 'fill:#000000' in style:
        # We can't easily delete while iterating, let's just make it completely transparent
        path.set('style', 'display:none;')

tree.write(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\LOGO_MAGICO.svg")
print("Done")
