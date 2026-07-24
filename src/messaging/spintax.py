import re
import random

def spin(text: str) -> str:
    """
    Evalúa una cadena Spintax y retorna una permutación aleatoria.
    Respeta anidación de llaves si las hay.
    Ejemplo: "{Hola|Buenos días|Qué tal} amigo."
    """
    if not text:
        return ""
        
    def replace_match(match):
        options = match.group(1).split('|')
        return random.choice(options)
        
    pattern = re.compile(r'\{([^{}]*)\}')
    result = text
    
    # Evaluar anidados si existieran
    while pattern.search(result):
        result = pattern.sub(replace_match, result)
        
    return result

def format_message(template: str, prospect: dict) -> str:
    """
    1. Interpreta el Spintax.
    2. Reemplaza las keywords como [NOMBRE], [TELEFONO], [MONTO], etc.
    """
    spun_text = spin(template)
    
    # Manejar variables con control de errores si vienen vacías
    nombre_limpio = prospect.get("nombre", "")
    if nombre_limpio:
        nombre_limpio = str(nombre_limpio).split()[0]  # Tomar solo el primer nombre
    spun_text = spun_text.replace("[NOMBRE]", nombre_limpio if nombre_limpio else "colega")
        
    def is_valid_num(val):
        try:
            # check for None, NaN (val != val), or 0
            return val is not None and val == val and float(val) != 0
        except:
            return False

    monto_susc = prospect.get("monto_suscrito")
    saldo_adm = prospect.get("saldo_administrado")
    
    if is_valid_num(monto_susc):
        monto_str = f"${int(float(monto_susc)):,}".replace(',', '.')
        spun_text = spun_text.replace("[MONTO]", monto_str)
    elif is_valid_num(saldo_adm):
        monto_str = f"${int(float(saldo_adm)):,}".replace(',', '.')
        spun_text = spun_text.replace("[MONTO]", monto_str)
    else:
        spun_text = spun_text.replace("[MONTO]", "su inversión")
        
    ciudad = prospect.get("ciudad")
    spun_text = spun_text.replace("[CIUDAD]", str(ciudad) if ciudad else "su ciudad")
    
    tel = prospect.get("telefono")
    spun_text = spun_text.replace("[TELEFONO]", str(tel) if tel else "")
    
    return spun_text
