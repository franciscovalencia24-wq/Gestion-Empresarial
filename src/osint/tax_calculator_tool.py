from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional

class TaxCalculatorInput(BaseModel):
    instrumento: str = Field(description="Nombre o ticker del instrumento (ej. MSFT, IYW)")
    cantidad: float = Field(description="Cantidad de acciones o cuotas del instrumento")
    precio_compra_usd: float = Field(description="Precio unitario de compra en dólares")
    precio_actual_usd: float = Field(description="Precio unitario actual de mercado en dólares")
    dolar_historico: float = Field(description="Valor del dólar observado (CLP) al momento de la compra")
    dolar_actual: float = Field(description="Valor del dólar observado (CLP) al momento actual")
    uf_historica: float = Field(description="Valor de la UF (CLP) al momento de la compra")
    uf_actual: float = Field(description="Valor de la UF (CLP) al momento actual")

class CalculadoraTributariaChile(BaseTool):
    name: str = "calculadora_tributaria_sii"
    description: str = "Calcula la rentabilidad real y el mayor valor tributable en Chile para inversiones extranjeras (Pershing) aplicando corrección monetaria de la UF."
    args_schema: Type[BaseModel] = TaxCalculatorInput

    def _run(self, instrumento: str, cantidad: float, precio_compra_usd: float, precio_actual_usd: float, 
             dolar_historico: float, dolar_actual: float, uf_historica: float, uf_actual: float) -> str:
        try:
            # 1. Costo Base Total en USD y CLP
            costo_base_usd = precio_compra_usd * cantidad
            costo_base_clp = costo_base_usd * dolar_historico
            
            # 2. Corrección Monetaria del Costo Base (Inflación vía UF)
            if uf_historica <= 0:
                return "Error: La UF histórica debe ser mayor a 0."
                
            factor_correccion = uf_actual / uf_historica
            costo_base_corregido_clp = costo_base_clp * factor_correccion
            
            # 3. Valor de Enajenación (Venta) Total en USD y CLP
            valor_actual_usd = precio_actual_usd * cantidad
            valor_actual_clp = valor_actual_usd * dolar_actual
            
            # 4. Cálculo de Ganancias y Rentabilidad Nominal USD
            ganancia_nominal_usd = valor_actual_usd - costo_base_usd
            rentabilidad_nominal_usd = (ganancia_nominal_usd / costo_base_usd) * 100 if costo_base_usd > 0 else 0
            
            # 5. Cálculo Tributario (Mayor Valor en CLP) y Rentabilidad Real
            mayor_valor_tributable_clp = valor_actual_clp - costo_base_corregido_clp
            rentabilidad_real_clp = (mayor_valor_tributable_clp / costo_base_corregido_clp) * 100 if costo_base_corregido_clp > 0 else 0
            
            return (
                f"### Resultados Tributarios SII para {instrumento}\n"
                f"- **Inversión Inicial (Costo Base Nominal):** {costo_base_usd:,.2f} USD | {costo_base_clp:,.0f} CLP\n"
                f"- **Costo Base Corregido por Inflación (UF):** {costo_base_corregido_clp:,.0f} CLP\n"
                f"- **Valor Actual de Mercado:** {valor_actual_usd:,.2f} USD | {valor_actual_clp:,.0f} CLP\n"
                f"- **Rentabilidad Nominal en Dólares:** {rentabilidad_nominal_usd:.2f}%\n"
                f"- **Mayor Valor Tributable (Ganancia Real CLP a tributar):** {mayor_valor_tributable_clp:,.0f} CLP\n"
                f"- **Rentabilidad Real Ajustada:** {rentabilidad_real_clp:.2f}%\n"
            )
        except Exception as e:
            return f"Error en la calculadora tributaria: {str(e)}"
