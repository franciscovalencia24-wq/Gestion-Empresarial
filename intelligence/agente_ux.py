import json

class AgenteUX:
    """
    Agente especialista en Experiencia de Usuario (UI/UX) y Neuromarketing.
    Su rol es examinar datos duros y complejos, y transformarlos en interfaces, 
    textos y presentaciones que sean visualmente impecables, fáciles de digerir 
    y psicológicamente atractivas para el cliente de Alto Patrimonio.
    """
    
    def __init__(self):
        self.profile_styles = {
            "Conservador": {
                "color_scheme": "#1e3a8a",  # Azul oscuro institucional
                "tone": "protección, legado, seguridad, minimización de riesgos.",
                "ux_focus": "Mostrar gráficos de baja volatilidad primero. Enfatizar blindaje."
            },
            "Agresivo": {
                "color_scheme": "#00B140",  # Verde crecimiento
                "tone": "oportunidad, retorno, vanguardia, outperformance.",
                "ux_focus": "Destacar comparativas de benchmark, alpha generado, charts dinámicos."
            },
            "Modo_Interno": {
                "color_scheme": "#1f2937",  # Gris oscuro
                "tone": "Analítico, directo, accionable.",
                "ux_focus": "KPIs limpios, alertas rojas/verdes, sin texto persuasivo."
            }
        }

    def adaptar_discurso_comercial(self, data_tecnica, perfil_cliente):
        """
        Toma datos técnicos crudos (ej. rentabilidades de la CMF, costos TAC)
        y rediseña la arquitectura de la información (Copywriting UX).
        """
        # Aquí se conectaría la IA Generativa (Gemini/OpenAI) con un prompt maestro.
        style = self.profile_styles.get(perfil_cliente, self.profile_styles["Conservador"])
        
        prompt = f"""
        Como Director de Experiencia de Usuario de un Family Office, 
        toma estos datos técnicos: {data_tecnica}
        
        Reescribe la presentación para un cliente {perfil_cliente}.
        Usa un tono centrado en {style['tone']}.
        El objetivo visual es que la información fluya sin fricción cognitiva.
        """
        
        # Simulación de la respuesta de la IA
        if perfil_cliente == "Conservador":
            return {
                "titulo_sugerido": "Estrategia de Preservación de Capital",
                "layout": "Columnas anchas, tipografía grande, uso de escudos visuales",
                "texto_ux": "Nuestra propuesta estructural reduce la volatilidad protegiendo su patrimonio frente a fluctuaciones abruptas del tipo de cambio..."
            }
        else:
            return {
                "titulo_sugerido": "Aceleración Patrimonial y Captura de Alpha",
                "layout": "Dashboard multitiempo condensado, métricas verdes",
                "texto_ux": "Al optimizar la eficiencia tributaria (TAC), capturamos un delta positivo que acelera la curva de capitalización de su portafolio..."
            }

    def auditar_dashboard(self, view_name):
        """
        El agente evalúa si la interfaz del sistema (para ti o el cliente) 
        está saturada y propone mejoras de usabilidad.
        """
        alertas = []
        if view_name == "Auditoria":
            alertas.append("UX TIP Client-Side: Oculta los datos del NEMOTECNICO del fondo, al cliente solo le importa el nombre comercial y el retorno.")
            alertas.append("UX TIP Advisor-Side: Coloca un botón de 'Agendar Cierre' flotante que siempre sea visible al hacer scroll.")
            
        return alertas

if __name__ == '__main__':
    ux_agent = AgenteUX()
    print("--- PRUEBA AGENTE UX ---")
    data_pesada = {"TAC_actual": 4.5, "TAC_ofrecida": 1.2, "Riesgo_Subjetivo": 12}
    print(json.dumps(ux_agent.adaptar_discurso_comercial(data_pesada, "Conservador"), indent=2, ensure_ascii=False))
