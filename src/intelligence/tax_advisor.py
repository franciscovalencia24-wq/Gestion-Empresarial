import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate
from src.intelligence.rag_advisor import RAGAdvisorV2

class TaxAdvisorAgent:
    """
    Agente Tributario Autónomo (Fase C).
    Combina conocimiento RAG (PDFs) con Búsqueda Web en vivo (DuckDuckGo)
    limitada a sitios oficiales del gobierno de Chile.
    """
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        # 1. Herramienta de Búsqueda Web Restringida
        self.search_tool = DuckDuckGoSearchRun()
        
        # 2. Herramienta de RAG Interno
        _PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        _PERSIST_DIR  = os.path.join(_PROJECT_ROOT, "data", "vector_db_local")
        _KNOW_PATHS   = [
            os.path.join(_PROJECT_ROOT, "DOCUMENTACIÓN CMV"),
            os.path.join(_PROJECT_ROOT, "data", "knowledge", "camv_pdfs"),
        ]
        
        self.rag_engine = RAGAdvisorV2(data_paths=_KNOW_PATHS, persist_dir=_PERSIST_DIR)
        
        # Si la base RAG no existe, intentamos cargarla/indexarla
        if not self.rag_engine.vector_store:
            try:
                self.rag_engine.index_documents(force_reload=False)
            except:
                pass

        if self.api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-flash-latest", # Usamos flash porque los pro están limitados
                temperature=0.1,
                google_api_key=self.api_key
            )
            self.agent_executor = self._initialize_agent()
        else:
            self.llm = None
            self.agent_executor = None

    def _rag_search(self, query: str) -> str:
        """Herramienta para buscar en los documentos internos (PDFs de leyes)."""
        try:
            return self.rag_engine.ask(query)
        except Exception as e:
            return f"Error consultando el RAG: {e}"

    def _official_web_search(self, query: str) -> str:
        """Herramienta para buscar en la web, forzando dominios oficiales chilenos."""
        # Agregamos filtros de dominio a la consulta
        restricted_query = f"{query} site:sii.cl OR site:bcn.cl OR site:cmfchile.cl OR site:spensiones.cl"
        try:
            return self.search_tool.run(restricted_query)
        except Exception as e:
            return f"Error buscando en la web: {e}"

    def _initialize_agent(self):
        tools = [
            Tool(
                name="BaseDeConocimientoLegal",
                func=self._rag_search,
                description="Útil para buscar detalles profundos, textos completos y explicaciones de leyes chilenas, circulares CMF o impuestos que están en nuestra base de datos interna."
            ),
            Tool(
                name="BusquedaWebOficialChile",
                func=self._official_web_search,
                description="Útil para buscar en internet información actual, noticias recientes, valores de UF/UTM, y corroborar si una ley ha cambiado recientemente. Solo busca en sii.cl, bcn.cl, cmfchile.cl."
            )
        ]

        template = '''Eres el Asesor Tributario Senior de FV ASESORIAS E INVERSIONES impulsada por Altus AI.
Tu rol es responder dudas complejas sobre herencia, impuestos (LIR), seguros de vida y APV en Chile.
Reglas estrictas:
1. Si te preguntan algo técnico o conceptual, usa SIEMPRE la 'BaseDeConocimientoLegal' primero.
2. Si te preguntan sobre datos vigentes (ej. tramos de este año, topes imponibles, si una ley cambió), usa SIEMPRE la 'BusquedaWebOficialChile' para verificar.
3. EN TU RESPUESTA FINAL: Debes obligatoriamente indicar de qué fuente obtuviste la información. Si usaste la web, incluye el texto 'Fuente web oficial utilizada' y menciona el sitio. Si usaste la base de conocimiento, menciona 'Fuente: Normativa Indexada'.
4. NUNCA inventes artículos de ley que no hayas encontrado en tus herramientas.

TOOLS:
------
Puedes usar las siguientes herramientas para responder la pregunta:

{tools}

Para usar una herramienta, usa EXACTAMENTE el siguiente formato:
```
Thought: Do I need to use a tool? Yes
Action: el nombre de la herramienta a usar, debe ser una de [{tool_names}]
Action Input: la entrada para la herramienta
Observation: el resultado de la herramienta
```
Cuando tengas la respuesta final para el usuario, o si no necesitas usar una herramienta, usa EXACTAMENTE este formato:
```
Thought: Do I need to use a tool? No
Final Answer: la respuesta final a la pregunta original, en español, y con las fuentes citadas.
```

Comenzamos!

New input: {input}
{agent_scratchpad}'''

        prompt = PromptTemplate.from_template(template)
        agent = create_react_agent(self.llm, tools, prompt)
        
        return AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True, 
            handle_parsing_errors=True
        )

    def ask(self, question: str) -> str:
        if not self.agent_executor:
            return "Error: GOOGLE_API_KEY no configurada o agente no inicializado."
        
        try:
            response = self.agent_executor.invoke({"input": question})
            return response.get("output", "Sin respuesta.")
        except Exception as e:
            return f"Lo siento, ocurrió un error procesando tu consulta: {e}"
