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
    al iniciar la aplicación web en la nube.
    """
    try:
        client = get_gcs_client()
        if not client:
            return False
        
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(db_filename)
        if blob.exists():
            # Validación de prevención de downgrade de BD
            if os.path.exists(destination_path):
                local_mtime = os.path.getmtime(destination_path)
                remote_mtime = blob.updated.timestamp()
                
                # Si el archivo local fue modificado más recientemente que la copia en GCS
                if local_mtime > remote_mtime:
                    logger.warning("PREVENCIÓN DE PÉRDIDA DE DATOS: La base de datos local es más reciente que la versión en GCS. Se cancelará la descarga para evitar sobreescribir tus movimientos manuales recientes.")
                    return False
                    
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            blob.download_to_filename(destination_path)
            logger.info(f"DB descargada exitosamente desde GCS: gs://{BUCKET_NAME}/{db_filename} -> {destination_path}")
            return True
        else:
            return False
    except Exception as e:
        logger.warning(f"Error descargando DB desde GCS: {e}")
        return False

def upload_db_to_gcs(source_path="data/crm_database.db", db_filename="crm_database.db"):
    """
    Sube la base de datos local a Google Cloud Storage (GCS)
    después de un guardado o actualización de clientes/movimientos.
    """
    if not os.path.exists(source_path):
        return False
    try:
        client = get_gcs_client()
        if not client:
            return False
        
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(db_filename)
        blob.upload_from_filename(source_path)
        logger.info(f"DB subida exitosamente a GCS: {source_path} -> gs://{BUCKET_NAME}/{db_filename}")
        return True
    except Exception as e:
        logger.warning(f"Error subiendo DB a GCS: {e}")
        return False
