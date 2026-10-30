"""
Utilidades estándar de validación, cálculo de dígito verificador y formateo de RUT chileno.
Soporta personas naturales y empresas (personas jurídicas).
"""
import re
import pandas as pd

def calcular_dv(cuerpo) -> str:
    """
    Calcula el dígito verificador oficial de un cuerpo de RUT mediante el algoritmo Módulo 11.
    Retorna el dígito como string ('0'-'9' o 'K'), o None si el cuerpo no es válido.
    """
    cuerpo_clean = re.sub(r'[^\d]', '', str(cuerpo))
    if not cuerpo_clean or len(cuerpo_clean) < 6:
        return None
    
    suma = 0
    multiplo = 2
    for c in reversed(cuerpo_clean):
        suma += int(c) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1
        
    res = 11 - (suma % 11)
    if res == 11:
        return "0"
    elif res == 10:
        return "K"
    else:
        return str(res)

def validar_rut(rut_str: str) -> bool:
    """Valida si un RUT chileno cumple con el algoritmo Módulo 11."""
    if not rut_str or pd.isna(rut_str):
        return False
    s = str(rut_str).strip().upper()
    if s.startswith("SINRUT") or s.startswith("INFOP") or s.startswith("DO"):
        return True
    s_clean = s.replace(".", "").replace(" ", "")
    if '-' not in s_clean:
        return False
    cuerpo, dv = s_clean.split('-', 1)
    dv_calc = calcular_dv(cuerpo)
    return dv_calc is not None and dv == dv_calc

def format_rut_miles(rut_str: str) -> str:
    """
    Formatea un RUT para visualización amigable con separadores de miles y guion.
    Ejemplo: '79904570-2' -> '79.904.570-2', '7888298-0' -> '7.888.298-0'.
    Mantiene intactos identificadores internos como 'SINRUT-...'.
    """
    if not rut_str or pd.isna(rut_str):
        return ""
    s = str(rut_str).strip().upper()
    if s.startswith("SINRUT") or s.startswith("INFOP") or s.startswith("DO"):
        return s
    
    s_clean = s.replace(".", "").replace(" ", "")
    if '-' in s_clean:
        cuerpo, dv = s_clean.split('-', 1)
    else:
        if len(s_clean) < 2:
            return s
        cuerpo, dv = s_clean[:-1], s_clean[-1:]
        
    cuerpo_digits = re.sub(r'[^\d]', '', cuerpo)
    if not cuerpo_digits:
        return s
        
    try:
        cuerpo_num = int(cuerpo_digits)
        cuerpo_formateado = f"{cuerpo_num:,}".replace(",", ".")
        return f"{cuerpo_formateado}-{dv}"
    except (ValueError, TypeError):
        return s

def clean_rut(rut_str: str) -> str:
    """Limpia un RUT quitando puntos para almacenamiento canónico: '79.904.570-2' -> '79904570-2'."""
    if not rut_str or pd.isna(rut_str):
        return ""
    s = str(rut_str).strip().upper()
    if s.startswith("SINRUT") or s.startswith("INFOP") or s.startswith("DO"):
        return s
    return s.replace(".", "").replace(" ", "")
