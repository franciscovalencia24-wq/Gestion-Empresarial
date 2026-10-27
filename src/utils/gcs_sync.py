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
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, module="google.auth._default")
            return storage.Client(project=PROJECT_ID)
    except Exception as e:
        logger.warning(f"No se pudo inicializar cliente de GCS: {e}")
        return None

def get_gcs_cloud_status(db_filename="crm_database.db"):
    """
    Obtiene metadatos en vivo del archivo en Google Cloud Storage:
    - exists (bool)
    - generation (int)
    - updated_utc (datetime)
    - updated_chile_str (str con fecha y hora de Chile)
    - size_mb (float)
    """
    try:
        client = get_gcs_client()
        if not client:
            return {"exists": False, "error": "No hay conexión o credenciales a Google Cloud"}
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(db_filename)
        if not blob.exists():
            return {"exists": False, "error": "El archivo no existe en el bucket GCS"}
        blob.reload()

        from datetime import timezone, timedelta
        tz_chile = timezone(timedelta(hours=-3))
        dt_chile = blob.updated.astimezone(tz_chile)
        dt_str = dt_chile.strftime("%d/%m/%Y %H:%M:%S")

        return {
            "exists": True,
            "generation": blob.generation,
            "updated_utc": blob.updated,
            "updated_chile_str": dt_str,
            "size_mb": round(blob.size / (1024 * 1024), 2),
            "size_bytes": blob.size
        }
    except Exception as e:
        logger.warning(f"Error obteniendo estado de GCS: {e}")
        return {"exists": False, "error": str(e)}

def download_db_from_gcs(db_filename="crm_database.db", destination_path="data/crm_database.db", timeout=30):
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
        if blob.exists(timeout=min(10, timeout)):
            blob.reload(timeout=min(10, timeout))
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
            
            # 2. Descargar a un archivo temporal primero con timeout controlado
            blob.download_to_filename(temp_path, timeout=timeout)
            
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

            # 4. Reemplazo Atómico usando SQLite Backup (Thread-safe)
            try:
                conn_src = sqlite3.connect(temp_path)
                conn_dst = sqlite3.connect(destination_path)
                conn_src.backup(conn_dst)
                conn_dst.close()
                conn_src.close()
                os.remove(temp_path)
                logger.info(f"Restauración atómica (backup API) exitosa: {destination_path}")
            except sqlite3.DatabaseError as db_err:
                # Si el destino estaba corrupto ("file is not a database"), el backup falla.
                try:
                    conn_dst.close()
                except:
                    pass
                try:
                    conn_src.close()
                except:
                    pass
                shutil.move(temp_path, destination_path)
                logger.warning(f"Restauración por OS move (destino estaba corrupto): {db_err}")
                
            # 5. Si la descarga presentaba corrupción, invocar rescate de emergencia
            if res and res[0] != "ok":
                try:
                    from src.database.connection import force_recover_db
                    force_recover_db(os.path.abspath(destination_path))
                except Exception as rec_err:
                    logger.error(f"Error invocando la rutina de rescate forzado: {rec_err}")
                
            logger.info(f"DB descargada desde GCS: gs://{BUCKET_NAME}/{db_filename} -> {destination_path}")
            
            # Guardamos la generación localmente en disco y en session_state
            gen_file = os.path.join(os.path.dirname(destination_path), ".gcs_local_generation")
            try:
                with open(gen_file, "w") as gf:
                    gf.write(str(blob.generation))
            except Exception as ge:
                logger.warning(f"No se pudo guardar archivo de generacion local: {ge}")

            try:
                import streamlit as st
                st.session_state.gcs_db_generation = blob.generation
                from datetime import timezone, timedelta
                tz_chile = timezone(timedelta(hours=-3))
                dt_chile = blob.updated.astimezone(tz_chile)
                st.session_state.gcs_last_sync_time = dt_chile.strftime("%d/%m/%Y %H:%M:%S")
                st.cache_data.clear()
                st.cache_resource.clear()
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

