import requests
import csv
import os
import random
from typing import List, Dict

def fetch_socich_data(termino: str = "ciru", tipo: str = "especialidad") -> List[Dict]:
    """
    Extrae la base de datos de cirujanos desde la API oculta de socich.cl
    """
    print(f"[*] Iniciando extracción en socich.cl (Búsqueda: {tipo} = '{termino}')...")
    
    # Generamos un parámetro 'v' aleatorio como lo hace el frontend para evitar caché
    rand_v = random.randint(1000, 9999)
    url = f"https://www.directoriocirujanos.desarrollomedico.com/excel-cirujanos/api/search.php?v={rand_v}&termino={termino}&tipo={tipo}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://socich.cl/"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"[!] Error de conexión. Código: {response.status_code}")
        return []
        
    try:
        data = response.json()
        total = data.get('total', 0)
        results = data.get('data', [])
        print(f"[+] API respondió exitosamente: Se encontraron {total} registros.")
        return results
    except Exception as e:
        print(f"[!] Error parseando el JSON de respuesta: {e}")
        return []

def save_to_csv(data: List[Dict], filename: str = "socios_socich.csv"):
    """
    Guarda los resultados en un archivo CSV estructurado.
    """
    if not data:
        print("[!] No hay datos para guardar.")
        return
        
    print(f"[*] Guardando datos en {filename}...")
    
    # Definir el orden de las columnas que queremos en el CSV
    fieldnames = ['Apellido', 'Nombre', 'Especialidad', 'Región']
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        
        for socio in data:
            # Reestructuramos el objeto JSON original a nuestras columnas
            # El JSON original trae: 'nombre', 'apellido', 'apellidom', 'especialidad', 'region'
            apellido_paterno = socio.get('apellido', '').strip()
            apellido_materno = socio.get('apellidom', '').strip()
            
            apellido_completo = f"{apellido_paterno} {apellido_materno}".strip()
            
            row = {
                'Apellido': apellido_completo,
                'Nombre': socio.get('nombre', '').strip(),
                'Especialidad': socio.get('especialidad', '').strip(),
                'Región': socio.get('region', '').strip()
            }
            writer.writerow(row)
            
    print(f"[+] Archivo {filename} generado exitosamente.")

if __name__ == "__main__":
    # Usamos "ciru" en "especialidad" ya que sabemos que arroja 1537 cirujanos (prácticamente todos)
    socios = fetch_socich_data(termino="ciru", tipo="especialidad")
    
    if socios:
        output_file = "socios_socich.csv"
        save_to_csv(socios, output_file)
        
        # Opcional: mostrar una muestra
        print("\nMuestra de los primeros 3 registros:")
        for s in socios[:3]:
            print(f" - {s.get('nombre')} {s.get('apellido')} {s.get('apellidom')} | {s.get('especialidad')}")
