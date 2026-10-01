import os
import fnmatch

def generate_tree(dir_path, exclude_dirs, exclude_files):
    tree_str = f"Estructura del Proyecto BD Senior\n=================================\n\n"
    
    for root, dirs, files in os.walk(dir_path):
        # Filtramos directorios ignorados
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in exclude_dirs)]
        
        # Ordenamos
        dirs.sort()
        files.sort()
        
        level = root.replace(dir_path, '').count(os.sep)
        indent = '    ' * level
        basename = os.path.basename(root)
        if basename == "":
            basename = "BD SENIOR"
        
        tree_str += f"{indent}{basename}/\n"
        
        subindent = '    ' * (level + 1)
        for f in files:
            if not any(fnmatch.fnmatch(f, p) for p in exclude_files):
                tree_str += f"{subindent}{f}\n"
                
    return tree_str

if __name__ == "__main__":
    exclude_dirs = ['.git', '__pycache__', 'venv', 'env', '.gemini', 'node_modules', '.pytest_cache', 'scratch', 'data', 'templates_pdf']
    exclude_files = ['*.pyc', '*.pyo', '*.pyd', '.DS_Store', '*.pdf', '*.xlsx', '*.png', '*.jpg', '*.log', '*.db', '*.sqlite3']
    
    project_path = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR"
    out_path = os.path.join(project_path, "scratch", "project_tree.txt")
    
    tree_content = generate_tree(project_path, exclude_dirs, exclude_files)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tree_content)
        
    print("Árbol generado en:", out_path)
