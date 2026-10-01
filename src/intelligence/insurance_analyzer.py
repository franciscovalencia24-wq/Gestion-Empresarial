import os
import base64
import filetype
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class InsurancePolicyAnalyst:
    """
    Analista de Pólizas de Seguro (Vida, Salud, Oncológico, etc).
    Lee PDFs extensos y extrae el resumen de costos, beneficios y letra chica.
    """
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            # flash es excelente para lectura rápida de documentos largos (hasta 1M tokens)
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                temperature=0.1, 
                google_api_key=self.api_key
            )
        else:
            self.llm = None

    def analyze_policy(self, file_bytes: bytes, filename: str) -> dict:
        if not self.llm:
            raise Exception("Falta GOOGLE_API_KEY")

        print(f"[InsuranceAnalyst] Analizando póliza: {filename}")
        
        # Determinar mime_type
        kind = filetype.guess(file_bytes)
        mime_type = kind.mime if kind else "application/pdf"
        
        content_parts = []
        
        prompt = """
        Eres un Abogado y Actuario experto en Seguros en Chile.
        He adjuntado el documento completo de una póliza de seguro (puede ser vida, salud, oncológico, APV, vehículos o general).
        
        Tu trabajo es leer atentamente el contrato y extraer EXACTAMENTE la siguiente información clave, ignorando la burocracia comercial. 
        Si un dato no existe, responde "No especificado".
        
        ESTRUCTURA OBLIGATORIA DE LA RESPUESTA:
        
        **TIPO DE SEGURO Y COMPAÑÍA:** [Ej: Seguro Complementario de Salud - MetLife]
        **NÚMERO DE PÓLIZA:** [Si lo encuentras]
        **PRIMA MENSUAL/ANUAL:** [Costo que paga el cliente]
        **CAPITAL ASEGURADO O TOPE MÁXIMO:** [Ej: UF 500, USD 100.000]
        **DEDUCIBLE:** [Ej: UF 50 por evento]
        
        **BENEFICIOS CLAVE:**
        - [Beneficio 1]
        - [Beneficio 2]
        
        **EXCLUSIONES CRÍTICAS (La Letra Chica):**
        - [Lo que NO cubre]
        - [Enfermedades preexistentes, plazos de carencia, etc.]
        
        **COMENTARIO DEL ASESOR (Opcional):** [Si notas algo inusualmente malo o bueno en esta póliza, menciónalo aquí brevemente].
        """
        
        content_parts.append({"type": "text", "text": prompt})
        
        if mime_type.startswith("text/"):
            try:
                text_content = file_bytes.decode('utf-8', errors='ignore')
                content_parts.append({"type": "text", "text": f"\n\nCONTENIDO DE LA PÓLIZA:\n{text_content}"})
            except:
                pass
        else:
            file_b64 = base64.b64encode(file_bytes).decode("utf-8")
            if mime_type == "application/pdf" or mime_type.startswith("image/"):
                content_parts.append({
                    "type": "media" if mime_type == "application/pdf" else "image_url",
                    "mime_type": mime_type,
                    "data": file_b64,
                } if mime_type == "application/pdf" else {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{file_b64}"}
                })

        try:
            message = HumanMessage(content=content_parts)
            response = self.llm.invoke([message])
            return response.content
        except Exception as e:
            raise Exception(f"Error analizando póliza: {str(e)}")

    def analyze_cmf_coberturas(self, tipo_seguro: str, coberturas: str) -> str:
        if not self.llm:
            return "Análisis IA no disponible (Falta GOOGLE_API_KEY)"
            
        if not coberturas or len(coberturas.strip()) < 10:
            return "Información insuficiente para análisis detallado."
            
        prompt = f"""
        Eres un Abogado y Actuario experto en Seguros en Chile.
        Te entregaré las cláusulas técnicas extraídas del portal CMF (Conoce Tu Seguro) para una póliza.
        
        TIPO DE SEGURO PRINCIPAL: {tipo_seguro}
        CLÁUSULAS TÉCNICAS (Letra Chica):
        {coberturas}
        
        Tu objetivo es traducir esta jerga técnica en un "Resumen Comercial y Diagnóstico" corto y directo (máximo 4-5 líneas) para un Asesor Financiero.
        
        ESTRUCTURA DE RESPUESTA REQUERIDA (Responde solo esto):
        - **Diagnóstico:** [¿Es una cobertura robusta, básica, o tiene vacíos importantes?]
        - **Cubre:** [Lo más importante que cubre]
        - **Falta/Alerta:** [Lo que NO cubre según las cláusulas, o vacíos típicos de este tipo de seguros que el cliente debería contratar aparte].
        - **Oportunidad Comercial:** [¿Qué producto le podrías hacer up-sell o cross-sell basado en esto? (ej: "Ofrecer Seguro Catastrófico de Salud", "Ofrecer Sismo")].
        """
        
        try:
            message = HumanMessage(content=[{"type": "text", "text": prompt}])
            response = self.llm.invoke([message])
            return response.content
        except Exception as e:
            return f"Error en IA: {str(e)}"

