import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuración Base de Datos Única y Canónica (data/crm_database.db)
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/crm_database.db")

parent_dir = os.path.dirname(DATABASE_PATH)
if parent_dir and not os.path.exists(parent_dir):
    os.makedirs(parent_dir, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
