def to_bold_unicode(text):
    result = []
    for char in text:
        if 'A' <= char <= 'Z':
            result.append(chr(ord(char) - ord('A') + 0x1D5D4))
        elif 'a' <= char <= 'z':
            result.append(chr(ord(char) - ord('a') + 0x1D5EE))
        elif '0' <= char <= '9':
            result.append(chr(ord(char) - ord('0') + 0x1D7EC))
        else:
            result.append(char)
    return ''.join(result)

text = f'''¿Sabías que la {to_bold_unicode("Megarreforma 2026 (Ley de Reconstrucción)")} abre una ventana temporal única para blindar y reestructurar tu patrimonio? 🏛️💼

Esta nueva ley trae consigo {to_bold_unicode("4 cambios radicales")} que afectarán tus inversiones si no te preparas con anticipación. En la oficina hemos hecho un análisis profundo de lo que esto significa para patrimonios de inversión y hemos preparado esta infografía para ti. 👇

🔑 Aquí te resumo los {to_bold_unicode("4 pilares fundamentales")} de la nueva ley que debes conocer hoy:

1️⃣ {to_bold_unicode("Repatriación de Capitales (Tasa Histórica):")} Se habilita una ventana de regularización con un impuesto del 10%. ¿El gran incentivo? Si mantienes esos fondos invertidos en Chile por 8 años en instrumentos estratégicos (como propiedades DFL2 o Art. 107), ¡la tasa baja a un 7%!

2️⃣ {to_bold_unicode("Ley de Donaciones (Herencia en Vida):")} Una medida sumamente disruptiva. Por solo 1 año, habrá una rebaja transitoria del 50% al Impuesto a las Donaciones para el círculo familiar directo, liberándote además del lento trámite judicial de insinuación. Es el momento perfecto para la planificación sucesoria.

3️⃣ {to_bold_unicode("Nuevo Régimen para Propiedades DFL2:")} Se elimina el antiguo límite de 2 viviendas favorecidas. Ahora, desde la tercera vivienda DFL2 en adelante (hasta 90m2), los rentistas inmobiliarios pagarán un Impuesto Único Fijo del 5% sobre el ingreso de los arriendos. Un escenario inmejorable para escalar tu portafolio de renta.

4️⃣ {to_bold_unicode("Exención Artículo 107 LIR:")} Las ganancias de capital, combinadas con los incentivos de la ley, abren la puerta a estructurar tu capital a través de Administradoras locales institucionales. La selección del fondo adecuado hoy es más crítica que nunca para maximizar tu rentabilidad neta libre de impuestos.

💡 {to_bold_unicode("El peor error patrimonial es la inacción.")} Estas ventanas de oportunidad son estrictamente temporales.

👇 Guarda y comparte la infografía adjunta. ¿Tienes dudas de cómo aplicar estas ventajas fiscales a tu portafolio personal o familiar? Escríbeme por mensaje directo y conversemos.

#Megarreforma #LeyDeReconstruccion #PlanificacionPatrimonial #InversionesChile #Tributacion #WealthManagement
'''

with open('post_linkedin.txt', 'w', encoding='utf-8') as f:
    f.write(text)

import shutil
shutil.copy2('post_linkedin.txt', r'C:\Users\franc\.gemini\antigravity-ide\brain\e0a740f0-6d0f-448b-98b0-162b61f9b6b0\post_linkedin.txt')
print("Hecho")
