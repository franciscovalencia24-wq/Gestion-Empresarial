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

# ---------------------------------------------------------
# LICENCIAMIENTO CORPORATIVO B2B (ALTUS CORE SaaS)
# ---------------------------------------------------------
B2B_LICENSE_TIERS = {
    "TIER_1": {
        "max_users": 50,
        "price_per_user_uf": 2.5,
        "description": "Hasta 50 ejecutivos C-Level / Alta Gerencia."
    },
    "TIER_2": {
        "max_users": 200,
        "price_per_user_uf": 2.0,
        "description": "Hasta 200 ejecutivos / Subgerencias."
    },
    "ENTERPRISE": {
        "max_users": float('inf'),
        "price_per_user_uf": 1.5,
        "description": "Volumen corporativo, más de 200 usuarios activos."
    }
}

B2B_MODULES_ENABLED = {
    "tax_optimization": os.getenv("ALTUS_B2B_TAX_OPT", "True") == "True",       # Motor Tributario (DPE, Reliquidación)
    "debt_cmf_audit": os.getenv("ALTUS_B2B_DEBT_CMF", "True") == "True",         # Auditoría Deudas CMF
    "insurance_audit": os.getenv("ALTUS_B2B_INSURANCE", "True") == "True",       # Auditoría Pólizas (Cautivas/Liquidez)
    "montecarlo_projections": os.getenv("ALTUS_B2B_MONTECARLO", "False") == "True" # Proyecciones Estocásticas (Premium)
}