def auditar_polizas_cliente(prospect_id: int, db_session) -> dict:
    from src.database.models import Prospect
    from src.osint.indicadores import get_uf_today
    import json
    
    prospect = db_session.query(Prospect).filter_by(id=prospect_id).first()
    if not prospect:
        return {}

    uf_val = get_uf_today()
    
    capital_vida_uf = 0.0
    polizas_analizadas = []
    
    # Análisis de Cartera
    total_polizas = 0
    total_cautivas = 0
    micro_polizas_bancarias = []
    
    for pol in prospect.insurances:
        if pol.estado != "VIGENTE":
            continue
            
        total_polizas += 1
        tipo = (pol.tipo_seguro or "").lower()
        contratante = (pol.contratante or "").lower()
        
        is_captive = "banco" in contratante or "cencosud" in contratante or "falabella" in contratante or "ripley" in contratante or "cmr" in contratante or "banchile" in contratante or "scotiabank" in contratante or "itau" in contratante or "bci" in contratante or "santander" in contratante or "estado" in contratante
        if is_captive:
            total_cautivas += 1
            if "desgravamen" in tipo or "fraude" in tipo or "robo" in tipo or "robo" in (pol.coberturas or "").lower():
                micro_polizas_bancarias.append(f"{pol.compania} ({pol.tipo_seguro})")
                
        if "vida" in tipo or "desgravamen" in tipo:
            capital_vida_uf += pol.capital_asegurado
            
        destino_beneficio = "Acreedor Financiero" if ("desgravamen" in tipo or is_captive and "vida" not in tipo) else "Familia / Herederos"
        if "vida individual" in tipo.lower() and not is_captive:
            destino_beneficio = "Familia / Herederos"
        elif "vida" in tipo.lower() and is_captive:
            # Often banks sell life insurance, but it usually goes to them or is a rigid product
            destino_beneficio = "Acreedor / Familia (Mixto)"
            
        polizas_analizadas.append({
            "compania": pol.compania,
            "contratante": pol.contratante,
            "tipo": pol.tipo_seguro,
            "capital_uf": pol.capital_asegurado,
            "prima_mensual": pol.prima_mensual,
            "es_apv": pol.es_apv_poliza,
            "estado": pol.estado,
            "destino_beneficio": destino_beneficio
        })
            
    capital_vida_clp = capital_vida_uf * uf_val
    
    # Pasivos (Deuda Hipotecaria Total)
    deuda_total_clp = sum(d.monto_actual for d in prospect.debts)
    for prop in prospect.properties:
        deuda_total_clp += prop.deuda_hipotecaria
        
    deuda_total_uf = deuda_total_clp / uf_val if uf_val > 0 else 0
    
    # Cobertura Real Familiar (Ignoramos Desgravamen para liquidez familiar)
    liquidez_familiar_uf = 0.0
    for p in polizas_analizadas:
        if "desgravamen" not in p["tipo"].lower() and "Familia" in p["destino_beneficio"]:
            liquidez_familiar_uf += p["capital_uf"]
            
    liquidez_familiar_clp = liquidez_familiar_uf * uf_val
    
    porcentaje_cautivas = (total_cautivas / total_polizas * 100) if total_polizas > 0 else 0
    
    # Brecha Sucesoria
    brecha_sucesoria_clp = 0.0
    if prospect.profile and prospect.profile.flujo_sucesorio:
        try:
            flujo_data = json.loads(prospect.profile.flujo_sucesorio)
            flujo_neto = flujo_data.get("flujo_caja_mensual_neto", 0)
            if flujo_neto < 0:
                brecha_sucesoria_clp = abs(flujo_neto * 12) / 0.04
        except Exception:
            pass
            
    if brecha_sucesoria_clp == 0 and prospect.gastos_recurrentes > 0:
         brecha_sucesoria_clp = prospect.gastos_recurrentes / 0.04  # Asumiendo anual
         
    brecha_sucesoria_uf = brecha_sucesoria_clp / uf_val if uf_val > 0 else 0
    
    deficit_sucesorio_clp = brecha_sucesoria_clp - liquidez_familiar_clp
    deficit_sucesorio_uf = deficit_sucesorio_clp / uf_val if uf_val > 0 else 0
    
    tiene_deficit = deficit_sucesorio_clp > 0
    
    # Dictamen Estructurado
    diag_proteccion = f"El {porcentaje_cautivas:.0f}% de las pólizas vigentes son cautivas de acreedores financieros. "
    if liquidez_familiar_uf == 0:
        diag_proteccion += "Cobertura líquida para herederos: $0 CLP (100% cautiva de acreedores financieros). Riesgo de Liquidez Sucesoria crítico."
    else:
        diag_proteccion += f"Cobertura líquida real para la familia: {liquidez_familiar_uf:,.0f} UF."
        
    diag_duplicidad = "No se detecta dispersión significativa."
    if len(micro_polizas_bancarias) > 1:
        diag_duplicidad = f"Se detecta acumulación ineficiente de {len(micro_polizas_bancarias)} micro-pólizas bancarias/retail (ej. {', '.join(micro_polizas_bancarias[:2])})."
        
    if tiene_deficit or liquidez_familiar_uf == 0:
        dictamen_comercial = f"Proponer la desintermediación de seguros bancarios mediante pólizas individuales endosables de menor prima. Recomendar la contratación de un Seguro de Vida con Ahorro Preferente en PRINCIPAL (Art. 17 N°8 / 42 bis) que cubra la Brecha Patrimonial Sucesoria al 4% (sugerido: {brecha_sucesoria_uf:,.0f} UF)."
    else:
        dictamen_comercial = "Revisar eficiencia tributaria y costos de primas de las pólizas actuales. Consolidar en Seguro APV PRINCIPAL para maximizar rebaja de IGC."

    return {
        "polizas": polizas_analizadas,
        "capital_vida_total_uf": capital_vida_uf,
        "capital_vida_total_clp": capital_vida_clp,
        "deuda_total_uf": deuda_total_uf,
        "deuda_total_clp": deuda_total_clp,
        "liquidez_familiar_uf": liquidez_familiar_uf,
        "liquidez_familiar_clp": liquidez_familiar_clp,
        "brecha_sucesoria_uf": brecha_sucesoria_uf,
        "brecha_sucesoria_clp": brecha_sucesoria_clp,
        "deficit_sucesorio_uf": deficit_sucesorio_uf if tiene_deficit else 0,
        "deficit_sucesorio_clp": deficit_sucesorio_clp if tiene_deficit else 0,
        "tiene_deficit": tiene_deficit,
        "porcentaje_cautivas": porcentaje_cautivas,
        "diag_proteccion": diag_proteccion,
        "diag_duplicidad": diag_duplicidad,
        "dictamen": dictamen_comercial,
        "recomendacion": dictamen_comercial
    }

