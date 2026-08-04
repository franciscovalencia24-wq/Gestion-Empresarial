import sys
import os

# Asegurar que corre desde root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ingestion.importer import run_import_all
from src.enrichment.run_enrichment import run_enrichment_process

def menu():
    while True:
        print("\n=" * 50)
        print("SISTEMA DE GESTIÓN DE PROSPECTOS (Fase 1 y 2)")
        print("=" * 50)
        print("1. Ingestar y limpiar base de datos Excel (Fase 1)")
        print("2. Enriquecer datos faltantes (Dummy API - Fase 2)")
        print("3. Salir")
        print("=" * 50)
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            print("\n--- INICIO DE INGESTIÓN ---")
            run_import_all()
        elif opcion == "2":
            print("\n--- INICIO DE ENRIQUECIMIENTO ---")
            run_enrichment_process()
        elif opcion == "3":
            print("Saliendo...")
            sys.exit(0)
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu()
