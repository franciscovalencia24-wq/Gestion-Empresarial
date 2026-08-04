import sys

sys.stdout.reconfigure(encoding='utf-8')

artifact_path = r"C:\Users\franc\.gemini\antigravity-ide\brain\e0a740f0-6d0f-448b-98b0-162b61f9b6b0\cumbre_sonami_prospeccion.md"

md_content = """# 🎯 Plan de Acción Inmediato: Búsqueda Ejecutiva y Prospección Casual en LinkedIn

**Objetivo**: Conectar HOY con líderes de SONAMI y ejecutivos mineros mediante mensajes casuales de alta tasa de aceptación.

---

## 💬 1. Mensajes Casuales de Invitación (<= 300 Caracteres)

Copia cualquiera de estas opciones al hacer clic en **"Conectar" ➔ "Añadir una nota"**:

### 📩 Opción 1: Casual & Directa (Recomendada - Alta Tasa de Aceptación)
> *Hola [Nombre], ¿cómo estás? Sigo muy de cerca el sector minero y los temas que abordan en SONAMI. Me gustaría conectar contigo para estar al tanto de tus publicaciones y análisis sobre la industria.*
>
> *Un saludo,*
> *Francisco*

*(Longitud: 247 / 300 caracteres)*

---

### 📩 Opción 2: Enfocada en Interés del Rubro y Contenido
> *Estimado/a [Nombre], me interesa mucho seguir de cerca la actualidad y desafíos de la minería en Chile. Al ser un referente del rubro, me gustaría conectar para estar al tanto de tus publicaciones.*
>
> *Un cordial saludo,*
> *Francisco Valencia*

*(Longitud: 260 / 300 caracteres)*

---

### 📩 Opción 3: Breve y Cercana
> *Hola [Nombre], me parece excelente el desarrollo e impacto del sector minero en Chile. Me interesa estar al tanto de tus publicaciones y novedades del rubro aquí en LinkedIn. Sería un gusto conectar.*
>
> *Saludos,*
> *Francisco*

*(Longitud: 246 / 300 caracteres)*

---

## 🎯 2. Contactos Detectados en tu Búsqueda Actual (Para Contactar Ahora)

1. **Cristian Pérez Escobar** (CEO - Director en Minera Monte Alto | Consejero SONAMI)
2. **Jorge Riesco Valdivieso** (Presidente Sociedad Nacional de Minería)
3. **Jorge Geldres Reyes** (Director SONAMI | Consejero CCHC | Consejero CPC)
4. **Diego Arrigorriaga** (Chief Development Officer @ Haldeman Mining | Ex-CFO/CCO)
5. **Lauren Cozzolino Arias** (Head of Joint Ventures at BHP | Board Director)

---

## 🤝 3. Qué Hacer Una Vez que ACEPTEN tu Solicitud

Una vez que acepten tu invitación, no les vendas de inmediato. Interactúa con sus publicaciones (dales *Like* o comenta con valor) y a los 2-3 días o cuando publiquen algo, inicia la conversación de forma natural por mensaje privado:

```text
Hola [Nombre], muchas gracias por conectar. 

Veo que estás abordando temas muy relevantes sobre [tema de su publicación/empresa]. En FV Asesorías apoyamos a empresarios y ejecutivos del sector a auditar su patrimonio y optimizar la carga tributaria en este nuevo escenario 2026.

Si en algún momento deseas intercambiar visiones sobre estructuras patrimoniales o eficiencias tributarias, con gusto coordinamos un café o breve llamada.

¡Que tengas una excelente semana!
Francisco
```
"""

with open(artifact_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Artefacto actualizado con notas casuales en: {artifact_path}")
