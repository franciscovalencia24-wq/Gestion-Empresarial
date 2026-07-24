import os
import google.generativeai as genai
from typing import List, Dict

WHITELIST_FONDOS = [
    "GESTION ACTIVA ARRIESGADO",
    "GLOBAL EQUITY",
    "CAPITALES ACCIONES",
    "LATAM EQUITY"
]

class SFOEngine:
    """
    Synthetic Family Office (SFO) Engine.
    El 'Clon IA' que simula impactos de mercado en el portafolio del cliente y recomienda rebalanceos
    restringidos a la Lista Blanca de FV Asesorías e Inversiones.
    """
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.llm = None
        else:
            genai.configure(api_key=api_key)
            self.llm = genai.GenerativeModel(
                model_name="gemini-2.5-pro",
                system_instruction=self._build_system_prompt()
            )

    def _build_system_prompt(self):
        return f'''Eres el motor algorítmico 'SFO' (Synthetic Family Office) de FV ASESORIAS E INVERSIONES impulsada por Altus AI.
Tu misión es proteger y optimizar el patrimonio de clientes de Alto Patrimonio ante turbulencias del mercado.

REGLAS DE REBALANCEO (FIDUCIARIAS):
Si recomiendas mover fondos o rebalancear la cartera tras un shock de mercado, DEBES seleccionar EXCLUSIVAMENTE entre los siguientes fondos pre-aprobados (Whitelist):
{", ".join(WHITELIST_FONDOS)}
Bajo ninguna circunstancia puedes recomendar acciones individuales ni fondos fuera de esta lista.

TONO Y ESTILO:
Institucional, urgente pero calmado. Hablas como un banquero privado de élite comunicándole una alerta temprana a su cliente.
'''

    def run_stress_test(self, prospect_info: str, portfolio_data: str, market_shock: str) -> str:
        """
        Ejecuta la simulación de estrés y genera la propuesta de rebalanceo.
        """
        if not self.llm:
            return "⚠️ GOOGLE_API_KEY no configurada. El motor SFO está apagado."

        prompt = f"""
Ejecuta un 'Test de Estrés de Legado' (SFO Alert) para el siguiente cliente debido a un shock de mercado.

EVENTO DE MERCADO (SHOCK): {market_shock}

DATOS DEL CLIENTE:
{prospect_info}

PORTAFOLIO DE INVERSIONES ACTUAL:
{portfolio_data}

Instrucciones de Salida:
Genera un memorándum de alerta para el cliente con la siguiente estructura (usa Markdown):

# 🚨 SFO Alert: Impacto de Mercado en su Portafolio
Estimado/a [Nombre Cliente], nuestro motor de Inteligencia Artificial (SFO) ha detectado un evento relevante que afecta sus inversiones.

## 💥 1. El Evento y su Impacto Aritmético
[Explica brevemente el evento de mercado y, basado en su portafolio real, calcula un estimado de pérdida/ganancia monetaria o porcentual en la cartera. Haz matemáticas simples pero contundentes].

## 🛡️ 2. Propuesta de Blindaje y Rebalanceo
Para mitigar este riesgo o aprovechar la oportunidad, nuestro comité sugiere las siguientes 3 alternativas tácticas de ejecución inmediata. 
(Recuerda, DEBES usar los fondos de la Whitelist de FV Asesorías: {", ".join(WHITELIST_FONDOS)}).

1. [Opción 1 con Fondo Whitelist] - [Razón técnica de por qué este fondo amortigua el golpe]
2. [Opción 2 con Fondo Whitelist] - [Razón]
3. [Opción 3 con Fondo Whitelist] - [Razón]

## ⚡ 3. Próximo Paso
[Un call to action indicando que el cliente puede responder este mensaje o presionar un botón para autorizar el movimiento].
"""
        try:
            response = self.llm.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error en la simulación SFO: {str(e)}"
