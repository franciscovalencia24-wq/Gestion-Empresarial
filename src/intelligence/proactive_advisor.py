import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import Prospect, ClientProfile, CartolaSummary
from src.intelligence.rag_advisor import RAGAdvisorV2
from src.intelligence.monte_carlo import MonteCarloEngine

class ProactiveAdvisor:
    """
    Asesor Tributario Proactivo Autónomo (Fase D).
    Toma toda la información estructurada de un cliente (CRM + Cartolas extraídas por OCR),
    y genera una Propuesta Estratégica Patrimonial de alto valor.
    """
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-flash-latest", 
                temperature=0.3,
                google_api_key=self.api_key
            )
        else:
            self.llm = None
            
        _PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        _PERSIST_DIR  = os.path.join(_PROJECT_ROOT, "data", "vector_db_local")
        self.rag_engine = RAGAdvisorV2(persist_dir=_PERSIST_DIR)

    def generate_strategy(self, prospect: Prospect, profile: ClientProfile, cartolas: list[CartolaSummary]) -> str:
        if not self.llm:
            return "Error: GOOGLE_API_KEY no configurada."
            
        perfil_text = f"""
        **Perfil del Cliente:**
        Nombre: {prospect.nombre or 'Desconocido'}
        RUT: {prospect.rut}
        Edad Cronológica: {profile.edad if profile and profile.edad else 'Desconocida'}
        Edad Actuarial (Seguros): {profile.edad_actuarial if profile and profile.edad_actuarial else 'Desconocida'}
        Fecha de Nacimiento: {profile.fecha_nacimiento if profile and profile.fecha_nacimiento else 'Desconocida'}
        Estado Civil: {profile.estado_civil if profile and profile.estado_civil else 'Desconocido'}
        Herederos Legales: {profile.cantidad_herederos if profile and hasattr(profile, 'cantidad_herederos') else 'Desconocido'}
        Segmento Estratégico: {profile.segmento_cliente if profile and hasattr(profile, 'segmento_cliente') else 'Desconocido'}
        Nivel de Riesgo: {profile.nivel_riesgo if profile and hasattr(profile, 'nivel_riesgo') else 'Desconocido'}
        Experiencia en Inversiones: {profile.experiencia_inversiones if profile and hasattr(profile, 'experiencia_inversiones') else 'Desconocida'}
        Patrimonio Líquido: ${profile.patrimonio_liquido if profile else 0:,.0f}
        Patrimonio Inmobiliario: ${profile.patrimonio_inmobiliario if profile else 0:,.0f}
        Flujo de Ingresos Mensuales Estimados: ${profile.ingresos_mensuales if profile and hasattr(profile, 'ingresos_mensuales') and profile.ingresos_mensuales else 0:,.0f}
        Flujo de Egresos Mensuales Estimados: ${profile.egresos_mensuales if profile and hasattr(profile, 'egresos_mensuales') and profile.egresos_mensuales else 0:,.0f}
        """

        cartolas_text = "**Resumen Financiero Mensual (OCR Document AI):**\n"
        if not cartolas:
            cartolas_text += "No hay cartolas analizadas para este cliente.\n"
        else:
            for c in cartolas:
                cartolas_text += f"- Mes: {c.mes} | Institución: {c.institucion_bancaria}\n"
                cartolas_text += f"  Total Aportes Recibidos: ${c.total_ingresos:,.0f} | Total Retiros: ${c.total_egresos:,.0f}\n"

        try:
            if profile and hasattr(profile, 'ingresos_mensuales') and profile.ingresos_mensuales:
                ahorro_mensual = profile.ingresos_mensuales - (profile.egresos_mensuales or 0)
            else:
                ahorro_mensual = 0
            
            patrimonio_actual = profile.patrimonio_liquido if profile else 0
            riesgo = profile.nivel_riesgo if profile and hasattr(profile, 'nivel_riesgo') else "Moderado"
            edad_actual = profile.edad if profile and profile.edad else 40
            horizonte = max(90 - edad_actual, 10) # Simular hasta los 90 años
            
            mc_results = MonteCarloEngine.run_wealth_projection(
                patrimonio_inicial=patrimonio_actual,
                ahorro_mensual=ahorro_mensual,
                perfil_riesgo=riesgo,
                horizonte_anos=horizonte
            )
            
            mc_text = f"**Resultados Matemáticos (Simulación Monte Carlo a {horizonte} años):**\n"
            mc_text += f"- Escenario Pesimista (P10): ${mc_results['escenario_pesimista_10']:,.0f}\n"
            mc_text += f"- Escenario Esperado (P50): ${mc_results['escenario_esperado_50']:,.0f}\n"
            mc_text += f"- Escenario Optimista (P90): ${mc_results['escenario_optimista_90']:,.0f}\n"
            mc_text += f"(Basado en {mc_results['simulaciones_ejecutadas']} iteraciones de volatilidad de mercado)\n"
        except Exception as e:
            mc_text = "Simulación cuantitativa Monte Carlo no disponible temporalmente."

        try:
            rag_context = self.rag_engine.ask("Resume brevemente los beneficios tributarios actuales del APV y los topes exentos del impuesto a la herencia en Chile.")
        except:
            rag_context = "Contexto tributario RAG no disponible temporalmente."

        prompt = f"""
        Actúa como un Asesor Patrimonial y Tributario Senior de "FV Asesorías e Inversiones" (Wealth Management).
        Tu objetivo es leer el perfil del cliente, leer su flujo de caja, y redactar una 'Propuesta Estratégica de Valor' 
        altamente personalizada y proactiva. No estás respondiendo preguntas, estás entregando un informe no solicitado de alto valor.

        DATOS DEL CLIENTE:
        {perfil_text}
        
        {cartolas_text}
        
        PROYECCIONES CUANTITATIVAS INSTITUCIONALES:
        {mc_text}
        
        LEYES TRIBUTARIAS VIGENTES (Extraídas del RAG interno):
        {rag_context}

        ESTRUCTURA DEL REPORTE (Comunicación Estilo CEO & Neurociencia):
        Tu respuesta DEBE seguir estrictamente esta estructura de comunicación:
        1. **Pausa Reflexiva (Resumen Ejecutivo y Patrimonial):** Una introducción directa y reflexiva que delimite la situación financiera actual del cliente en un solo párrafo. DEBES mencionar explícitamente su nivel y estructura de Ahorro Mensual (por ejemplo, cuánto aporta a APV, descuentos por planilla, o depósitos regulares).
        2. **Los 2 Puntos Críticos:** Identifica y enumera EXCLUSIVAMENTE los dos problemas u oportunidades más urgentes/críticos basados en su edad, impuestos o flujo de caja (Usa los ingresos/egresos del perfil, NO uses las cartolas de inversión para asumir su flujo de caja real). Explícalos de forma concisa.
        3. **Conclusión y Plan de Acción:** Una directriz clara sobre los siguientes pasos a tomar.
        4. **🎁 Bono de Valor (Inesperado):** (Aplicando Error de Predicción de Recompensa Positivo). Extrae una lección profunda de psicología o tácticas de negociación que se relacione con el dilema o perfil del cliente y ofrécesela como un "Consejo C-Level".

        REGLAS DE COMUNICACIÓN:
        - Sé asertivo, profesional y consultivo, usa un tono de CEO de "FV Asesorías e Inversiones".
        - Sé muy específico con los números del cliente.
        - Si el cliente tiene 65 años o más, INCLUYE EXPLICITAMENTE como uno de los Puntos Críticos recomendar la contratación de un "Seguro de Vida con Ahorro en PRINCIPAL Financial Group". ATENCIÓN (REGLA ESTRICTA): Las pólizas emitidas a partir de febrero de 2022 SÍ pagan impuesto a la herencia, NUNCA digas que están exentas. El argumento principal de venta es que entregan liquidez inmediata a los herederos en pocos días sin necesidad de esperar el trámite de posesión efectiva.
        - Usa la 'Edad Actuarial' al referirte a la viabilidad de seguros de vida.
        - Formatea el texto en Markdown hermoso y fácil de leer.
        """
        
        print("[ProactiveAdvisor] Generando Estrategia Autónoma...")
        
        try:
            from langchain_core.output_parsers import StrOutputParser
            chain = self.llm | StrOutputParser()
            return chain.invoke(prompt)
        except Exception as e:
            return f"Error generando estrategia con Langchain: {str(e)}"
