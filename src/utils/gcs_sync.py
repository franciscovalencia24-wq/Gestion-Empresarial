import os
import logging

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "fv-asesorias-db-storage-fv")
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gen-lang-client-0304091025")

logger = logging.getLogger("gcs_sync")

def get_gcs_client():
    try:
        from google.cloud import storage
        from google.oauth2 import service_account
        import streamlit as st
        
        # Intenta usar Streamlit Secrets (Nube)
        try:
            if "gcp_service_account" in st.secrets:
                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"]
                )
                return storage.Client(credentials=credentials, project=PROJECT_ID)
        except Exception:
            pass # Si no hay st.secrets o falla, cae al entorno local
            
        # Fallback para desarrollo local
        return storage.Client(project=PROJECT_ID)
    except Exception as e:
        logger.warning(f"No se pudo inicializar cliente de GCS: {e}")
        return None

def download_db_from_gcs(db_filename="crm_database.db", destination_path="data/crm_database.db"):
    """
    Descarga la última versión de la base de datos desde Google Cloud Storage (GCS)
    al iniciar la aplicación web en la nube, usando una descarga atómica para evitar corrupción.
    """
    try:
        client = get_gcs_client()
        if not client:
            return False
        
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(db_filename)
        if blob.exists():
            import shutil
            import sqlite3
            # 1. Liberar conexiones SQLAlchemy antes de sobreescribir
            try:
                from src.database.connection import engine
                engine.dispose()
            except Exception:
                pass
                
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            temp_path = destination_path + ".download.tmp"
            
            # 2. Descargar a un archivo temporal primero
            blob.download_to_filename(temp_path)
            
            # 3. Validar integridad del archivo descargado
            try:
                conn_test = sqlite3.connect(temp_path)
                cursor = conn_test.cursor()
                cursor.execute("PRAGMA integrity_check;")
                res = cursor.fetchone()
                conn_test.close()
                if res and res[0] != "ok":
                    logger.warning("El archivo descargado de GCS presenta corrupción. Se permitirá la descarga para que el Salvavidas (Auto-Recovery) de connection.py intente rescatar los datos en el siguiente paso.")
            except Exception as e:
                logger.error(f"Fallo verificando integridad de la descarga, pero se continuará: {e}")

            # 4. Reemplazo Atómico
            shutil.move(temp_path, destination_path)
            logger.info(f"DB descargada desde GCS: gs://{BUCKET_NAME}/{db_filename} -> {destination_path}")
            return True
        else:
            return False
    except Exception as e:
        logger.warning(f"Error descargando DB desde GCS: {e}")
        return False

def upload_db_to_gcs(source_path="data/crm_database.db", db_filename="crm_database.db"):
    """
    Sube la base de datos local a Google Cloud Storage (GCS)
    después de un guardado o actualización de clientes/movimientos,
    usando sqlite3.backup() para asegurar consistencia en caliente.
    """
    if not os.path.exists(source_path):
        return False
    try:
        import sqlite3
        client = get_gcs_client()
        if not client:
            return False
            
        backup_path = source_path + ".safe_upload.tmp"
        
        # 1. Crear snapshot consistente en caliente
        src = sqlite3.connect(source_path)
        dst = sqlite3.connect(backup_path)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()
        
        # 2. Subir el snapshot congelado a GCS
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(db_filename)
        blob.upload_from_filename(backup_path)
        
        # 3. Limpiar temporal
        if os.path.exists(backup_path):
            os.remove(backup_path)
            
        logger.info(f"DB subida exitosamente a GCS en modo SafeSync: {source_path} -> gs://{BUCKET_NAME}/{db_filename}")
        return True
    except Exception as e:
        logger.warning(f"Error subiendo DB a GCS: {e}")
        return False
