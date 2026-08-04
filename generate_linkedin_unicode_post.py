import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def to_unicode_bold(text):
    res = []
    for char in text:
        code = ord(char)
        if 65 <= code <= 90: # A-Z
            res.append(chr(0x1D5D4 + (code - 65)))
        elif 97 <= code <= 122: # a-z
            res.append(chr(0x1D5EE + (code - 97)))
        elif 48 <= code <= 57: # 0-9
            res.append(chr(0x1D7EC + (code - 48)))
        else:
            res.append(char)
    return ''.join(res)

def convert_markdown_bold_to_unicode(text):
    # Regex to find **text**
    def replace_match(match):
        inner_text = match.group(1)
        return to_unicode_bold(inner_text)
    
    return re.sub(r'\*\*(.*?)\*\*', replace_match, text)

raw_post = """🚨 **REFORMA TRIBUTARIA 2026: 6 Cambios Estratégicos y Oportunidades Clave antes de su Entrada en Vigencia**

La discusión del proyecto de Reforma Tributaria trae ajustes estructurales de alto impacto para **empresas, inversionistas y patrimonios familiares en Chile**.

No se trata solo de una actualización normativa: se abren **ventanas transitorias de oportunidad** que exigen planificación estratégica antes de su entrada en vigencia.

---

🔑 **6 PILARES FUNDAMENTALES QUE DEBES EVALUAR HOY:**

1️⃣ 🏢 **Impuesto de 1ª Categoría (IDPC)**: 
Baja gradual de la tasa corporativa del **27% al 23%** (2027: 25,5% ➔ 2029: 23%). Exige revisar políticas de distribución de dividendos, depreciaciones y aprovechamiento de créditos acumulados en el SAC.

2️⃣ 📈 **Mercado de Capitales (Art. 107 LIR)**: 
Las ganancias en la venta de acciones y cuotas con presencia bursátil **vuelven a ser Ingreso No Renta (0%)** desde enero de 2027, eliminando el impuesto único del 10%. Clave para reestructurar portafolios bursátiles.

3️⃣ 🎁 **Donaciones & Sucesión Familiar**: 
**Ventana transitoria de 1 año con 50% de rebaja** en el Impuesto a las Donaciones y sin insinuación judicial. Una oportunidad histórica para adelantar la sucesión patrimonial a legitimarios de forma ordenada.

4️⃣ 🔄 **Integración Tributaria Total**: 
Se elimina la obligación de restituir el 35% del crédito por IDPC al retirar o remesar utilidades a personas naturales o al extranjero. Reducción directa del costo de liquidez familiar.

5️⃣ 🏠 **Patrimonio Inmobiliario & DFL 2**: 
El beneficio DFL 2 se restringe a las 2 viviendas más antiguas. A contar de la 3ª propiedad, se crea la opción de **Impuesto Único del 5% sobre ingresos brutos sin gastos**. Además, **100% de exención de contribuciones** para la vivienda principal de mayores de 65 años.

6️⃣ 🌐 **Declaración Extraordinaria de Bienes en el Extranjero**: 
Ventana voluntaria de 12 meses para regularizar cuentas, inmuebles, trusts y criptoactivos no declarados mediante un **Impuesto Sustitutivo del 10%** y condonación de intereses/multas.

---

💡 **Conclusión Estratégica**: La oportunidad depende de la historia tributaria y la estructura particular de cada familia o grupo empresarial. Anticipar estos cambios permite maximizar el retorno y proteger el patrimonio acumulado.

💬 **¿Ya estás evaluando el impacto de estas medidas en tus inversiones o estructura societaria?** Conversemos.

---
**Francisco Valencia**  
**Managing Partner | Asesor Financiero Senior**  
📩 contacto@fv-inversiones.com • 📱 +56 9 6677 9662  

#ReformaTributaria #PlanificacionPatrimonial #FamilyOffice #Inversiones #TributariaChile #DFL2 #SucesionFamiliar #BienesRaices #MercadoDeCapitales"""

unicode_post = convert_markdown_bold_to_unicode(raw_post)

with open('linkedin_unicode_post.txt', 'w', encoding='utf-8') as f:
    f.write(unicode_post)

print("POST GENERADO EXITOSAMENTE:")
print(unicode_post)
