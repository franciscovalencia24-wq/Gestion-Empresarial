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
