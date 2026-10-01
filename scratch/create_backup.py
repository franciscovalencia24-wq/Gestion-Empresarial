import os
import zipfile
import datetime

def create_backup():
    base_dir = r"c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR"
    backup_dir = os.path.join(base_dir, "backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = os.path.join(backup_dir, f"backup_sistema_{timestamp}.zip")
    
    exclude_dirs = {'.git', '.venv', 'venv', 'env', '__pycache__', 'backups', 'scratch', '.gemini', 'node_modules'}
    
    print(f"Creando respaldo en: {zip_filename}")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # Excluir directorios
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                # No respaldar el propio archivo zip ni archivos de scratch irrelevantes
                if file.endswith('.zip') or file.endswith('.pyc'):
                    continue
                
                arcname = os.path.relpath(file_path, base_dir)
                zipf.write(file_path, arcname)
                
    print(f"¡Respaldo completado con éxito! Tamaño: {os.path.getsize(zip_filename) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    create_backup()
