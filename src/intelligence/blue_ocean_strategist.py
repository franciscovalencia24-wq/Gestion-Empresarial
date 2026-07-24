"""
Agente de Innovación y Arquitectura de Negocios — BD SENIOR
Genera oportunidades de Océano Azul para el negocio de Wealth Management chileno,
utilizando el contexto real de la plataforma (OSINT, RAG, Auditor, CRM).
"""
import os
import json
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv


# ─── Contexto del negocio real (fuente de verdad para el LLM) ────────────────
BUSINESS_CONTEXT = """
PLATAFORMA: BD SENIOR — CRM de Prospección Patrimonial
EMPRESA: FV Asesorías e Inversiones SpA (Francisco Valencia, Asesor Senior)
PARTNER PRINCIPAL: Principal Financial Group Chile

CAPACIDADES TECNOLÓGICAS ACTUALES:
- Motor OSINT: Scraping de Diario Oficial, InfoProbidad, CAMV
- RAG Advisor: Motor de consulta tributaria/normativa (CMF, SII, UAF)
- Auditor Patrimonial: Comparativa de portafolios con Monte Carlo (Wealth 3.0)
- CRM con segmentación, Kanban, campaña WhatsApp automatizada
- Enriquecimiento de datos: RUT, teléfono, empresa (TransUnion + Apollo.io)

PRODUCTO ESTRELLA: Seguro de Vida Patrimonial Preferente (Principal Financial Group)
MERCADO OBJETIVO ACTUAL: Altos patrimonios individuales ($100M+ CLP)
REGIÓN DE OPERACIÓN: IV Región (Coquimbo, La Serena) + expansión nacional
"""

PREDEFINED_STRATEGIES = [
    "Sindicatos de Minería y Energía (Atacama, Antofagasta)",
    "Asociaciones de Médicos y Especialistas Clínicos",
    "Ex-Funcionarios Públicos (PEP Retirados) — InfoProbidad",
    "Founders de Startups Chilenas (Pre-Exit / Serie A)",
    "Alianzas con Estudios de Abogados Tributarios y Notariales",
    "Asociaciones de Agricultores (Venta de Derechos de Agua y Tierras)",
    "Proptech: Inversionistas de Real Estate (DFL-2, Leasing)",
    "Cooperativas de Ahorro (COOPEUCH, CAPUAL, ServiEstado)",
    "Gremios de Ingenieros y Arquitectos (Colegios Profesionales)",
    "Familia empresarial regional (Empresas con sucesor sin plan)",
    "Microempresarios con Renta Imponible Alta (SII Grupo 2)",
    "Comunidades de Indemnizaciones (Juicios laborales / Liquidaciones)",
]


class BlueOceanStrategist:
    """
 PLATAFORMA: FV ASESORIAS E INVERSIONES impulsada por Altus AI
OBJETIVO: Detectar "Océanos Azules" (mercados no disputados) y diseñar
modelos de negocio escalables usando nuestra infraestructura.
    """

    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-flash-lite-latest",
                temperature=0.75,
                google_api_key=self.api_key,
            )
        else:
            self.llm = None
        self._memory_dir = "intelligence/playbooks"

    # ─────────────────────────────────────────────────────────────────────────
    def generate_business_brief(self, focus_area: str = "General") -> str:
        """
        Genera un reporte ejecutivo de una nueva oportunidad de negocio,
        adaptado al contexto real de la plataforma FV ASESORIAS E INVERSIONES.
        """
        if not self.llm:
            return "⚠️ Error: GOOGLE_API_KEY no configurada en el archivo .env."

        prompt = f"""
{BUSINESS_CONTEXT}

Eres un experto en Estrategia de Océano Azul y Arquitectura de Negocios en el        adaptado al contexto real de FV ASESORIAS E INVERSIONES.
        Debe ser una propuesta CORTA, VIOLENTA Y EXTREMADAMENTE
        RENTABLE y EJECUTABLE usando nuestras capacidades tecnológicas actuales.

ÁREA DE ENFOQUE: {focus_area}

REGLAS:
1. No repitas ideas genéricas de "venderle a clientes individuales".
2. Piensa en estructuras organizacionales: sindicatos, gremios, B2B, alianzas.
3. La solución DEBE usar al menos 2 capacidades tecnológicas de la plataforma.
4. El modelo de ingresos debe ser específico (fee fijo, % AUM, success fee, licencia).
5. El plan de acción debe ser ejecutable en los próximos 30 días con recursos actuales.

FORMATO DE SALIDA (Markdown estricto):
# 🌊 [Título de la Oportunidad]

**Concepto en una línea:** [Descripción ejecutiva de 20 palabras máximo]

---

### 🎯 El Océano Azul
[Por qué este mercado está desatendido en Chile. Tamaño estimado del mercado. Quiénes son.]

### 🛠️ Cómo lo ejecutamos con FV ASESORIAS E INVERSIONES
[Qué módulos usamos: OSINT para identificar, Auditor para demostrar valor, RAG para asesoría, CRM para contactar]

### 💰 Modelo de Ingresos
| Concepto | Tarifa | Frecuencia |
|----------|--------|------------|
| [Ej: Fee de entrada] | [Monto] | [Única / Mensual] |

### 🚀 Plan de Acción — Primeros 30 días
1. **Semana 1:** [Acción concreta]
2. **Semana 2:** [Acción concreta]
3. **Semana 3-4:** [Acción concreta]

### ⚠️ Riesgos y Mitigación
- [Riesgo 1]: [Cómo mitigarlo]
"""
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            return f"❌ Error generando estrategia: {e}"

    # ─────────────────────────────────────────────────────────────────────────
    def get_competitive_analysis(self, focus_area: str) -> str:
        """Genera un análisis rápido de competidores y diferenciadores."""
        if not self.llm:
            return "⚠️ GOOGLE_API_KEY no configurada."
        prompt = f"""
{BUSINESS_CONTEXT}

Para el nicho: {focus_area}

Analiza en 3 párrafos cortos:
1. ¿Quiénes son los competidores actuales en Chile en este nicho?
2. ¿Cuál es el diferenciador estratégico de FV ASESORIAS E INVERSIONES vs. la competencia?
3. ¿Cuál es la propuesta de valor en una frase para el decisor de ese segmento?

Responde en formato Markdown, directo y ejecutivo.
"""
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            return f"Error: {e}"

    # ─────────────────────────────────────────────────────────────────────────
    def save_strategy(self, focus_area: str, content: str) -> str:
        """Guarda una estrategia generada como archivo Markdown en el playbook."""
        os.makedirs(self._memory_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        safe_name = focus_area.replace(" ", "_").replace("/", "-")[:40]
        path = os.path.join(self._memory_dir, f"oceano_azul_{safe_name}_{ts}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Estrategia: {focus_area}\n")
            f.write(f"*Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}*\n\n")
            f.write(content)
        return path

    # ─────────────────────────────────────────────────────────────────────────
    def get_predefined_strategies(self) -> list:
        """Lista de áreas de enfoque sugeridas para el mercado chileno."""
        return PREDEFINED_STRATEGIES
