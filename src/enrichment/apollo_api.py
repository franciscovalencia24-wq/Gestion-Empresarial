import requests
import json

class ApolloProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }

    def search_people_by_company(self, company_name: str):
        """Busca tomadores de decisión (C-Level, Directores) dado un nombre de empresa"""
        url = f"{self.base_url}/people/search"
        
        # Filtramos para buscar gerentes, dueños, fundadores de la empresa
        payload = {
            "q_organization_name": company_name,
            "person_titles": ["CEO", "Director", "Gerente", "Fundador", "Owner", "Socio", "CTO", "CIO"],
            "page": 1,
            "per_page": 5
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=15)
            print("HTTP Status:", response.status_code)
            try:
                print("Apollo Data:", response.json())
            except:
                print("Apollo Data:", response.text)
            if response.status_code == 200:
                return response.json().get('people', [])
            return []
        except Exception as e:
            print(f"Error Apollo: {e}")
            return []

    def search_prospects(self, job_titles: list = None, industries: list = None, locations: list = ["Chile"], per_page: int = 10):
        """
        Búsqueda avanzada de prospectos por cargos, industrias y países.
        Ideal para generar listas 'Lookalike' masivas.
        """
        url = f"{self.base_url}/people/search"
        
        payload = {
            "person_titles": job_titles or ["CEO", "Director", "Gerente", "Owner", "Socio"],
            "q_organization_keyword_tags": industries,
            "person_locations": locations,
            "page": 1,
            "per_page": per_page
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=20)
            if response.status_code == 200:
                data = response.json()
                return data.get('people', []), data.get('pagination', {})
            return [], {}
        except Exception as e:
            print(f"Error en Búsqueda Prospectos: {e}")
            return [], {}

    def get_company_details(self, company_id: str):
        """Obtiene detalles profundos de una empresa para extraer etiquetas de industria"""
        url = f"{self.base_url}/organizations/{company_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json().get('organization', {})
            return {}
        except Exception:
            return {}
