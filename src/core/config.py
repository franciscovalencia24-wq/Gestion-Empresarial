import os
from dotenv import load_dotenv

# Carga variables desde `.env`
load_dotenv()

# Configuración Base de Datos. Por defecto SQLite local.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/processed/prospectos.db")
