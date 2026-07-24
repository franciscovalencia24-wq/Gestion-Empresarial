from pydantic import BaseModel, Field
from typing import Optional, Type, Dict
from langchain.tools import BaseTool
import json
from src.utils.simulators.apv_simulator import APVSimulator
from src.osint.bcc_tool import BancoCentralTool

class APVCalculatorInput(BaseModel):
    sueldo_bruto_mensual: float = Field(..., description="El sueldo bruto mensual del cliente en CLP (pesos chilenos).")
    aporte_apv_mensual: float = Field(..., description="El monto que el cliente desea aportar al APV cada mes en CLP (pesos chilenos).")

class APVCalculatorTool(BaseTool):
    name: str = "Calculadora_Beneficios_APV"
    description: str = "Útil para simular e identificar cuánto dinero exacto se ahorrará un cliente en impuestos al aportar a un APV mensual, o cuánto le bonificará el Estado."
    args_schema: Type[BaseModel] = APVCalculatorInput

    def _run(self, sueldo_bruto_mensual: float, aporte_apv_mensual: float) -> str:
        try:
            # Init tools
            bcc = BancoCentralTool()
            uf_val = bcc.get_uf_actual()
            if uf_val == 0.0:
                uf_val = 38000
                
            sim = APVSimulator(uf_actual=uf_val)
            
            res_a = sim.calcular_beneficio_regimen_a(aporte_mensual_clp=aporte_apv_mensual)
            res_b = sim.calcular_beneficio_regimen_b(sueldo_bruto_clp=sueldo_bruto_mensual, aporte_mensual_clp=aporte_apv_mensual)
            
            # Formatting response for LLM
            report = (
                f"Resultados de la Simulación APV (Aporte de {aporte_apv_mensual:,.0f} CLP / mes, Sueldo {sueldo_bruto_mensual:,.0f} CLP / mes):\n"
                f"- RÉGIMEN B (Ahorro de Impuestos): El cliente se ahorrará {res_b['ahorro_tributario_anual_clp']:,.0f} CLP anuales en impuestos. Mensualmente su sueldo líquido bajará menos de lo que aporta, porque deja de pagar {res_b['ahorro_tributario_mensual_clp']:,.0f} CLP en impuestos cada mes.\n"
                f"- RÉGIMEN A (Bono del Estado): El estado le depositará directamente {res_a['bonificacion_estado_clp']:,.0f} CLP extra al año a su cuenta (15% del aporte).\n\n"
                "RECOMENDACIÓN ALGORÍTMICA PARA EL AGENTE: Recomienda Régimen B si el cliente tiene un sueldo tributable alto y el ahorro tributario supera el 15%. De lo contrario, recomienda Régimen A."
            )
            return report
        except Exception as e:
            return f"Error calculando APV: {str(e)}"

    async def _arun(self, sueldo_bruto_mensual: float, aporte_apv_mensual: float) -> str:
        return self._run(sueldo_bruto_mensual, aporte_apv_mensual)
