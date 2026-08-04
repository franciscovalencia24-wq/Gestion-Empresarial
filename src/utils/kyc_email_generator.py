import re

def clean_markdown_formatting(text: str) -> str:
    """
    Limpia símbolos de markdown (** negrita **, `código`, ### títulos) 
    para que al copiar y pegar en Outlook o Gmail el texto quede 100% limpio sin asteriscos ni comillas invertidas.
    """
    if not text:
        return ""
    # Quitar negritas **texto**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Quitar comillas invertidas `codigo`
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Quitar encabezados ### Título
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    return text


def generar_comunicacion_kyc(client_name="Cliente", missing_herederos=True, missing_propiedades=True, missing_polizas=True, advisor_name="Francisco Valencia"):
    """
    Genera el texto limpio (sin asteriscos) de correo electrónico y mensaje de WhatsApp 
    para solicitar los antecedentes KYC generales al cliente.
    """
    c_name = client_name.strip() if client_name else "Estimado/a Cliente"
    first_name = c_name.split()[0] if c_name else "Cliente"
    
    req_bullets = []
    if missing_herederos:
        req_bullets.append("• 👨‍👩‍👧‍👦 Detalle de Herederos y Parentesco: Necesario para auditar distribución legal eficiente, exenciones del Impuesto a la Herencia (Ley N° 16.271) y liquidez sucesoria.")
    if missing_propiedades:
        req_bullets.append("• 🏠 Bienes Raíces y Deudas Hipotecarias: Indispensable para calcular patrimonio neto consolidado, avalúos en UF y planificar optimización tributaria.")
    if missing_polizas:
        req_bullets.append("• 🛡️ Pólizas de Vida y APV: Requerido para auditar inembargabilidad de fondos y maximizar beneficios tributarios (Art. 57 LIR, Art. 42 bis LIR).")
        
    if not req_bullets:
        req_bullets = ["• 📋 Antecedentes de Identificación y Estructura Patrimonial: Requerido para la consolidación general del informe 360°."]
        
    bullets_text = "\n".join(req_bullets)
    
    clean_client_file = c_name.replace(' ', '_')
    asunto = f"Planificación Patrimonial & Onboarding 360° — Antecedentes y Formulario KYC | {c_name}"
    
    cuerpo_email = f"""Estimado/a {c_name},

Espero que se encuentre muy bien.

En el marco de nuestro proceso de asesoría patrimonial integral y con el objetivo de estructurar una estrategia a la medida de sus metas financieras y familiares, le escribo para hacerle entrega de los documentos de recopilación de antecedentes iniciales (KYC - Know Your Customer).

Adjunto a este correo encontrará dos archivos clave:
1. 📄 Manual de Recopilación Patrimonial (PDF): Documento guía con la explicación normativa y el enfoque de la auditoría 360°.
2. 📊 Formulario de Registro Patrimonial (Altus_KYC_{clean_client_file}.xlsx): Planilla estructurada en Excel para completar la información solicitada.

----------------------------------------------------------------------
💡 ¿POR QUÉ ES FUNDAMENTAL COMPLETAR ESTOS ANTECEDENTES?

Entendemos que reunir estos datos requiere de su valioso tiempo. Sin embargo, este ejercicio es el insumo indispensable para que nuestro motor de inteligencia Altus AI y nuestro equipo analítico puedan:

{bullets_text}

----------------------------------------------------------------------
✍️ INDICACIONES PARA EL COMPLETADO DEL EXCEL:

Al abrir la planilla adjunta, encontrará la columna destacada en azul: "Respuesta / Detalle del Cliente (Escribir aquí)".
📌 Le agradeceremos ingresar los datos específicos solicitados (nombres completos, RUT, roles, montos de deudas o seguros). Por favor evite responder únicamente "Sí" o "De acuerdo", ya que requerimos los datos reales para alimentar los modelos de cálculo.

----------------------------------------------------------------------
🔒 CONFIDENCIALIDAD Y MARCO LEGAL:

Toda la información que nos comparta está resguardada bajo estricto Secreto Patrimonial, amparada por la Ley N° 19.628 sobre Protección de la Vida Privada y protegida con cifrado de grado bancario (AES-256). Asimismo, conforme a la Ley N° 19.799, el envío de este formulario desde su casilla de correo constituye una Firma Electrónica Simple (FES) válida.

Quedo a su entera disposición para resolver cualquier inquietud o asistirle en el completado. Puede responder a este mismo correo adjuntando la planilla una vez lista.

Agradeciendo de antemano su confianza, le saluda atentamente,

-- 
{advisor_name}
Managing Partner / Asesor Patrimonial Senior
FV Asesorías e Inversiones & Altus AI
📧 contacto@fv-inversiones.com | 📱 WhatsApp: +56 9 6677 9662"""

    mensaje_whatsapp = f"""Hola {first_name}, espero que estés muy bien. 

Te acabo de enviar un correo formal con el Manual y el Formulario Excel KYC para nuestro proceso de Auditoría Patrimonial 360°. 

Ahí te detallo los aspectos clave para la optimización tributaria y de sucesión, y la guía para completarlo fácilmente. Quedo atento a tus comentarios por esa vía o si necesitas que revisemos algún punto juntos. ¡Un saludo cordial!"""

    return {
        "asunto": clean_markdown_formatting(asunto),
        "cuerpo_email": clean_markdown_formatting(cuerpo_email),
        "mensaje_whatsapp": clean_markdown_formatting(mensaje_whatsapp)
    }


