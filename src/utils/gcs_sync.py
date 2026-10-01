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
            try:
                from src.database.connection import engine
                engine.dispose()
            except Exception:
                pass
                
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Limpiar archivos temporales de SQLite (Journal/WAL) para evitar corrupción 
            # al sobreescribir el archivo principal
            wal_path = destination_path + "-wal"
            shm_path = destination_path + "-shm"
            for p in [wal_path, shm_path]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception as e:
                        logger.warning(f"No se pudo borrar {p}: {e}")
            
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
            
            # 5. Si estaba corrupto, forzar el rescate inmediatamente
            try:
                from src.database.connection import force_recover_db
                force_recover_db(os.path.abspath(destination_path))
            except Exception as rec_err:
                logger.error(f"Error invocando la rutina de rescate forzado: {rec_err}")
                
            logger.info(f"DB descargada desde GCS: gs://{BUCKET_NAME}/{db_filename} -> {destination_path}")
            # Guardamos la generación en session_state de streamlit si está disponible
            try:
                import streamlit as st
                st.session_state.gcs_db_generation = blob.generation
            except:
                pass
            return True
        else:
            return False
    except Exception as e:
        logger.warning(f"Error descargando DB desde GCS: {e}")
        return False

def get_current_gcs_generation(db_filename="crm_database.db"):
    """
    Obtiene el generation number actual de la Bóveda en GCS sin descargarla.
    Retorna None si no existe o hay error.
    """
    try:
        client = get_gcs_client()
        if not client: return None
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(db_filename)
        blob.reload()
        return blob.generation
    except Exception as e:
        logger.warning(f"No se pudo obtener generación de GCS: {e}")
        return None

def upload_db_to_gcs(source_path="data/crm_database.db", db_filename="crm_database.db", expected_generation=None):
    """
    Sube la base de datos local a Google Cloud Storage (GCS)
    después de un guardado o actualización de clientes/movimientos,
    usando sqlite3.backup() para asegurar consistencia en caliente.
    
    Si se proporciona expected_generation, la subida fallará (levantando PreconditionFailed)
    si la nube fue modificada por alguien más en el intertanto.
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
        
        try:
            if expected_generation is not None:
                blob.upload_from_filename(backup_path, if_generation_match=expected_generation)
            else:
                blob.upload_from_filename(backup_path)
        except Exception as upload_error:
            # Capturar el HTTP 412 (Precondition Failed)
            if "412 Precondition Failed" in str(upload_error) or "conditionNotMet" in str(upload_error):
                logger.error("Conflicto de Concurrencia: La Bóveda en la Nube fue modificada por otro usuario. Subida abortada.")
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                raise Exception("CONCURRENCY_CONFLICT")
            else:
                raise upload_error
        
        # 3. Limpiar temporal
        if os.path.exists(backup_path):
            os.remove(backup_path)
            
        logger.info(f"DB subida exitosamente a GCS en modo SafeSync: {source_path} -> gs://{BUCKET_NAME}/{db_filename}")
        
        # Actualizamos la versión local segura en session_state
        try:
            import streamlit as st
            blob.reload()
            st.session_state.gcs_db_generation = blob.generation
        except:
            pass
            
        return True
    except Exception as e:
        if str(e) == "CONCURRENCY_CONFLICT":
            raise e
        logger.warning(f"Error subiendo DB a GCS: {e}")
        return False

def safe_upload_with_streamlit_ui():
    """
    Wrapper para Streamlit: lee el session_state, intenta subir la Bóveda con if_generation_match,
    y si falla por conflicto de concurrencia, muestra un st.error masivo y detiene la ejecución (st.stop).
    Esto obliga al usuario a forzar la restauración desde GCS, impidiendo la sobreescritura accidental.
    """
    import streamlit as st
    expected = st.session_state.get('gcs_db_generation')
    try:
        return upload_db_to_gcs(expected_generation=expected)
    except Exception as e:
        if str(e) == "CONCURRENCY_CONFLICT":
            st.error("🚨 **ALERTA DE SEGURIDAD Y CONCURRENCIA** 🚨\n\n"
                     "Otra sesión (por ejemplo, Natalia u otra pestaña) modificó la Bóveda en la Nube "
                     "mientras tú tenías esta pantalla abierta.\n\n"
                     "Para **evitar la pérdida de los datos de tu compañero**, la Nube ha RECHAZADO tu "
                     "intento de guardado de forma automática.\n\n"
                     "👉 **QUÉ DEBES HACER**: Ve a la barra lateral izquierda y presiona el botón "
                     "`☁️ Forzar Restauración desde la Nube (GCS)` para descargar los datos más recientes "
                     "y luego vuelve a ingresar tu movimiento.")
            st.stop()
        else:
            raise e

def upload_backup_zip_to_gcs(zip_path, destination_blob_name=None):
    """
    Sube un archivo ZIP de respaldo hacia Google Cloud Storage.
    Retorna (True, gs_url) si fue exitoso, o (False, motivo) en caso de fallo.
    """
    if not os.path.exists(zip_path):
        return False, "Archivo ZIP local no encontrado."
    
    try:
        client = get_gcs_client()
        if not client:
            return False, "Sin credenciales o cliente GCS no disponible."
            
        if destination_blob_name is None:
            filename = os.path.basename(zip_path)
            destination_blob_name = f"backups/{filename}"
            
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        
        blob.upload_from_filename(zip_path)
        gs_url = f"gs://{BUCKET_NAME}/{destination_blob_name}"
        logger.info(f"Backup subido a la nube exitosamente: {gs_url}")
        
        return True, gs_url
    except Exception as e:
        logger.warning(f"Error subiendo el backup ZIP a GCS: {e}")
        return False, str(e)
