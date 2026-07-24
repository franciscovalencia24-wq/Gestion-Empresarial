import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Esquemas de Salida Estructurada (Pydantic)
class CartolaTransactionSchema(BaseModel):
    fecha: str = Field(description="Fecha de la transacción (ej. 2026-05-15)")
    descripcion: str = Field(description="Descripción del movimiento")
    monto: float = Field(description="Monto. Positivo si es abono/ingreso, negativo si es cargo/egreso.")
    categoria: str = Field(description="Categoría sugerida (Ej: Supermercado, Salud, Inversiones, Sueldo, Ocio, Seguros, Créditos, Otros)")

class CartolaSummarySchema(BaseModel):
    mes: str = Field(description="Mes y año de la cartola (ej. 2026-05)")
    institucion_bancaria: str = Field(description="Nombre del banco o institución (ej. Banco Santander, Banco de Chile)")
    saldo_inicial: float = Field(description="Saldo al inicio del periodo")
    saldo_final: float = Field(description="Saldo al final del periodo")
    total_ingresos: float = Field(description="Suma total de abonos/ingresos en el periodo")
    total_egresos: float = Field(description="Suma total de cargos/egresos en el periodo (valor absoluto positivo)")
    gasto_supermercado: float = Field(description="Suma estimada de gastos en supermercados o alimentación")
    gasto_seguros: float = Field(description="Suma estimada de pagos de seguros (vida, salud, auto)")
    gasto_creditos: float = Field(description="Suma estimada de pagos de créditos o dividendos")
    gasto_ocio: float = Field(description="Suma estimada de gastos en ocio, restaurantes, viajes")
    capacidad_ahorro_estimada: float = Field(description="Ingresos totales menos egresos totales. Positivo es ahorro.")
    analisis_cualitativo: str = Field(description="Análisis cualitativo detallado. DEBE usar formato Markdown con viñetas (bullet points). Si es inversión, incluye 4 viñetas: 🏛️ Instrumentos, 📈 Rentabilidad, ⚠️ Riesgos, 💸 Costos. Si es cuenta corriente, analiza gastos.")
    transacciones: Optional[List[CartolaTransactionSchema]] = Field(default=[], description="Lista detallada de transacciones si se solicita extracción profunda.")

class CartolaReader:
    """
    Módulo de Ingesta Autónoma (Fase D).
    Lee un PDF de cartola bancaria, extrae el texto y utiliza Gemini Flash
    para estructurar la información en un formato JSON listo para la base de datos.
    """
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            # Usamos Flash que es ultrarrápido y tiene alto rate limit
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-flash-latest",
                temperature=0.0, 
                google_api_key=self.api_key
            )
        else:
            self.llm = None

    def analyze_pdf(self, pdf_path: str, extract_transactions: bool = False) -> CartolaSummarySchema:
        if not self.llm:
            raise ValueError("GOOGLE_API_KEY no configurada.")
        
        # 1. Extraer texto bruto del PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        raw_text = "\n".join([page.page_content for page in pages])
        
        # Si el texto es muy largo, lo truncamos (Flash soporta 1M+ tokens, pero por eficiencia)
        raw_text = raw_text[:30000] 

        # 2. Configurar LLM con Salida Estructurada (Structured Output)
        structured_llm = self.llm.with_structured_output(CartolaSummarySchema)
        
        # 3. Prompt de extracción
        prompt = f"""
        Eres un experto analista financiero y sistema de Document AI.
        A continuación, te proporcionaré el texto extraído mediante OCR de una Cartola Bancaria o Estado de Cuenta.
        Tu trabajo es extraer los datos clave, clasificar los gastos y entregar un resumen estructurado.
        
        REGLAS:
        - Si el texto está sucio o desordenado, usa tu lógica financiera para identificar qué es un abono y qué es un cargo.
        - Calcula los totales si no están explícitos.
        - IMPORTANTE: La mayoría de estos documentos son CARTOLAS DE INVERSIONES (Fondo Mutuo, APV, BNY Pershing, Corredoras).
        - En cartolas de inversión, clasifica los "Aportes/Depósitos" como `total_ingresos` y los "Retiros/Rescates" como `total_egresos`.
        - Para cartolas de inversión, establece los gastos (supermercado, ocio, créditos) en 0.
        - La `capacidad_ahorro_estimada` debe ser simplemente los Aportes menos los Retiros. JAMÁS uses la palabra "ahorro" o "flujo neto" en tu `analisis_cualitativo`. Usa "Aportes Netos" o "Retiros Netos".
        - {'EXTRAE TODAS LAS TRANSACCIONES INDIVIDUALES. Esto es un modo de extracción profunda.' if extract_transactions else 'NO extraigas las transacciones individuales, deja la lista de transacciones vacía. Concéntrate solo en el resumen y los totales.'}
        
        TEXTO DE LA CARTOLA:
        -------------------
        {raw_text}
        -------------------
        """
        
        print("[CartolaReader] Procesando documento con Gemini Structured Output...")
        result: CartolaSummarySchema = structured_llm.invoke(prompt)
        return result
