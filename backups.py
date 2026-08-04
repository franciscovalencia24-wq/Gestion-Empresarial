import os
import shutil
import zipfile
from datetime import datetime

def check_external_drives():
    """Busca pendrives o discos duros externos conectados (D:, E:, F:, etc.)"""
    drives = [f"{chr(x)}:" for x in range(68, 91)] # De D: a Z:
    valid_drives = [d for d in drives if os.path.exists(d)]
    return valid_drives

def create_checkpoint(description="", export_to_cloud=True, export_to_usb=True):
    """
    Crea un respaldo total del sistema en formato ZIP, excluyendo archivos pesados innecesarios.
    """
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_desc = description.replace(' ', '_')
    zip_filename = f"BDSENIOR_Backup_{timestamp}_{safe_desc}.zip"
    zip_path = os.path.join(backup_dir, zip_filename)
    
    # Exclusiones
    exclude_dirs = ['.git', 'venv', '__pycache__', '.pytest_cache', 'backups']
    exclude_files = ['.env'] # NUNCA respaldar secretos en crudo
    
    print(f"[*] Comprimiendo el ecosistema en {zip_filename}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # Filtrar carpetas ignoradas
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files or file.endswith('.zip'):
                    continue
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file_path)
                
    print(f" [OK] Respaldo local creado exitosamente: {zip_path}")
    
    # --- RESPALDO EN NUBE (ONEDRIVE/GOOGLE DRIVE) ---
    if export_to_cloud:
        cloud_path = os.path.expanduser("~/OneDrive/Respaldo_BDSENIOR")
        if not os.path.exists(cloud_path):
            try:
                os.makedirs(cloud_path)
            except Exception:
                cloud_path = None
        
        if cloud_path:
            cloud_file = os.path.join(cloud_path, zip_filename)
            shutil.copy2(zip_path, cloud_file)
            print(f" [NUBE] Respaldo sincronizado en la nube: {cloud_file}")
            
    # --- RESPALDO EN PENDRIVE ---
    if export_to_usb:
        drives = check_external_drives()
        if drives:
            # Seleccionar el primer disco extraíble disponible (usualmente D: o E:)
            target_drive = drives[0]
            usb_folder = os.path.join(target_drive, "BDSENIOR_Respaldos")
            if not os.path.exists(usb_folder):
                try:
                    os.makedirs(usb_folder)
                except:
                    pass
            
            if os.path.exists(usb_folder):
                usb_file = os.path.join(usb_folder, zip_filename)
                shutil.copy2(zip_path, usb_file)
                print(f" [USB] Respaldo físico guardado en Pendrive/Disco: {usb_file}")
        else:
            print(" [!] No se detectaron pendrives para el respaldo físico.")

    return zip_path

if __name__ == "__main__":
    create_checkpoint("resguardo_semanal", export_to_cloud=True, export_to_usb=True)
