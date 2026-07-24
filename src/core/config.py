import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuración Base de Datos. Por defecto SQLite local (crm_database.db o prospectos.db).
DATABASE_PATH = "data/crm_database.db"
if not os.path.exists("data"):
    os.makedirs("data", exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
