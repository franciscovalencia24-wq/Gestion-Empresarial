import os
import json
import datetime
import pandas as pd

BACKUP_DIR = os.path.join("data", "backups")
HISTORY_DIR = os.path.join(BACKUP_DIR, "history")

def save_client_backup(rut: str, backup_payload: dict) -> str:
    """
    Guarda una copia de seguridad física en disco (JSON) de la ficha completa del cliente
    antes de interactuar con la base de datos SQLite. Esto garantiza CERO pérdida de información.
    """
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        os.makedirs(HISTORY_DIR, exist_ok=True)
        
        clean_rut = str(rut).replace(".", "").replace("-", "_").strip()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convertir DataFrames a dict si vienen como DataFrames
        serializable_payload = {}
        for k, v in backup_payload.items():
            if isinstance(v, pd.DataFrame):
                serializable_payload[k] = v.to_dict(orient="records")
            elif isinstance(v, (datetime.date, datetime.datetime)):
                serializable_payload[k] = str(v)
            else:
                serializable_payload[k] = v
                
        serializable_payload["_saved_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        serializable_payload["_rut"] = str(rut)
        
        # Guardar archivo 'last' y archivo con timestamp en historial
        last_file = os.path.join(BACKUP_DIR, f"backup_client_{clean_rut}_last.json")
        hist_file = os.path.join(HISTORY_DIR, f"backup_client_{clean_rut}_{timestamp}.json")
        
        with open(last_file, "w", encoding="utf-8") as f:
            json.dump(serializable_payload, f, ensure_ascii=False, indent=2, default=str)
            
        with open(hist_file, "w", encoding="utf-8") as f:
            json.dump(serializable_payload, f, ensure_ascii=False, indent=2, default=str)
            
        return last_file
    except Exception as e:
        print(f"Error creando backup en disco: {e}")
        return ""

def get_latest_client_backup(rut: str) -> dict:
    """Recupera la última copia de seguridad guardada en disco para el cliente."""
    clean_rut = str(rut).replace(".", "").replace("-", "_").strip()
    last_file = os.path.join(BACKUP_DIR, f"backup_client_{clean_rut}_last.json")
    if os.path.exists(last_file):
        try:
            with open(last_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error leyendo backup {last_file}: {e}")
    return {}
import os
import zipfile
import datetime
import threading

def create_system_backup(base_dir=None):
    if not base_dir:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    backup_dir = os.path.join(base_dir, "backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = os.path.join(backup_dir, f"backup_sistema_{timestamp}.zip")
    
    exclude_dirs = {'.git', '.venv', 'venv', 'env', '__pycache__', 'backups', 'scratch', '.gemini', 'node_modules'}
    
    def run_backup():
        try:
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(base_dir):
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file.endswith('.zip') or file.endswith('.pyc'):
                            continue
                        arcname = os.path.relpath(file_path, base_dir)
                        zipf.write(file_path, arcname)
        except Exception as e:
            print(f"Error in background backup: {e}")

    # Run in background to avoid blocking the UI
    t = threading.Thread(target=run_backup)
    t.start()
    return zip_filename

def create_system_backup_sync(base_dir=None, upload_to_cloud=True):
    """
    Creates a full system backup synchronously. Safely copies the active database using
    shutil.copy2 to avoid locking issues during the zip compression.
    Returns the path to the created ZIP, its size in MB, cloud_synced_bool and cloud_msg.
    """
    import shutil
    import tempfile
    
    if not base_dir:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    backup_dir = os.path.join(base_dir, "backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = os.path.join(backup_dir, f"BDSENIOR_Backup_{timestamp}.zip")
    
    # 1. Rutas de bases de datos posibles
    db_paths = [
        os.path.join(base_dir, "database.sqlite"),
        os.path.join(base_dir, "data", "crm_database.db")
    ]
    
    # 2. Rutas de configuración o assets a respaldar
    key_dirs = ['assets', 'data', 'src/config']
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            # --- RESPALDAR BASES DE DATOS DE FORMA SEGURA ---
            for db_path in db_paths:
                if os.path.exists(db_path):
                    # Copia temporal
                    temp_db = os.path.join(temp_dir, os.path.basename(db_path))
                    shutil.copy2(db_path, temp_db)
                    # Escribir en zip preservando estructura original
                    arcname = os.path.relpath(db_path, base_dir)
                    zipf.write(temp_db, arcname)
                    
            # --- RESPALDAR CONFIGURACIONES Y ASSETS ---
            for kd in key_dirs:
                target_dir = os.path.join(base_dir, kd)
                if os.path.exists(target_dir):
                    for root, dirs, files in os.walk(target_dir):
                        if 'backups' in dirs:
                            dirs.remove('backups')
                        for file in files:
                            # Evitamos la base original que ya copiamos seguro, o basuras
                            if file in ['crm_database.db', 'database.sqlite']:
                                continue
                            if file.endswith('.zip') or file.endswith('.pyc') or file.startswith('.'):
                                continue
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, base_dir)
                            zipf.write(file_path, arcname)
                            
            # Respaldar .env (opcional, pero crítico como conf)
            env_path = os.path.join(base_dir, ".env")
            if os.path.exists(env_path):
                zipf.write(env_path, ".env")
                
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    
    cloud_synced_bool = False
    cloud_msg = "Sincronización a la nube deshabilitada."
    
    if upload_to_cloud:
        try:
            from src.utils.gcs_sync import upload_backup_zip_to_gcs
            cloud_synced_bool, cloud_msg = upload_backup_zip_to_gcs(zip_filename)
        except Exception as e:
            cloud_synced_bool = False
            cloud_msg = f"Fallo al intentar sincronizar con GCS: {e}"
            
    return zip_filename, size_mb, cloud_synced_bool, cloud_msg

