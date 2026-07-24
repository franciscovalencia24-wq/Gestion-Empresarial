import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate
from src.intelligence.rag_advisor import RAGAdvisorV2

class OmniAdvisorAgent:
    """
    Asesor Patrimonial y Tributario Senior.
    Combina conocimiento RAG (PDFs) con Búsqueda Web en vivo y
    Memoria Persistente a Largo Plazo por Cliente usando JSON puro.
    """
    def __init__(self, client_id: str = "default_user"):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.client_id = client_id
        
        # 1. Configurar Memoria Persistente con JSON
        _PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.memory_dir = os.path.join(_PROJECT_ROOT, "data", "memory", "clients")
        os.makedirs(self.memory_dir, exist_ok=True)
        
        self.memory_file = os.path.join(self.memory_dir, f"{self.client_id}_memory.json")
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        # 2. Herramienta de Búsqueda Web Restringida
        self.search_tool = DuckDuckGoSearchRun()
        
        # 3. Herramienta de RAG Interno
        _PERSIST_DIR  = os.path.join(_PROJECT_ROOT, "data", "vector_db_local")
        _KNOW_PATHS   = [
            os.path.join(_PROJECT_ROOT, "DOCUMENTACIÓN CMV"),
            os.path.join(_PROJECT_ROOT, "data", "knowledge", "camv_pdfs"),
        ]
        
        self.rag_engine = RAGAdvisorV2(data_paths=_KNOW_PATHS, persist_dir=_PERSIST_DIR)
        
        if not self.rag_engine.vector_store:
            try:
                self.rag_engine.index_documents(force_reload=False)
            except:
                pass

        if self.api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-flash-latest",
                temperature=0.1,
                google_api_key=self.api_key
            )
            self.agent_executor = self._initialize_agent()
        else:
            self.llm = None
            self.agent_executor = None

    def _get_history(self) -> str:
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                hist = json.load(f)
            # Solo los últimos 6 mensajes para no saturar tokens
            hist = hist[-6:]
            text_hist = "\\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in hist])
            return text_hist if text_hist else "Sin historial previo."
        except:
            return "Sin historial previo."

    def _save_to_history(self, role: str, content: str):
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                hist = json.load(f)
            hist.append({"role": role, "content": content})
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(hist, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _rag_search(self, query: str) -> str:
        try:
            return self.rag_engine.ask(query)
        except Exception as e:
            return f"Error consultando el RAG: {e}"

    def _official_web_search(self, query: str) -> str:
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
                description="Útil para buscar normativas CMF, leyes chilenas, APV, herencias y reglamentos que están en nuestra base indexada."
            ),
            Tool(
                name="BusquedaWebOficialChile",
                func=self._official_web_search,
                description="Útil para buscar en internet información actual, topes imponibles, UF/UTM, y si una ley cambió recientemente."
            )
        ]

        template = '''Eres el Asesor Patrimonial y Tributario Senior de FV ASESORIAS E INVERSIONES impulsada por Altus AI.
Tu rol es aconsejar sobre estrategias fiscales, normativas y patrimonio en Chile, recordando el contexto del cliente.
Reglas estrictas de Contenido:
1. Usa siempre la 'BaseDeConocimientoLegal' para consultas técnicas o legales sobre Chile.
2. NUNCA inventes artículos de ley.
3. El historial de conversación (memoria) está disponible abajo. Úsalo para recordar quién es el cliente y de qué hablaron antes.

ESTRUCTURA DEL REPORTE (Comunicación Estilo CEO & Neurociencia):
Tu respuesta DEBE seguir estrictamente esta estructura de comunicación:
1. **Pausa Reflexiva:** Una introducción directa y ejecutiva que delimite el problema del usuario.
2. **Los 2 Puntos Críticos:** Identifica EXCLUSIVAMENTE los dos problemas o soluciones más relevantes. Explícalos de forma concisa.
3. **Conclusión y Plan de Acción:** Una directriz clara sobre los siguientes pasos.
4. **🎁 Bono de Valor (Inesperado):** (Error de Predicción de Recompensa Positivo). Entrega un dato, optimización, lección de psicología de ventas o de negociación (ej. Método Harvard) de altísimo valor que el cliente no haya preguntado explícitamente, pero que se relacione con su caso. Tienes acceso a transcripciones de Youtube sobre esto en tu Base de Conocimiento, úsalas.

HISTORIAL DEL CHAT (Memoria a Largo Plazo):
{chat_history}

TOOLS:
------
Puedes usar las siguientes herramientas:

{tools}

Formato estricto a seguir:
```
Thought: Do I need to use a tool? Yes
Action: el nombre de la herramienta a usar, debe ser una de [{tool_names}]
Action Input: la entrada para la herramienta
Observation: el resultado de la herramienta
```
Cuando tengas la respuesta final para el usuario:
```
Thought: Do I need to use a tool? No
Final Answer: [Tu respuesta detallada y estratégica, citando fuentes si aplica]
```

Comenzamos!

New input: {input}
{agent_scratchpad}'''

        prompt = PromptTemplate.from_template(template)
        return create_react_agent(self.llm, tools, prompt)

    def ask(self, question: str) -> str:
        if not self.agent_executor:
            return "Error: GOOGLE_API_KEY no configurada o agente no inicializado."
        
        # Guardar input
        self._save_to_history("user", question)
        
        try:
            # Obtener historia
            history = self._get_history()
            
            # El agent de langchain_classic necesita ser ejecutado con AgentExecutor
            # pero necesitamos inyectar chat_history. Lo más simple es pasar todo como input al AgentExecutor
            
            from langchain_classic.agents import AgentExecutor
            executor = AgentExecutor(
                agent=self.agent_executor, 
                tools=[
                    Tool(name="BaseDeConocimientoLegal", func=self._rag_search, description="Buscar leyes"),
                    Tool(name="BusquedaWebOficialChile", func=self._official_web_search, description="Buscar en web")
                ], 
                verbose=True, 
                handle_parsing_errors=True
            )
            
            response = executor.invoke({
                "input": question,
                "chat_history": history
            })
            
            final_output = response.get("output", "Sin respuesta.")
            self._save_to_history("assistant", final_output)
            return final_output
            
        except Exception as e:
            return f"Lo siento, ocurrió un error procesando tu consulta: {e}"
