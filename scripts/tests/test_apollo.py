import sys
import os
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from src.enrichment.apollo_api import ApolloProvider

def test_apollo():
    api_key = os.getenv("APOLLO_API_KEY")
    apollo = ApolloProvider(api_key)
    
    empresas = ["Cencosud", "WOLF CORREDORES DE SEGUROS SpA"]
    
    for empresa in empresas:
        print(f"Probando Apollo para: '{empresa}'")
        res = apollo.search_people_by_company(empresa)
        if res:
            top = res[0]
            print("EXITO - Datos encontrados:")
            print(" - Nombre:", top.get("name"))
            print(" - Cargo:", top.get("title"))
            print(" - Email:", top.get("email"))
            print(" - LinkedIn:", top.get("linkedin_url"))
        else:
            print(f"SIN EXITO - No se encontraron contactos C-level en Apollo para '{empresa}'.")
        print("-" * 40)

if __name__ == "__main__":
    test_apollo()