def generar_comunicacion_apv_reliquidacion(client_name="José González Daza", advisor_name="Francisco Valencia"):
    """
    Genera el texto de correo y WhatsApp limpio (sin asteriscos) enfocado específicamente
    en la meta del cliente: Aporte Mensual APV + Simulador APV Inteligente + Simulador de Reliquidación IGC.
    """
    c_name = client_name.strip() if client_name else "José González Daza"
    first_name = c_name.split()[0] if c_name else "José"
    clean_file_name = f"Formulario_APV_Reliquidacion_{c_name.replace(' ', '_')}.xlsx"
    
    asunto = f"Planificación APV & Optimización Tributaria (Reliquidación IGC) | {c_name}"
    
    cuerpo_email = f"""Estimado/a {first_name},

Un gusto haber conversado con usted el día de hoy.

Conforme a lo conversado y respondiendo a su objetivo de estructurar un APORTE MENSUAL DE APV (Ahorro Previsional Voluntario) de forma óptima, le escribo para solicitarle algunos antecedentes clave.

Para entregarle un análisis verdaderamente personalizado y de alto valor, procesaremos sus datos a través de dos de nuestros simuladores patrimoniales de última generación:

1. 🎯 SIMULADOR "APV INTELIGENTE": Evaluará de forma exacta si a su nivel de renta le conviene optar por el Régimen A (Bonificación Estatal directa del 15% sobre lo aportado) o el Régimen B (Rebaja directa en su impuesto a la renta IGC), optimizando la rentabilidad neta de su aporte mensual.

2. 🔄 SIMULADOR "RELIQUIDACIÓN DE IMPUESTOS IGC": Calculará el potencial de devolución de impuestos anual a su favor por concepto de reliquidación de sueldos (Art. 47 y 52 bis LIR), rebaja por dividendos hipotecarios (Art. 55 bis) y crédito por gastos en educación de sus hijos (Art. 55 ter).

----------------------------------------------------------------------
📋 ANTECEDENTES REQUERIDOS (Adjuntos en la planilla {clean_file_name}):

Para poder correr las simulaciones con precisión de peso, requerimos los siguientes datos:
• 👨‍👩‍👧‍👦 Datos de la Cónyuge: Nombre completo, RUT, fecha de nacimiento y si percibe ingresos independientes o renta imponible.
• 👶 Detalle de Hijos (Cargas de Familia): Nombres completos, RUT, fechas de nacimiento y si están estudiando (colegio/universidad) para aplicar la rebaja por gastos en educación (Art. 55 ter LIR).
• 💰 Renta Bruta / Sueldo Líquido Mensual Aproximado: Para definir el tramo exacto del Impuesto Global Complementario (entre 4% y 40%).
• 📊 Monto de Aporte Mensual APV Deseado: El monto estimado en CLP o UF que proyecta ahorrar mensualmente.
• 🛡️ APV Actual (Si aplica): Institución donde lo mantiene (ej. Principal), régimen actual y saldo aproximado.

----------------------------------------------------------------------
✍️ INDICACIONES PARA EL LLENADO DEL EXCEL:

Adjunto a este correo encontrará la planilla estructurada {clean_file_name}.
Solo debe ingresar los antecedentes en la columna destacada en azul: "Respuesta / Detalle del Cliente (Escribir aquí)".

----------------------------------------------------------------------
🔒 CONFIDENCIALIDAD Y MARCO LEGAL:

Le garantizamos que todos sus datos están protegidos bajo Secreto Patrimonial, amparados por la Ley N° 19.628 sobre Protección de la Vida Privada y almacenados bajo cifrado de grado bancario (AES-256). Conforme a la Ley N° 19.799, la respuesta a este correo desde su casilla personal constituye una Firma Electrónica Simple (FES) válida.

Quedo a su completa disposición para cualquier consulta. Una vez que nos envíe estos datos, le entregaremos el informe comparativo completo con la proyección de su aporte mensual APV y el cálculo de reliquidación.

Le saluda muy atentamente,

-- 
{advisor_name}
Managing Partner / Asesor Patrimonial Senior
FV Asesorías e Inversiones & Altus AI
📧 contacto@fv-inversiones.com | 📱 WhatsApp: +56 9 6677 9662"""

    mensaje_whatsapp = f"""Hola {first_name}, excelente haber conversado hoy contigo. 

Te acabo de enviar un correo enfocado en tu Aporte Mensual de APV. Para correr nuestros dos simuladores (APV Inteligente para ver si te conviene Régimen A o B, y el de Reliquidación de Impuestos para ver devoluciones a tu favor), te adjunté una planilla breve solicitando datos clave (cónyuge, hijos, fechas de nac. y renta aprox.).

Quedo muy atento por esa vía para correr las simulaciones y entregarte la propuesta optimizada. ¡Un abrazo!"""

    return {
        "asunto": clean_markdown_formatting(asunto),
        "cuerpo_email": clean_markdown_formatting(cuerpo_email),
        "mensaje_whatsapp": clean_markdown_formatting(mensaje_whatsapp)
    }
