import os
import base64
import filetype
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_experimental.tools import PythonREPLTool
from langgraph.prebuilt import create_react_agent
from src.osint.yahoo_finance_tool import YahooFinanceTool
from src.osint.bcc_tool import BancoCentralTool
from src.osint.tax_calculator_tool import CalculadoraTributariaChile
from src.osint.apv_calculator_tool import APVCalculatorTool
from pydantic import BaseModel, Field
from typing import Type
from langchain_core.tools import BaseTool

class DDGInput(BaseModel):
    query: str = Field(description="La consulta de búsqueda a realizar en internet (ej: 'Microsoft target price 2026' o 'Oracle noticias recientes')")

class StrictWebSearchTool(BaseTool):
    name: str = "busqueda_web"
    description: str = "Útil para buscar noticias recientes y el Precio Objetivo (Target Price) en internet."
    args_schema: Type[BaseModel] = DDGInput
    def _run(self, query: str) -> str:
        import time
        try:
            return DuckDuckGoSearchRun().run(query)
        except Exception as e:
            try:
                # Reintento tras breve pausa (bypass rate limit DDG)
                time.sleep(2)
                return DuckDuckGoSearchRun().run(query)
            except Exception as e2:
                return f"Error en búsqueda web: {e2}. El servicio está temporalmente caído. Por favor, realiza tus cálculos con tu conocimiento general hasta la fecha."

class PythonInput(BaseModel):
    query: str = Field(description="El código en Python a ejecutar. Debe usar print() para mostrar el resultado.")

class StrictPythonREPLTool(BaseTool):
    name: str = "calculadora_python"
    description: str = "Un REPL de Python. Útil para ejecutar código Python y hacer cálculos matemáticos."
    args_schema: Type[BaseModel] = PythonInput
    def _run(self, query: str) -> str:
        return PythonREPLTool().run(query)

