import sys
import os

# Configuración de rutas
sys.path.append(os.getcwd())

from src.osint.scraper_do import run_scraper

def debug_osint():
    print("--- INICIANDO DIAGNÓSTICO PROFUNDO OSINT V6 (SYNC) ---")
    print(f"Directorio actual: {os.getcwd()}")
    
    try:
        # Probamos el barrido nacional (Todo Chile)
        stats = run_scraper(region_target=None)
        print(f"ESTADÍSTICAS FINALES: {stats}")
        
    except Exception as e:
        import traceback
        print(f"ERROR DURANTE LA EJECUCIÓN: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_osint()
