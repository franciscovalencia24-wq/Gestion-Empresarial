import os
from datetime import datetime
import json
import google.generativeai as genai
from dotenv import load_dotenv
from src.database.connection import SessionLocal
from src.database.models import MarketVision

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class MacroAnalystAgent:
    """
    Agente Macroeconómico que centraliza las visiones de mercado leyendo la Base de Datos Temporal.
    """
    def __init__(self):
        if api_key:
            # Imponer temperatura 0.1 para forzar anclaje a los datos crudos (anti-alucinaciones)
            self.model = genai.GenerativeModel("gemini-2.5-pro", generation_config=genai.types.GenerationConfig(temperature=0.1))
        else:
            self.model = None

    def ingest_document_vision(self, institucion: str, periodo: str, text_content: str = "", file_path: str = "", is_multimodal: bool = False) -> str:
        """
        Ingesta un Documento (PDF/PPTX) manual a la base de datos temporal.
        Soporta modo texto y modo Multimodal (para leer gráficos como en JP Morgan).
        Maneja actualizaciones intra-mes acumulativas (ej. Advisors Talks semanales).
        """
        if not self.model:
            return "Error: GOOGLE_API_KEY no configurada."

        # Revisar si ya existe una visión para este mes (Memoria Acumulativa)
        db = SessionLocal()
        vision = db.query(MarketVision).filter_by(institucion=institucion, periodo=periodo).first()
        contexto_previo = ""
        
        if vision and vision.resumen_extendido:
            contexto_previo = f"\n\nATENCIÓN: Ya teníamos un registro previo de esta institución este mes. Este es el registro existente:\n{vision.resumen_extendido}\n\nTu tarea es MANTENER esa información base y SUMAR/ACTUALIZAR con los nuevos datos que te paso a continuación. Explícitamente indica 'Actualización Intra-mes:' si la postura cambió."
        
        prompt = f"""
        Eres un analista macroeconómico de élite. Analiza la visión de mercado de {institucion} para el período {periodo}.
        {contexto_previo}
        
        """
        if not is_multimodal:
            prompt += f"AQUÍ ESTÁ EL NUEVO TEXTO DEL REPORTE:\n{text_content[:15000]}\n"
        else:
            prompt += "El documento original (PDF/PPTX) ha sido adjuntado. Por favor, lee cuidadosamente el texto y sobre todo INTERPRETA LOS GRÁFICOS E IMÁGENES complejas para extraer las conclusiones tácticas.\n"
            
        prompt += """
        OBJETIVO:
        1. VALIDADOR DE PERÍODO: Verifica si el documento aportado corresponde realmente al período esperado ({periodo}). Si el texto indica claramente ser de un mes/año distinto (ej. Julio, Trimestre anterior), debes indicarlo.
        2. Resume la visión corta (1 párrafo contundente). Si el período es incorrecto o desactualizado, inicia el resumen diciendo: "[⚠️ ALERTA: Este documento parece ser de <mes encontrado> y no de {periodo}] ".
        3. Escribe el resumen extendido (Renta Fija, Variable, Alternativos). Si es una actualización intra-mes, asegúrate de indicarlo en el texto.
        
        Responde ÚNICAMENTE con un JSON válido con esta estructura:
        {
            "resumen_corto": "...",
            "resumen_extendido": "..."
        }
        """
        
        try:
            if is_multimodal and file_path:
                # Subir archivo a Gemini para visión multimodal
                import google.generativeai as genai
                uploaded_file = genai.upload_file(path=file_path)
                resp = self.model.generate_content([uploaded_file, prompt])
                # Limpiar archivo en Google Cloud
                genai.delete_file(uploaded_file.name)
            else:
                resp = self.model.generate_content(prompt)
                
            texto = resp.text.strip()
            if texto.startswith("```json"): texto = texto[7:]
            if texto.endswith("```"): texto = texto[:-3]
            data = json.loads(texto.strip())
            
            if vision:
                vision.fuente = "Documento Actualizado"
                vision.contenido_bruto = (vision.contenido_bruto or "") + "\n\n--- NUEVO APORTE ---\n" + (text_content[:5000] if not is_multimodal else "[Aporte Multimodal - JP Morgan]")
                vision.resumen_corto = data.get("resumen_corto")
                vision.resumen_extendido = data.get("resumen_extendido")
                vision.fecha_ingesta = datetime.utcnow()
            else:
                vision = MarketVision(
                    institucion=institucion,
                    periodo=periodo,
                    fuente="Documento",
                    contenido_bruto=text_content[:5000] if not is_multimodal else "[Aporte Multimodal - JP Morgan]",
                    resumen_corto=data.get("resumen_corto"),
                    resumen_extendido=data.get("resumen_extendido")
                )
                db.add(vision)
                
            db.commit()
            db.close()
            return f"✅ Visión de {institucion} ({periodo}) procesada y guardada correctamente."
        except Exception as e:
            return f"❌ Error al procesar IA: {e}"

    def generate_monthly_consolidation(self, periodo: str) -> str:
        """
        Genera el Consenso de Mercado leyendo los resúmenes de la DB para un período específico.
        """
        if not self.model:
            return "Error: GOOGLE_API_KEY no configurada."

        db = SessionLocal()
        visiones = db.query(MarketVision).filter(
            MarketVision.periodo == periodo,
            MarketVision.institucion != "Consenso IA"
        ).all()
        db.close()

        if not visiones:
            return f"No hay reportes institucionales registrados para el período {periodo}."

        datos_crudos = ""
        for v in visiones:
            datos_crudos += f"\n--- {v.institucion} ({v.fuente}) ---\nRESUMEN CORTO:\n{v.resumen_corto}\nRESUMEN EXTENDIDO:\n{v.resumen_extendido}\n"

        prompt = f"""
        Eres el sistema analítico 'Altus AI' de un Family Office Privado.
        
        A continuación te presento las visiones de mercado de {len(visiones)} instituciones correspondientes al período {periodo}:
        
        {datos_crudos}
        
        TU MISIÓN:
        Genera el "Consenso Institucional de Mercado" definitivo para este período basándote EXCLUSIVAMENTE en el texto anterior.
        
        REGLAS ANTI-ALUCINACIÓN Y DE PRIVACIDAD (CRÍTICO):
        - Tienes ESTRICTAMENTE PROHIBIDO inventar o asumir posturas que no estén expresamente escritas en los resúmenes anteriores.
        - Si no hay información suficiente sobre un activo o mercado en los reportes provistos, simplemente omítelo.
        - DEBES ANONIMIZAR totalmente a las instituciones. NUNCA menciones nombres propios de bancos, corredoras o AGFs en el texto. En su lugar, utiliza estadísticas, fracciones o consensos abstractos (ejemplo: "El 65% de las instituciones analizadas sugiere...", "Dos de los grandes bancos de inversión locales advierten...", "Existe un consenso mayoritario en...").
        
        ESTRUCTURA OBLIGATORIA:
        Al inicio del documento incluye el siguiente texto en cursiva: "*Análisis basado en las recomendaciones mensuales de {len(visiones)} instituciones.*"
        
        1. **Visión Global y Local**: Resumen de lo que opina la industria sobre tasas, inflación y crecimiento (con foco en la visión de las instituciones chilenas).
        2. **Consenso por Tipo de Activo**:
           - Renta Variable Local e Internacional
           - Renta Fija Local e Internacional
           - Activos Alternativos / Commodities
        3. **Sugerencia de Portafolio por Perfil de Riesgo**:
           - **Conservador:** Qué % asignar a cada activo.
           - **Moderado:** Qué % asignar a cada activo.
           - **Agresivo/Arriesgado:** Qué % asignar a cada activo.
        
        Usa formato Markdown profesional. No inventes datos que no estén en el texto provisto.
        CRÍTICO: Tu respuesta DEBE comenzar estrictamente con el texto en cursiva indicado, y luego el símbolo numeral (#) para el primer título. NO uses encabezados de tipo "De: / Para: / Asunto:".
        Si incluyes un subtítulo de autor, DEBE decir EXACTAMENTE: "**Preparado por:** Altus AI". (NUNCA uses la palabra Macro ni el título Economista Jefe).
        NUNCA digas "Absolutamente" ni saludes.
        """

        try:
            response = self.model.generate_content(prompt)
            consenso_texto = response.text
            
            # Limpiar cualquier saludo terco que la IA haya puesto antes del primer título
            if "#" in consenso_texto:
                consenso_texto = consenso_texto[consenso_texto.find("#"):]
            
            # Guardar/Actualizar en DB para memoria a largo plazo
            try:
                db_save = SessionLocal()
                existing_c = db_save.query(MarketVision).filter_by(institucion="Consenso IA", periodo=periodo).first()
                if existing_c:
                    existing_c.resumen_extendido = consenso_texto
                    existing_c.fecha_ingesta = datetime.now()
                else:
                    new_c = MarketVision(
                        institucion="Consenso IA",
                        periodo=periodo,
                        fuente="Altus AI Engine",
                        resumen_corto="Consenso Institucional Definitivo del Mes",
                        resumen_extendido=consenso_texto,
                        fecha_ingesta=datetime.now()
                    )
                    db_save.add(new_c)
                db_save.commit()
                db_save.close()
            except Exception as e_save:
                pass

            return consenso_texto
        except Exception as e:
            return f"Error en el LLM: {e}"

    def answer_macro_query(self, query: str, context: str = "", client_rut: str = None) -> str:
        if not self.model:
            return "Error: API_KEY no configurada."
            
        client_context = ""
        if client_rut:
            try:
                from src.database.models import Prospect
                db = SessionLocal()
                prospect = db.query(Prospect).filter(Prospect.rut == client_rut).first()
                if prospect and prospect.profile:
                    client_context = f"\n\nContexto Psicológico e Intereses del Cliente:\n{prospect.profile.notas_neuroventas or 'No hay notas.'}\n\nTipo de Cliente: {prospect.profile.tipo_persona}\n"
                db.close()
            except Exception as e:
                pass
            
        prompt = f"""
        Eres 'Altus AI Macro', un asesor macroeconómico. 
        Un cliente te hace la siguiente consulta: "{query}"
        {client_context}
        Contexto adjunto (opcional):
        {context}
        
        Responde la duda de forma estructurada, profesional, citando el contexto adjunto si es pertinente.
        Si hay 'Contexto Psicológico e Intereses del Cliente', ajusta el tono, los ejemplos o las analogías de tu respuesta para que resuenen fuertemente con la neurociencia de sus miedos o intereses específicos.
        IMPORTANTE: No firmes el reporte como IA (ej. no pongas "Altus AI" ni tu nombre al final). Despídete formalmente pero deja el espacio en blanco para que el Asesor Humano firme con su propio nombre.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {e}"
