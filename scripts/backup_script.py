import os
import zipfile

def make_zip(zip_path, source_dir):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for r, d, files in os.walk(source_dir):
            if any(x in r for x in ['.git', 'venv', '__pycache__', 'backups', 'scratch']):
                continue
            for f in files:
                zf.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), source_dir))

if __name__ == '__main__':
    make_zip('backups/respaldo_macro_history.zip', '.')
    print("Backup completado exitosamente.")
