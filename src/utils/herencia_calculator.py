import os
import sys
import logging

# Ensure src module is reachable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.intelligence.rag_advisor import RAGAdvisorV2

logger = logging.getLogger("HerenciaCalculator")

class HerenciaCalculator:
    def __init__(self):
        self.rag = RAGAdvisorV2()
        
    def generar_analisis_herencia(self, cliente_nombre, herederos, activos=None, masa_patrimonial=None):
        """
        Consulta la ley chilena (vía RAG local) para estructurar el testamento 
        y calcular el impuesto a la herencia estimado, analizando exenciones por tipo de activo.
        
        herederos: dict con 'conyuge' (bool) y 'numero_hijos' (int)
        activos: dict opcional con 'propiedades' (lista de str), 'polizas' (lista de str), 'inversiones' (lista de str)
        """
        if activos is None:
            activos = {}
            
        detalle_activos = ""
        if activos:
            detalle_activos = "Detalle de Activos Relevantes para Análisis de Exenciones Tributarias:\n"
            if activos.get("propiedades"):
                detalle_activos += "- Propiedades:\n  * " + "\n  * ".join(activos["propiedades"]) + "\n"
            if activos.get("polizas"):
                detalle_activos += "- Pólizas de Seguro:\n  * " + "\n  * ".join(activos["polizas"]) + "\n"
            if activos.get("inversiones"):
                detalle_activos += "- Inversiones (AFP Cta 2, APV, etc):\n  * " + "\n  * ".join(activos["inversiones"]) + "\n"

        logger.info(f"Generando análisis de herencia detallado para {cliente_nombre}")
        
        prompt = f"""
        El cliente {cliente_nombre} tiene el siguiente perfil patrimonial.
        Masa Patrimonial Total Estimada: ${masa_patrimonial:,.0f} CLP si se provee, sino guíate por los activos.
        Su conformación familiar es: Cónyuge sobreviviente: {'Sí' if herederos.get('conyuge') else 'No'}, Número de hijos: {herederos.get('numero_hijos', 0)}.
        
        {detalle_activos}
        
        Por favor, actúa como abogado experto en derecho sucesorio e impuesto a la herencia chileno (Ley 16.271) y realiza lo siguiente:
        1. Explica brevemente cómo se distribuye la herencia según la ley chilena (Mitad legitimaria, Cuarta de mejoras, Cuarta de libre disposición).
        2. Analiza exhaustivamente los activos listados en busca de FRANQUICIAS Y BENEFICIOS TRIBUTARIOS. Específicamente, verifica:
           - Seguros de Vida contratados ANTES de febrero de 2022 (Exentos de impuesto a la herencia).
           - Fondos en Cuenta 2 de AFP (Tienen una exención de 4.000 UF).
           - Propiedades DFL2 u otras propiedades (Menciona reglas sobre fecha de adquisición, ej: pre-2003, y si conviene venderlas en vida versus heredarlas).
        3. Realiza una estimación conceptual del Impuesto a la Herencia a pagar por cada heredero, detallando las deducciones de UTA según parentesco.
        4. Redacta un borrador formal de cláusula testamentaria que asigne la Cuarta de Mejoras y Cuarta de Libre Disposición para optimizar el patrimonio.
        
        Devuelve el resultado en formato Markdown profesional. No inventes leyes, básate en el SII, CMF y la Ley 16.271.
        """
        
        try:
            # Query the local RAG
            respuesta_legal = self.rag.ask(prompt)
            return respuesta_legal
        except Exception as e:
            logger.error(f"Error consultando RAG para herencia: {e}")
            return f"Hubo un error al conectar con el motor legal local: {e}"

    def calcular_flujo_caja_sucesorio(self, ingresos_pasivos_mensuales: float, gastos_vida: float, 
                                      sueldos_servicios: float, compromisos_fijos: float, seguros_vigentes: float) -> dict:
        """
        Calcula el flujo de caja operativo/sucesorio para estimar si el estándar de vida
        se mantiene o hay déficit, y calcula la brecha de capital requerida.
        """
        gastos_mensuales_totales = gastos_vida + sueldos_servicios + compromisos_fijos + seguros_vigentes
        flujo_neto_mensual = ingresos_pasivos_mensuales - gastos_mensuales_totales
        flujo_neto_anual = flujo_neto_mensual * 12
        
        # Asumimos una tasa libre de riesgo / retiro seguro conservadora del 4% anual
        # para calcular cuánto capital líquido se requiere para cubrir el déficit.
        tasa_retiro_seguro = 0.04
        
        if flujo_neto_anual < 0:
            brecha_sucesoria_capital = abs(flujo_neto_anual) / tasa_retiro_seguro
            estado = "DÉFICIT"
        else:
            brecha_sucesoria_capital = 0.0
            estado = "SUPERÁVIT"
            
        return {
            "gastos_mensuales_totales": gastos_mensuales_totales,
            "gastos_trimestrales_totales": gastos_mensuales_totales * 3,
            "gastos_anuales_totales": gastos_mensuales_totales * 12,
            "ingresos_pasivos_mensuales": ingresos_pasivos_mensuales,
            "flujo_neto_mensual": flujo_neto_mensual,
            "flujo_neto_anual": flujo_neto_anual,
            "estado_flujo": estado,
            "brecha_sucesoria_capital_requerido": brecha_sucesoria_capital,
            "tasa_retiro_asumida": tasa_retiro_seguro
        }

if __name__ == "__main__":
    # Prueba rápida
    calc = HerenciaCalculator()
    resultado = calc.generar_analisis_herencia(
        cliente_nombre="Juan Pérez",
        masa_patrimonial=1500000000,
        herederos={"conyuge": True, "numero_hijos": 2},
        activos={
            "propiedades": ["Casa DFL2 adquirida en 2001 (UF 10.000)", "Depto adquirido en 2018 (UF 5.000)"],
            "polizas": ["Seguro de Vida con Ahorro Principal contratado en 2019 por UF 3.000"],
            "inversiones": ["Cuenta 2 AFP Habitat con $150.000.000 CLP"]
        }
    )
    print("=== REPORTE GENERADO ===")
    print(resultado)
