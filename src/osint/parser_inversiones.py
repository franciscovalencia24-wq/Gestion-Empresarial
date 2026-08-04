import google.generativeai as genai
import pandas as pd
import json
import logging
import os

def get_gemini_api_key():
    return os.getenv("GOOGLE_API_KEY")

def parse_investment_files(file_bytes_list, file_names):
    """
    Parsea cartolas de inversin (PDF) usando Gemini.
    Retorna un DataFrame con las columnas: 
    ['Institucin', 'Activo', 'Tipo', 'Monto', 'Moneda', 'Monto (CLP)']
    """
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("No hay API Key de Gemini configurada. Ve a Ajustes del Sistema para ingresarla.")

    genai.configure(api_key=api_key)
    
    # We will use gemini-2.5-flash as it is fast and has a free tier
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = """
    Eres un analista financiero experto. 
    A continuación te entregaré el texto o datos extraídos de cartolas de inversión, cuentas corrientes o estados de cuenta de AFP de Chile.
    Tu objetivo es extraer TODAS las posiciones financieras y activos.
    
    Para cada posición, extrae:
    1. institucion: El banco, AFP, o corredora (ej. 'Banco de Chile', 'AFP Habitat', 'Fintual').
    2. activo: Nombre del fondo o instrumento (ej. 'Fondo Mutuo A', 'Cuenta Corriente', 'Acciones Apple').
    3. tipo: Clasifícalo estrictamente en una de estas categorías: ["Cotización Obligatoria", "APV-A", "APV-B", "APV con Póliza", "Depósito Convenido (DC-R)", "Depósito Convenido (DC-L)", "Cuenta 2", "Fondo Mutuo", "Acciones", "Depósito a Plazo", "Otro"]
    4. monto: El monto total (saldo) en número (sin comas ni formato).
    5. moneda: La moneda del activo (ej. 'CLP', 'UF', 'USD').
    6. monto_clp: El monto convertido a CLP en número (si está en CLP, es el mismo que 'monto').

    Devuelve EXCLUSIVAMENTE un JSON con el formato:
    {
      "posiciones": [
        {
          "institucion": "...",
          "activo": "...",
          "tipo": "...",
          "monto": 1000000,
          "moneda": "CLP",
          "monto_clp": 1000000
        }
      ]
    }
    No agregues markdown de bloque de código, responde solo el JSON crudo.
    """

    all_positions = []

    for file_bytes, file_name in zip(file_bytes_list, file_names):
        try:
            # En un entorno real se subiria el PDF usando genai.upload_file 
            # Pero para soportar rapido textos o archivos binarios en memoria con la API,
            # podemos mandar el documetn si el SDK lo soporta asi:
            
            response = model.generate_content([
                {"mime_type": "application/pdf", "data": file_bytes},
                prompt
            ])
            
            clean_text = response.text.replace('`json', '').replace('`', '').strip()
            data = json.loads(clean_text)
            
            if "posiciones" in data:
                all_positions.extend(data["posiciones"])
                
        except Exception as e:
            logging.error(f"Error parseando archivo {file_name}: {e}")
            # Si falla un archivo en especifico, loggear pero continuar con el resto
            continue

    if not all_positions:
        return pd.DataFrame()

    df = pd.DataFrame(all_positions)
    # Renombrar columnas para la UI
    # En caso de que el modelo haya devuelto mayusculas, bajamos todo a minuscula
    df.columns = [str(c).lower() for c in df.columns]
    
    df = df.rename(columns={
        "institucion": "Institucion",
        "activo": "Activo",
        "tipo": "Tipo",
        "monto": "Monto",
        "moneda": "Moneda",
        "monto_clp": "Monto CLP"
    })
    
    return df

