# src/intelligence/strategy_engine.py
import pandas as pd

def generate_strategic_recommendations(prospect, deudas_df, inversiones_df, propiedades_df, polizas_df, sociedades_df):
    """
    Motor de Recomendaciones Estratégicas para el MFO.
    Analiza el patrimonio y entrega insights consultivos de alto valor.
    """
    recomendaciones = []
    
    # 1. Análisis de Liquidez y Deuda
    total_deuda = deudas_df['Monto Actual'].sum() if not deudas_df.empty and 'Monto Actual' in deudas_df.columns else 0
    total_inversion = inversiones_df['Monto USD'].sum() if not inversiones_df.empty and 'Monto USD' in inversiones_df.columns else 0 # Asumiendo columna
    
    if total_deuda > 0 and total_inversion > total_deuda * 2:
        recomendaciones.append({
            "categoria": "Estructuración de Pasivos",
            "titulo": "Oportunidad de Prepago Estratégico",
            "descripcion": "Existe suficiente liquidez en el portafolio de inversiones para liquidar las deudas vigentes. Recomendamos evaluar el costo financiero de la deuda (TCAE) versus la rentabilidad esperada del portafolio. Si el costo de la deuda es mayor, el prepago generará valor inmediato."
        })

    # 2. Análisis Inmobiliario
    if not propiedades_df.empty:
        prop_arrendadas = propiedades_df[propiedades_df.get('Arrendada') == True]
        if len(prop_arrendadas) < len(propiedades_df) and len(propiedades_df) > 2:
            recomendaciones.append({
                "categoria": "Optimización Inmobiliaria",
                "titulo": "Rentabilización de Activos Fijos",
                "descripcion": "Se detectan propiedades sin flujo de caja activo (no arrendadas). Recomendamos un análisis de 'Highest and Best Use' (HBU) para rentabilizar estos activos o liquidarlos y reinvertir el capital en instrumentos financieros más eficientes tributariamente."
            })

    # 3. Análisis Societario (VPP)
    if not sociedades_df.empty and len(sociedades_df) > 1:
        recomendaciones.append({
            "categoria": "Gobierno Corporativo y Tributario",
            "titulo": "Consolidación en Holding / Family Office",
            "descripcion": "Dada la multiplicidad de vehículos de inversión (sociedades), sugerimos establecer un Holding Matriz que consolide las participaciones. Esto optimizará el flujo de dividendos, facilitará el control y sentará las bases para un Protocolo Familiar formal."
        })

    # 4. Planificación Sucesoria y Seguros
    total_polizas = polizas_df['Monto (UF)'].sum() if not polizas_df.empty and 'Monto (UF)' in polizas_df.columns else 0
    if total_polizas < 5000:
        recomendaciones.append({
            "categoria": "Resguardo Patrimonial y Herencia",
            "titulo": "Déficit de Cobertura para Liquidez Sucesoria",
            "descripcion": "El capital asegurado actual puede no ser suficiente para cubrir los impuestos a la herencia y deudas latentes en caso de sucesión. Se recomienda estructurar una póliza de vida inembargable (Art. 57 LIR) que provea liquidez inmediata a los herederos sin pasar por posesión efectiva."
        })

    # 5. Recomendación Genérica MFO
    recomendaciones.append({
        "categoria": "Estructura MFO y Protocolo Familiar",
        "titulo": "Implementación de Gobierno Corporativo Familiar",
        "descripcion": "Para asegurar la continuidad del patrimonio transgeneracional, es crítico establecer un Consejo de Familia, un Comité de Inversiones formal y un Protocolo Familiar que dicte las reglas de sucesión, participación de herederos en las empresas y resolución de conflictos."
    })

    return recomendaciones
