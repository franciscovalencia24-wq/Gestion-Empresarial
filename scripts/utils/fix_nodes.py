import numpy as np
from svgpathtools import svg2paths, Path, Line, wsvg
import sys

paths, attributes = svg2paths(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\NUEVO LOGO FV.svg")

def snap_points(paths):
    rectified_paths = []
    
    for path in paths:
        if not path:
            rectified_paths.append(path)
            continue
            
        points = []
        for segment in path:
            points.append(segment.start)
            points.append(segment.end)
            
        pts_array = np.array([[p.real, p.imag] for p in points])
        if len(pts_array) == 0:
            rectified_paths.append(path)
            continue
            
        for i in range(2): 
            vals = pts_array[:, i]
            sorted_idx = np.argsort(vals)
            sorted_vals = vals[sorted_idx]
            
            clusters = []
            curr_cluster = [sorted_idx[0]]
            for j in range(1, len(sorted_vals)):
                if abs(sorted_vals[j] - vals[curr_cluster[-1]]) < 5:
                    curr_cluster.append(sorted_idx[j])
                else:
                    clusters.append(curr_cluster)
                    curr_cluster = [sorted_idx[j]]
            clusters.append(curr_cluster)
            
            for c in clusters:
                mean_val = np.mean(vals[c])
                pts_array[c, i] = mean_val
                
        new_path = Path()
        idx = 0
        for segment in path:
            start = complex(pts_array[idx*2, 0], pts_array[idx*2, 1])
            end = complex(pts_array[idx*2+1, 0], pts_array[idx*2+1, 1])
            new_path.append(Line(start, end))
            idx += 1
            
        rectified_paths.append(new_path)
    return rectified_paths

rectified = snap_points(paths)
wsvg(rectified, attributes=attributes, filename=r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\LOGO_ALINEADO_PERFECTO.svg")
print("Done")
