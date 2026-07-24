from sqlalchemy.orm import Session
from src.database.models import Prospect

def get_prospects_missing_info(db: Session, limit: int = 50):
    """
    Obtiene los prospectos que tienen RUT y Monto,
    pero les falta el Nombre o Teléfono para ser contactables en Fase 3.
    """
    prospects = db.query(Prospect).filter(
        (Prospect.nombre == None) | (Prospect.telefono == None) | 
        (Prospect.nombre == "") | (Prospect.telefono == "")
    ).limit(limit).all()
    
    return prospects