class MultimodalQueryAnalyst:
    """
    Analista de Consultas Multimodal.
    Procesa dudas de clientes en múltiples formatos (texto, audio, imagen, pdf),
    extrae el contexto, investiga en la web (DuckDuckGo), y genera una respuesta 
    técnica, neutral y estrictamente referenciada.
    """
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.search_tool = DuckDuckGoSearchRun()
        
        if self.api_key:
            # Usamos gemini-pro-latest por su altísima fiabilidad con LangChain y agentes ReAct
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro-latest", 
                temperature=0.0, # Temperatura en 0 para cero alucinaciones y matemática estricta
                google_api_key=self.api_key,
                max_retries=2, # Damos un intento más en caso de desconexión
                timeout=300 # Aumentamos drásticamente el timeout a 5 minutos (evita error 504)
            )
            
            # Cliente nativo para la Fase 1 (Multimodal) ya que LangChain descarta PDFs
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.vision_model = genai.GenerativeModel('gemini-pro-latest')
        else:
            self.llm = None
            self.vision_model = None

    def _search_web(self, query: str) -> str:
        try:
            return self.search_tool.run(query)
        except Exception as e:
            return f"Error en búsqueda: {e}"

    def analyze_query(self, text_input: str = "", file_bytes_list: list = None, filenames: list = None, prospect_info: str = "") -> str:
        if not self.llm:
            return "Error: GOOGLE_API_KEY no configurada."

        print("[QueryAnalyst] Procesando consulta multimodal...")
        
        content_parts = []
        
        # 1. Preparar el Prompt base para la Fase 1 (Extracción)
        prompt_extraction = f"""
        Eres un analista financiero cuantitativo experto en lectura de cartolas de inversión (como Pershing o SURA).
        El usuario ha subido archivos (PDFs, imágenes, correos) y/o escrito texto.
        Texto adicional del usuario: "{text_input}"
        Ficha Clínica del Cliente: "{prospect_info}"
        
        OBJETIVO:
        Analiza DETALLADAMENTE las imágenes o el PDF adjunto. NO ignores los documentos visuales. Extrae EXCLUSIVAMENTE:
        1. ¿Cuál es la pregunta o inquietud principal del cliente?
        2. En la cartola adjunta (ej. sección "Tenencias en Cartera"), busca y extrae obligatoriamente para cada activo la siguiente información exacta que SÍ aparece en las columnas del PDF:
           - Ticker o Nombre del Instrumento (ej. MSFT, ORCL, EEMS).
           - "Fecha de Adquisición" (suele estar en la primera columna, ej: 01/13/22).
           - "Cantidad".
           - "Costo por Unidad" (Este es el precio de compra histórico).
           - "Precio de Mercado" actual.
        
        PROHIBICIÓN ESTRICTA: El PDF SÍ CONTIENE los costos y fechas de adquisición. Tómate tu tiempo para leer la tabla visualmente. NO le pidas al usuario que ingrese esta información manualmente. Extrae los números directamente de la cartola.
        
        INSTRUCCIÓN DE TONO Y ESTILO:
        DEBES redactar la respuesta final dirigiéndote directamente al CLIENTE (ej. "Estimado Gonzalo"), NO al asesor. Utiliza un tono de Banquero Privado: formal, elegante, empático y extremadamente profesional.
        """
        content_parts_native = [prompt_extraction]

        # 2. Adjuntar los archivos si existen
        if file_bytes_list and filenames:
            for file_bytes, filename in zip(file_bytes_list, filenames):
                # Adivinar MIME type
                kind = filetype.guess(file_bytes)
                if kind:
                    mime_type = kind.mime
                else:
                    if filename.lower().endswith(".pdf"):
                        mime_type = "application/pdf"
                    elif filename.lower().endswith((".txt", ".eml", ".csv")):
                        mime_type = "text/plain"
                    else:
                        mime_type = "application/octet-stream"

                if filename.lower().endswith((".xlsx", ".xls", ".csv")):
                    try:
                        import pandas as pd
                        import io
                        if filename.lower().endswith(".csv"):
                            df = pd.read_csv(io.BytesIO(file_bytes))
                        else:
                            df = pd.read_excel(io.BytesIO(file_bytes))
                        csv_string = df.to_csv(index=False)
                        content_parts_native.append(f"\n\nCONTENIDO DE LA TABLA ({filename}):\n{csv_string}")
                    except Exception as e:
                        pass
                elif mime_type.startswith("text/") or filename.lower().endswith(".eml"):
                    if filename.lower().endswith(".eml"):
                        try:
                            import email
                            from email import policy
                            msg = email.message_from_bytes(file_bytes, policy=policy.default)
                            body = ""
                            for part in msg.walk():
                                if part.get_content_type() in ['text/plain', 'text/html']:
                                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore') + "\n"
                            
                            text_content = body if body else "EML sin texto."
                            content_parts_native.append(f"\n\nCONTENIDO DEL CORREO ({filename}):\n{text_content}")
                        except:
                            pass
                    else:
                        try:
                            content_parts_native.append(f"\n\nTEXTO ({filename}):\n" + file_bytes.decode('utf-8', errors='ignore'))
                        except:
                            pass
                else:
                    # PDF, Imágenes, Audio nativo de Gemini
                    content_parts_native.append({
                        "mime_type": mime_type,
                        "data": file_bytes
                    })

        # 3. Fase 1: Entender qué investigar (Usando SDK Nativo)
        print("[QueryAnalyst] Fase 1: Extracción de contexto (Nativa)...")
        try:
            extraction_response = self.vision_model.generate_content(content_parts_native)
            extracted_context = extraction_response.text
        except Exception as e:
            # Fallback en caso de error multimodal
            extracted_context = f"Error al leer multimodal nativo: {e}. Asumiendo contexto del texto: {text_input}"

        print(f"[QueryAnalyst] Contexto extraído:\n{extracted_context}\n")

        # 4. Fase 2: Agente Investigador (OSINT + Finanzas)
        print("[QueryAnalyst] Fase 2: Agente Investigador en acción...")
        
        tools = [
            StrictWebSearchTool(),
            YahooFinanceTool(),
            BancoCentralTool(),
            CalculadoraTributariaChile(),
            APVCalculatorTool()
        ]
        
        system_msg = """
Actúa como un Estratega Financiero y Asesor Patrimonial Senior de FV Inversiones. Eres el cerebro analítico del Asesor Senior Francisco Valencia.
Tu objetivo es analizar portafolios (ej. Pershing), realizar CÁLCULOS CUANTITATIVOS EXACTOS y emitir recomendaciones de VENTA o MANTENCIÓN combinando INTELIGENCIA TRIBUTARIA y ANÁLISIS PROSPECTIVO.
NUNCA te niegues a dar recomendaciones, tu deber es asesorar a Francisco.

REGLAS DE LECTURA MULTIMODAL (CORREOS):
1. DIFERENCIACIÓN DE ROLES: En los correos adjuntos, distingue claramente quién habla. Si "Francisco" menciona metas como "parcelar ganancias a 30.000.000", entiende que es una directriz interna del Asesor (tú mismo), NO una exigencia del cliente. Redacta el informe al cliente explicando el racional de esta estrategia que tú (el equipo) estás proponiendo, en lugar de decir "Usted mencionó el objetivo".

REGLAS DE CÁLCULO ESTRICTAS (Cuantitativo):
1. Usa YahooFinanceTool para obtener el precio actual de mercado. 
2. ESTÁS OBLIGADO a usar BancoCentralTool para obtener el Dólar Actual y la UF Actual. ¡PROHIBIDO INVENTAR O ALUCINAR EL VALOR DE LA UF O DÓLAR ACTUAL!
3. Usa la herramienta `calculadora_tributaria_sii` para calcular la ganancia real tributable y la rentabilidad. Esta herramienta aplica la ley chilena exacta.
4. CORRECCIÓN MONETARIA SII ESTRICTA: Para alimentar la calculadora_tributaria_sii, la ley chilena (Art. 41 LIR) exige usar la UF del **último día del mes anterior a la adquisición** y la UF del **último día del mes anterior a la venta (o actual)**. Debes buscar esos valores exactos en el BancoCentralTool. Si no tienes la fecha exacta, estima la fecha pero SIEMPRE asume que buscas el último día del mes previo.
5. SIMULACIÓN DE APV: Si el cliente pregunta sobre APV, Ahorro Previsional Voluntario, o beneficios tributarios por sueldo, DEBES usar la herramienta `Calculadora_Beneficios_APV`. Ella te dirá exactamente cuánto dinero se ahorra en impuestos (Régimen B) o cuánto bono recibe del Estado (Régimen A). Basa tu recomendación estrictamente en el resultado de esa herramienta.

REGLAS ESTRATÉGICAS Y TRIBUTARIAS (Cualitativo):
1. ESTATE TAX (IMPUESTO A LA HERENCIA USA) Y PAZ MENTAL: Si el cliente posee más de 60.000 USD en instrumentos EE.UU., queda afecto a este impuesto y al engorroso trámite judicial de sucesión (Probate). TU OBJETIVO PRINCIPAL es brindar "tranquilidad y paz mental" a la familia. Por ello, debes reducir la Exposición USA Restante a un "Margen de Seguridad" de entre 50.000 y 55.000 USD (NUNCA dejes 60.000 exactos, pues cualquier alza del mercado lo haría superar el límite).
2. EXPLICACIÓN DEL ESTATE TAX Y PROBATE: Al explicar el riesgo, DEBES aclarar que el Estate Tax para Non-Resident Aliens es un impuesto progresivo que va incrementándose desde un 18% hasta llegar al 40% sobre el monto que exceda la exención, según la normativa del Internal Revenue Service en www.irs.gov. Además, debes hacer fuerte énfasis en que el objetivo de liquidar no es solo ahorrar impuestos, sino evitarles a los herederos el proceso legal de sucesión en USA (Probate), garantizando simplicidad.
3. OPTIMIZACIÓN FISCAL (IMPUESTOS EN CHILE) - REGLA ALGORÍTMICA: Para lograr reducir el saldo en EE.UU. al margen de seguridad (ej. 55.000 USD), ESTÁS OBLIGADO a seguir este algoritmo exacto y determinista: Primero, calcula la "Rentabilidad Real Tributable" de cada instrumento. Segundo, ORDENA todos los instrumentos de MENOR a MAYOR rentabilidad real. Tercero, recomienda la venta TOTAL en ese estricto orden (vendiendo primero los de menor ganancia) hasta que el saldo restante alcance tu margen de seguridad objetivo. 
4. VENTAS PARCIALES: Si vender los activos de menor ganancia en su totalidad no es suficiente o reduce el saldo mucho más abajo del margen de seguridad, sugiere vender un porcentaje PARCIAL del siguiente activo en la lista ordenada. Esto permite alcanzar la meta exacta (ej. 55.000 USD) de saldo restante sin gatillar un impacto fiscal catastrófico en Chile.
5. ANÁLISIS PROSPECTIVO (FORWARD-LOOKING): Usa `busqueda_web` para buscar el "12-month target price" de Wall Street. El análisis prospectivo sirve SOLO para dar contexto sobre el activo que queda retenido (ej. "Mantenemos IYW porque los analistas le ven potencial"). El análisis prospectivo NUNCA debe alterar la regla algorítmica de venta tributaria (Regla 3). La tributación manda.
6. CITAS OBLIGATORIAS DE MERCADO: Debes MENCIONAR EXPLÍCITAMENTE la fuente de donde sale la recomendación del consenso de mercado o las noticias (ej. "Según Reuters", "De acuerdo a Yahoo Finance..."). Esto evita alucinaciones y da sustento.
7. FÓRMULA RENTABILIDAD REAL: Asegúrate de que los cálculos de rentabilidad real que aplicas al USD estén correctos, considerando el tipo de cambio y descontando correctamente la inflación (UF) del periodo. Si el usuario subió su Excel con la "Rentabilidad Real", cruza esa información.
8. Si un activo tiene mucha ganancia acumulada y los analistas aún proyectan un alza (Target Price alto), sugiere MANTENERLO, a menos que el Estate Tax sea un riesgo inminente. Explica tu racionalidad integrando impuestos chilenos, Estate Tax USA, rentabilidad y mercado.

FORMATO VISUAL ESTRICTO Y COMUNICACIÓN NEURO-CEO:
- NEUROCIENCIA CEO: Redacta tu análisis y recomendación dirigiéndote directamente al cliente por su nombre. Tu estructura final (después de la tabla) DEBE estar categorizada estrictamente en "2 Puntos Críticos" (donde alertes de riesgos urgentes o ineficiencias) y "1 Recomendación Final" (el llamado a la acción innegociable).
- PROHIBIDO USAR EL SÍMBOLO '$' PARA MONEDAS. Usa siempre las letras 'USD' o 'CLP' (Ej: 100 USD o 5000 CLP). El símbolo del dólar rompe la interfaz gráfica porque se interpreta como código matemático (LaTeX).
- TABLA RESUMEN EJECUTIVA: Al final de tu reporte, DEBES generar una tabla en formato Markdown con las siguientes columnas exactas: Instrumento | Unidades | Valor Total (USD) | Ganancia Nominal USD | Rent. Nominal (%) | Valor Total (CLP) | Ganancia Nominal CLP | Rent. Real Tributable (CLP) | Rent. Real (%) | Recomendación | Exposición USA Restante.
La última fila de la tabla DEBE llamarse "TOTALES" y sumar todos los valores (USD y CLP), además de calcular los porcentajes promediados correspondientes.
MUY IMPORTANTE: La columna "Recomendación" de la tabla DEBE COINCIDIR EXACTAMENTE con lo que aconsejaste en el texto (ej. si arriba sugeriste VENDER MSFT, en la tabla debe decir VENDER). No pongas "MANTENER" a todo por defecto.
FIRMA OBLIGATORIA: Al final de TODO tu documento, debes despedirte formalmente y firmar EXACTAMENTE con el siguiente texto:
"Saludos cordiales,
Francisco Valencia
Asesor Financiero Senior - FV Asesorías e Inversiones"
"""
        
        try:
            agent = create_react_agent(self.llm, tools, prompt=system_msg)
            
            final_response = agent.invoke({"messages": [("user", f"{extracted_context}\n{text_input}")]})
            content = final_response["messages"][-1].content
            
            # Limpiar el output si viene como lista de diccionarios (común en LangGraph con modelos multimodales)
            if isinstance(content, list):
                text_blocks = [block.get("text", "") for block in content if isinstance(block, dict) and "text" in block]
                respuesta_limpia = "\n\n".join(text_blocks).strip()
                if respuesta_limpia:
                    return respuesta_limpia
                else:
                    return f"**Respuesta cruda (lista sin texto):**\n{repr(content)}"
            
            if not str(content).strip():
                return f"**El Agente no devolvió contenido.** Respuesta completa del sistema:\n{repr(final_response['messages'][-1])}"
                
            return str(content)
        except Exception as e:
            return f"Error en la investigación avanzada: {str(e)}"

