from svgpathtools import svg2paths
import numpy as np

paths, attributes = svg2paths(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\NUEVO LOGO FV.svg")

for idx, path in enumerate(paths):
    if not path: continue
    
    # Get all points
    points = []
    for segment in path:
        points.append(segment.start)
        points.append(segment.end)
        
    pts = np.array([[p.real, p.imag] for p in points])
    
    xmin, xmax = np.min(pts[:, 0]), np.max(pts[:, 0])
    ymin, ymax = np.min(pts[:, 1]), np.max(pts[:, 1])
    
    # also print style
    style = attributes[idx].get('style', '')
    
    print(f"Path {idx}: x=[{xmin:.1f}, {xmax:.1f}], y=[{ymin:.1f}, {ymax:.1f}], w={xmax-xmin:.1f}, h={ymax-ymin:.1f}")
    if '000000' in style: print("  (BLACK BACKGROUND)")
    elif '383838' in style or '363636' in style: print("  (DARK GREY SHAPE)")
    elif '016a53' in style: print("  (GREEN SHAPE)")