def ensure_latest_database_from_gcs(db_filename="crm_database.db", destination_path="data/crm_database.db"):
    """
    Verifica automáticamente si la versión en la nube (GCS) es más reciente
    que la versión local en disco. Si no existe la base local o hay una versión
    más nueva en GCS (distinta generación), descarga inmediatamente la base de datos
    para que el usuario SIEMPRE vea los datos 100% correctos y actualizados al abrir la página.
    """
    try:
        if not os.path.exists(destination_path):
            logger.info("Base de datos local no existe. Descargando desde GCS...")
            return download_db_from_gcs(db_filename=db_filename, destination_path=destination_path)

        status = get_gcs_cloud_status(db_filename=db_filename)
        if not status.get("exists"):
            logger.warning("Bóveda no accesible en GCS. Se mantiene copia local.")
            return False

        cloud_gen = str(status.get("generation"))
        gen_file = os.path.join(os.path.dirname(destination_path), ".gcs_local_generation")
        local_gen = None
        if os.path.exists(gen_file):
            try:
                with open(gen_file, "r") as gf:
                    local_gen = gf.read().strip()
            except Exception:
                local_gen = None

        if local_gen != cloud_gen:
            logger.info(f"Sincronizando: Nube tiene gen {cloud_gen} vs local {local_gen}. Descargando última versión...")
            return download_db_from_gcs(db_filename=db_filename, destination_path=destination_path)

        return True
    except Exception as e:
        logger.warning(f"Error en ensure_latest_database_from_gcs: {e}")
        return False

def upload_db_to_gcs(source_path="data/crm_database.db", db_filename="crm_database.db", expected_generation=None, force=False):
    """
    Sube la base de datos local a Google Cloud Storage (GCS)
    después de un guardado o actualización de clientes/movimientos,
    usando sqlite3.backup() para asegurar consistencia en caliente.
    
    Si force=True, sobreescribe incondicionalmente sin fallar por PreconditionFailed.
    Si force=False y se proporciona expected_generation, fallará si hubo conflicto.
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
            if not force and expected_generation is not None:
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
        
        # Actualizamos la versión local segura en session_state y en disco
        try:
            blob.reload()
            gen_file = os.path.join(os.path.dirname(source_path), ".gcs_local_generation")
            with open(gen_file, "w") as gf:
                gf.write(str(blob.generation))
        except Exception:
            pass

        try:
            import streamlit as st
            st.session_state.gcs_db_generation = blob.generation
            from datetime import timezone, timedelta
            tz_chile = timezone(timedelta(hours=-3))
            dt_chile = blob.updated.astimezone(tz_chile)
            st.session_state.gcs_last_sync_time = dt_chile.strftime("%d/%m/%Y %H:%M:%S")
        except:
            pass
            
        return True
    except Exception as e:
        if str(e) == "CONCURRENCY_CONFLICT":
            raise e
        logger.warning(f"Error subiendo DB a GCS: {e}")
        return False

def safe_upload_with_streamlit_ui(force=False):
    """
    Wrapper para Streamlit: intenta subir la Bóveda a GCS.
    Si force=True, sobreescribe sin chequear generación (para el botón 'Forzar Guardado').
    Si falla por conflicto de concurrencia, muestra alerta clara.
    """
    import streamlit as st
    expected = None if force else st.session_state.get('gcs_db_generation')
    try:
        res = upload_db_to_gcs(expected_generation=expected, force=force)
        if not res:
            st.error("⚠️ No se pudo completar la sincronización con Google Cloud Storage. Verifique sus credenciales o conexión.")
        return res
    except Exception as e:
        if str(e) == "CONCURRENCY_CONFLICT":
            st.error("🚨 **ALERTA DE SEGURIDAD Y CONCURRENCIA** 🚨\n\n"
                     "Otra sesión (por ejemplo, Natalia u otra pestaña) modificó la Bóveda en la Nube "
                     "mientras tú tenías esta pantalla abierta.\n\n"
                     "Para **evitar la pérdida de los datos de tu compañero**, la Nube ha RECHAZADO tu "
                     "intento de guardado de forma automática.\n\n"
                     "👉 **QUÉ DEBES HACER**: Ve a la barra lateral izquierda y presiona el botón "
                     "`☁️ Forzar Restauración desde la Nube (GCS)` para descargar los datos más recientes "
                     "o presiona `💾 Forzar Guardado Seguro` si estás seguro de sobreescribir.")
            st.stop()
        else:
            st.error(f"⚠️ Error sincronizando con Google Cloud: {e}")
            return False

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
