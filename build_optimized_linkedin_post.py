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

def get_linkedin_char_count(text):
    # LinkedIn counts UTF-16 code units (surrogate pairs count as 2)
    return len(text.encode('utf-16-le')) // 2

# Post optimizado y conciso
post_text = f"""🚨 {to_unicode_bold('REFORMA TRIBUTARIA 2026: 6 Cambios y Decisiones Clave')}

El proyecto de Reforma Tributaria trae ajustes de alto impacto para {to_unicode_bold('empresas, inversionistas y patrimonios familiares en Chile')}.

Se abren {to_unicode_bold('ventanas transitorias de oportunidad')} que exigen planificación estratégica antes de su entrada en vigencia.

---

🔑 {to_unicode_bold('6 PILARES ESTRATÉGICOS QUE DEBES EVALUAR HOY:')}

1️⃣ 🏢 {to_unicode_bold('Impuesto de 1ª Categoría (IDPC)')}
Baja gradual de la tasa corporativa del {to_unicode_bold('27% al 23%')} (2027: 25,5% ➔ 2029: 23%). Exige revisar cierres tributarios, dividendos y créditos en el SAC.

2️⃣ 📈 {to_unicode_bold('Mercado de Capitales (Art. 107 LIR)')}
Venta de acciones y cuotas con presencia bursátil vuelve a ser {to_unicode_bold('Ingreso No Renta (0%)')} desde enero 2027, eliminando el impuesto único del 10%.

3️⃣ 🎁 {to_unicode_bold('Sucesión & Donaciones')}
{to_unicode_bold('Ventana de 1 año con 50% de rebaja')} en Impuesto a las Donaciones a legitimarios sin insinuación judicial (límite: 50% patrimonio). Oportunidad histórica para planificar la herencia.

4️⃣ 🔄 {to_unicode_bold('Integración Tributaria Total')}
Se elimina la restitución del 35% del crédito por IDPC. Reducción directa del costo efectivo al retirar o remesar utilidades.

5️⃣ 🏠 {to_unicode_bold('Patrimonio Inmobiliario & DFL 2')}
DFL 2 se limita a las 2 viviendas más antiguas. Desde la 3ª, opción de {to_unicode_bold('Impuesto Único del 5% bruto')}. Exención 100% contribuciones para vivienda principal (65+ años).

6️⃣ 🌐 {to_unicode_bold('Activos en el Extranjero')}
Ventana de 12 meses para declarar cuentas, inmuebles, trusts y criptoactivos con {to_unicode_bold('Impuesto Sustitutivo del 10%')} y condonación de intereses y multas.

---

💡 {to_unicode_bold('Conclusión:')} La oportunidad depende de la historia tributaria de cada familia o empresa. Anticipar estos cambios protege tu patrimonio.

💬 {to_unicode_bold('¿Estás evaluando el impacto en tus inversiones o empresas?')} Conversemos.

---
{to_unicode_bold('Francisco Valencia')}
{to_unicode_bold('Managing Partner | Asesor Financiero Senior')}
📩 contacto@fv-inversiones.com • 📱 +56 9 6677 9662

#ReformaTributaria #PlanificacionPatrimonial #FamilyOffice #Inversiones #TributariaChile #DFL2 #SucesionFamiliar #BienesRaices #MercadoDeCapitales"""

count = get_linkedin_char_count(post_text)
limit = 3000
margin = limit - count

print(f"CARACTERES LINKEDIN: {count} / {limit}")
print(f"MARGEN DE SEGURIDAD: +{margin} caracteres libres")

with open('linkedin_unicode_post.txt', 'w', encoding='utf-8') as f:
    f.write(post_text)

# Actualizar el artefacto markdown
artifact_path = r"C:\Users\franc\.gemini\antigravity-ide\brain\e0a740f0-6d0f-448b-98b0-162b61f9b6b0\reforma_tributaria_2026_post.md"
md_content = f"""# 📊 Propuesta de Post para LinkedIn & Infografía 4K: Reforma Tributaria 2026

![Infografía Reforma Tributaria 2026](file:///C:/Users/franc/.gemini/antigravity-ide/brain/e0a740f0-6d0f-448b-98b0-162b61f9b6b0/infografia_reforma_2026.png)

---

## 📋 Copia y Pega Directo en LinkedIn (Verificado: {count} / 3.000 Caracteres - {margin} de margen)

```text
{post_text}
```
"""

with open(artifact_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Artefacto actualizado en: {artifact_path}")
