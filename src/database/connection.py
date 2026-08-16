import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.core.config import DATABASE_URL

# Si es SQLite, nos aseguramos de que los directorios donde vivirá existan
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if db_path:
        db_abs = os.path.abspath(db_path)
        parent_dir = os.path.dirname(db_abs)
        if parent_dir and parent_dir != db_abs:  # evita crear '' o el mismo path
            os.makedirs(parent_dir, exist_ok=True)
            
def force_recover_db(db_abs):
    import sqlite3
    import logging
    import subprocess
    logger = logging.getLogger("db_recovery")
    
    if os.path.exists(db_abs):
        corrupted = False
        try:
            conn = sqlite3.connect(db_abs)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            res = cursor.fetchone()
            if res and res[0] != "ok":
                corrupted = True
            conn.close()
        except sqlite3.DatabaseError as e:
            corrupted = True
            logger.error(f"DatabaseError detectado: {e}")
        
        if corrupted:
            logger.warning(f"¡Base de datos corrupta ({db_abs})! Iniciando rescate de datos...")
            backup_path = db_abs + ".corrupted_bak"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(db_abs, backup_path)
            
            try:
                # Intento 1: CLI sqlite3 (El más robusto)
                dump_process = subprocess.Popen(["sqlite3", backup_path, ".dump"], stdout=subprocess.PIPE)
                subprocess.run(["sqlite3", db_abs], stdin=dump_process.stdout)
                dump_process.wait()
                logger.info("Rescate por CLI completado.")
            except Exception as ex:
                logger.error(f"Fallo CLI sqlite3: {ex}. Intentando iterdump en Python...")
                try:
                    # Intento 2: Python iterdump
                    conn_bad = sqlite3.connect(backup_path)
                    sql_path = db_abs + ".sql"
                    with open(sql_path, "w", encoding="utf-8") as f:
                        for line in conn_bad.iterdump():
                            f.write(f'{line}\n')
                    conn_bad.close()
                    
                    conn_good = sqlite3.connect(db_abs)
                    with open(sql_path, "r", encoding="utf-8") as f:
                        conn_good.executescript(f.read())
                    conn_good.close()
                    os.remove(sql_path)
                    logger.info("Rescate por Python iterdump completado.")
                except Exception as e2:
                    logger.error(f"Fallo total en recuperación: {e2}")

if db_path:
    db_abs = os.path.abspath(db_path)
    force_recover_db(db_abs)

engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={"timeout": 30} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Generador para obtener la sesión de BD de forma segura."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
