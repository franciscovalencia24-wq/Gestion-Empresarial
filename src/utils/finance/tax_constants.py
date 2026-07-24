from datetime import datetime

# Ley 21.133: Aumento gradual de la retención de boletas de honorarios
RETENCION_BOLETAS = {
    2020: 0.1075,
    2021: 0.1150,
    2022: 0.1225,
    2023: 0.1300,
    2024: 0.1375,
    2025: 0.1450,
    2026: 0.1525,
    2027: 0.1600,
    2028: 0.1700
}

def get_current_retention_rate(year=None) -> float:
    """
    Retorna la tasa de retención de boletas correspondiente al año.
    Si el año supera el límite establecido (2028), retorna el valor máximo (17%).
    """
    if not year:
        year = datetime.now().year
        
    if year > 2028:
        return 0.1700
    
    # Por si se solicita un año muy antiguo
    if year < 2020:
        return 0.1000
        
    return RETENCION_BOLETAS.get(year, 0.1525)

def get_current_retention_percentage_str(year=None) -> str:
    """
    Retorna el string formateado, ej: '15.25%'
    """
    rate = get_current_retention_rate(year)
    return f"{rate * 100:.2f}%"
