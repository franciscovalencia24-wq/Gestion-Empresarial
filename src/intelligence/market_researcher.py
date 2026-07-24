import os
import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from src.database.connection import SessionLocal
import src.database.models as models

class MarketResearcherAgent:
    """
    Agente Investigador de Mercado.
    Vigila a la competencia (SURA, Banchile, Santander, BCI) y tecnologías emergentes,
    generando reportes estratégicos para marketing y ventas.
    """
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.search_tool = DuckDuckGoSearchRun()
        
        if self.api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-flash-latest", 
                temperature=0.4,
                google_api_key=self.api_key
            )
        else:
            self.llm = None

    def _search_web(self, query: str) -> str:
        try:
            return self.search_tool.run(query)
        except Exception as e:
            return f"Error en búsqueda: {e}"

    def generate_weekly_report(self) -> str:
        if not self.llm:
            return "Error: GOOGLE_API_KEY no configurada."

        print("[MarketResearcher] Realizando OSINT de competencia...")
        
        # Realizamos 3 búsquedas clave
        search_1 = self._search_web("noticias 'Banchile Inversiones' OR 'SURA' OR 'Santander Wealth' Chile")
        search_2 = self._search_web("nuevas tendencias Wealth Management Inteligencia Artificial 2026")
        search_3 = self._search_web("estrategias captacion clientes altos patrimonios family office")

        prompt = f"""
        Actúa como un Director de Inteligencia Competitiva para FV ASESORIAS E INVERSIONES impulsada por Altus AI.
        Has realizado vigilancia tecnológica y competitiva hoy ({datetime.date.today()}).
        
        RESULTADOS DE BÚSQUEDA WEB:
        - Competencia Local: {search_1[:1500]}
        - Tendencias IA/WealthTech: {search_2[:1500]}
        - Estrategias de Captación: {search_3[:1500]}

        OBJETIVO:
        Genera un 'Brief Semanal de Mercado' dirigido al equipo comercial para mejorar el programa,
        identificar debilidades de la competencia y captar nuevos clientes.

        ESTRUCTURA DEL REPORTE (Comunicación Estilo CEO & Neurociencia):
        Tu respuesta DEBE seguir estrictamente esta estructura de comunicación:
        1. **Pausa Reflexiva (Executive Summary):** Una introducción directa que resuma el estado actual de la competencia y el mercado esta semana.
        2. **Los 2 Puntos Críticos:** Identifica EXCLUSIVAMENTE las dos mayores amenazas o nichos abandonados por la competencia (SURA, Banchile, Santander, BCI) basándote en la búsqueda.
        3. **Conclusión y Táctica de Ataque:** Una directriz clara sobre cómo FV ASESORIAS E INVERSIONES debe evolucionar en marketing o capacidades para robarse esa cuota de mercado.
        4. **🎁 Bono de Valor (Inesperado):** (Error de Predicción Positivo). Entrega una idea de tecnología de IA o estrategia radical, poco convencional, que no estemos usando actualmente y que dejaría obsoleta a la competencia local.

        REGLAS DE COMUNICACIÓN:
        - Sé asertivo, usa un tono de CEO agresivo en ventas.
        - Formatea el texto en Markdown hermoso.
        """
        
        print("[MarketResearcher] Generando Reporte...")
        response = self.llm.invoke(prompt)
        
        import ast
        content = response.content
        if isinstance(content, str) and content.startswith("[{'type':"):
            try:
                parsed = ast.literal_eval(content)
                if isinstance(parsed, list) and len(parsed) > 0 and 'text' in parsed[0]:
                    content = parsed[0]['text']
            except:
                pass
        elif isinstance(content, list):
            content = content[0].get('text', '') if isinstance(content[0], dict) else str(content)
            
        return str(content)

    def run_deep_osint(self):
        """
        Ejecuta una vigilancia profunda (Deep OSINT) sobre los competidores registrados en la DB,
        y actualiza la tabla competitor_profiles con datos estructurados.
        """
        if not self.llm:
            return "Error: GOOGLE_API_KEY no configurada."

        import json

        db = SessionLocal()
        
        # 1. Verificar si hay competidores, si no, crear los básicos
        if db.query(models.CompetitorProfile).count() == 0:
            basicos = [
                models.CompetitorProfile(nombre="Banchile Inversiones", tipo="Banco"),
                models.CompetitorProfile(nombre="SURA", tipo="Administradora"),
                models.CompetitorProfile(nombre="Santander", tipo="Banco"),
                models.CompetitorProfile(nombre="BCI", tipo="Banco"),
            ]
            db.add_all(basicos)
            db.commit()
            
        competidores = db.query(models.CompetitorProfile).all()

        print(f"[MarketResearcher] Iniciando Deep OSINT para {len(competidores)} competidores...")

        for comp in competidores:
            print(f"  -> Investigando a: {comp.nombre}")
            
            # Búsqueda web específica (Deep OSINT v2 - 3 vectores de ataque)
            q_estrategia = self._search_web(f"'{comp.nombre}' Chile estrategia wealth management altos patrimonios 2026")
            q_reclamos = self._search_web(f"'{comp.nombre}' Chile reclamos problemas debilidades inversiones")
            q_productos = self._search_web(f"'{comp.nombre}' Chile nuevos productos inversion comisiones rentabilidad")
            
            prompt = f"""
            Eres un analista de inteligencia competitiva de élite. Analiza esta información sobre nuestro competidor '{comp.nombre}':
            
            VECTOR 1 (ESTRATEGIA): {q_estrategia[:1500]}
            VECTOR 2 (DEBILIDADES/RECLAMOS): {q_reclamos[:1500]}
            VECTOR 3 (PRODUCTOS/COMISIONES): {q_productos[:1500]}
            
            Tu objetivo es extraer datos altamente precisos para nuestra 'Matriz de Guerra'.
            Debes responder ÚNICAMENTE con un objeto JSON válido, sin usar bloques de código Markdown (```json ... ```), sin ningún otro texto. Usa este formato exacto:
            {{
                "pros": "Puntos fuertes de {comp.nombre}",
                "contras": "Debilidades operativas, de servicio o reclamos frecuentes",
                "estrategias": "Hacia dónde están apuntando actualmente (IA, nuevos productos, etc.)",
                "publico_objetivo": "Qué tipo de cliente alto patrimonio buscan",
                "nichos_abandonados": "Qué tipo de clientes o servicios están ignorando (nuestra oportunidad de ataque)"
            }}
            """
            
            try:
                # Usamos temperatura 0 para respuestas más deterministas
                self.llm.temperature = 0.0
                resp = self.llm.invoke(prompt)
                
                # Limpiar texto (por si acaso el LLM insiste en poner ```json)
                texto_json = resp.content
                if isinstance(texto_json, list):
                    texto_json = texto_json[0].get('text', '') if isinstance(texto_json[0], dict) else str(texto_json)
                
                texto_json = str(texto_json).strip()
                if texto_json.startswith("```json"):
                    texto_json = texto_json[7:]
                if texto_json.endswith("```"):
                    texto_json = texto_json[:-3]
                    
                data = json.loads(texto_json.strip())
                
                # Actualizar DB
                comp.pros = data.get("pros", "")
                comp.contras = data.get("contras", "")
                comp.estrategias = data.get("estrategias", "")
                comp.publico_objetivo = data.get("publico_objetivo", "")
                comp.nichos_abandonados = data.get("nichos_abandonados", "")
                comp.updated_at = datetime.datetime.utcnow()
                
                db.commit()
                print(f"     [OK] {comp.nombre} actualizado en la BD.")
            except Exception as e:
                print(f"     [ERROR] analizando {comp.nombre}: {e}")
                
            self.llm.temperature = 0.4 # Restaurar
            
        db.close()
        return "Deep OSINT completado. Base de datos de competidores actualizada."

    def ingest_competitor_from_url(self, url: str) -> str:
        import requests
        import json
        import datetime
        from bs4 import BeautifulSoup

        try:
            # 1. Scrapear la URL
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            # Extraer solo el texto, limpiando scripts y estilos
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text(separator=' ', strip=True)
            
            # Acotar el texto
            text = text[:10000]
            
            # 2. IA analiza el texto
            prompt = f"""
            Eres un analista de inteligencia. Lee la siguiente información extraída de la página web de un competidor:
            URL: {url}
            CONTENIDO: {text}
            
            Extrae su perfil para nuestra matriz de guerra.
            Responde ÚNICAMENTE con un JSON válido sin Markdown, con esta estructura:
            {{
                "nombre": "Nombre oficial de la empresa",
                "tipo": "Megabanco | Boutique/MFO | WealthTech | Corredora",
                "pros": "Fortalezas que venden en su web",
                "contras": "Debilidades o puntos ciegos (ej. mucha fricción, conflictos de interés, falta de foco)",
                "estrategias": "Estrategia que comunican",
                "publico_objetivo": "A qué tipo de cliente apuntan",
                "nichos_abandonados": "Oportunidades de ataque para FV ASESORIAS E INVERSIONES (somos boutique Family Office enfocada en arquitectura abierta)"
            }}
            """
            
            self.llm.temperature = 0.0
            resp = self.llm.invoke(prompt)
            texto_json = resp.content
            if isinstance(texto_json, list):
                texto_json = texto_json[0].get('text', '') if isinstance(texto_json[0], dict) else str(texto_json)
            
            texto_json = str(texto_json).strip()
            if texto_json.startswith("```json"):
                texto_json = texto_json[7:]
            if texto_json.endswith("```"):
                texto_json = texto_json[:-3]
                
            data = json.loads(texto_json.strip())
            
            # 3. Guardar en BD
            db = SessionLocal()
            nombre = data.get("nombre", "Competidor Desconocido")
            comp = db.query(models.CompetitorProfile).filter_by(nombre=nombre).first()
            if not comp:
                comp = models.CompetitorProfile(nombre=nombre, tipo=data.get("tipo", "Desconocido"))
                db.add(comp)
            else:
                comp.tipo = data.get("tipo", comp.tipo)
                
            comp.pros = data.get("pros", "")
            comp.contras = data.get("contras", "")
            comp.estrategias = data.get("estrategias", "")
            comp.publico_objetivo = data.get("publico_objetivo", "")
            comp.nichos_abandonados = data.get("nichos_abandonados", "")
            comp.updated_at = datetime.datetime.utcnow()
            
            db.commit()
            db.close()
            return f"✅ Competidor '{nombre}' ingestado correctamente desde {url}."
            
        except Exception as e:
            return f"❌ Error al ingestar {url}: {str(e)}"

