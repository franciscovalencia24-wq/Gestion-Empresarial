import re
import pandas as pd

def clean_rut_chileno(rut: str) -> str:
    """Limpia el RUT chileno, quitando puntos, y dejando el DV con guión: 11222333-4"""
    if pd.isna(rut):
        return None
    
    rut_str = str(rut).strip().upper()
    rut_str = re.sub(r'[^0-9K]', '', rut_str)
    
    if len(rut_str) < 2:
        return None
        
    cuerpo = rut_str[:-1]
    dv = rut_str[-1]
    
    return f"{cuerpo}-{dv}"

def clean_phone_number(phone) -> str:
    """Estandariza teléfono para WAPI: extrae un número móvil chileno +569XXXXXXXX válido."""
    if pd.isna(phone):
        return None
        
    phone_str = str(phone).strip()
    phone_str = re.sub(r'[^\d]', '', phone_str)  # solo deja números
    
    if len(phone_str) >= 9:
        ultimo_9 = phone_str[-9:]
        if ultimo_9.startswith('9'):
            return f"+56{ultimo_9}"
            
    return None  # No pudo parsearse como móvil chileno válido


def clean_amount(amount) -> float:
    """Limpiador de montos que maneja formatos 'string' ej. $5.000.000 a flotantes"""
    if pd.isna(amount):
        return None
        
    if isinstance(amount, (int, float)):
        return float(amount)
        
    amount_str = str(amount).replace('$', '').strip()
    
    # Manejar formatos como 5.000.000 
    if '.' in amount_str and ',' not in amount_str:
        amount_str = amount_str.replace('.', '')
    # Manejar si hay coma como decimal 5.000,50
    elif '.' in amount_str and ',' in amount_str:
        amount_str = amount_str.replace('.', '').replace(',', '.')
    # Si solo hay coma 5000,50
    elif ',' in amount_str and '.' not in amount_str:
        amount_str = amount_str.replace(',', '.')
        
    amount_str = re.sub(r'[^\d.]', '', amount_str)
    try:
        return float(amount_str) if amount_str else None
    except ValueError:
        return None
