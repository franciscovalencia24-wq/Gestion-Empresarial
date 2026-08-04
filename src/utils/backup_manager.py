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
