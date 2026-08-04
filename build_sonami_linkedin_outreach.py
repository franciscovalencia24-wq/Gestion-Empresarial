import sys

sys.stdout.reconfigure(encoding='utf-8')

artifact_path = r"C:\Users\franc\.gemini\antigravity-ide\brain\e0a740f0-6d0f-448b-98b0-162b61f9b6b0\cumbre_sonami_prospeccion.md"

md_content = """# 🎯 Plan de Acción Inmediato: Búsqueda Ejecutiva y Prospección en LinkedIn (Cumbre SONAMI 2026)

**Objetivo**: Identificar y contactar HOY a ejecutivos, directores y empresarios del sector minero en Chile a través de LinkedIn.

---

## 🔍 1. Comandos de Búsqueda Directa en LinkedIn (Copiar y Pegar en la Barra de Búsqueda)

Abre LinkedIn en tu navegador y pega los siguientes filtros Booleanos en el buscador para filtrar contactos en Chile:

### 🔹 Búsqueda 1: Liderazgo Gremiador y Directores SONAMI
```text
(SONAMI OR "Sociedad Nacional de Mineria") AND (Presidente OR Director OR "Vicepresidente" OR Consejero)
```
👉 *Filtro de Ubicación*: Chile.

### 🔹 Búsqueda 2: Fundadores y Dueños de Empresas Proveedoras Mineras (High Net Worth)
```text
("Servicios Mineros" OR "Sondajes" OR "Maquinaria Minera" OR "Ingenieria Minera" OR "Montaje Industrial") AND (Fundador OR Socio OR "Gerente General" OR CEO)
```
👉 *Filtro de Ubicación*: Chile.

### 🔹 Búsqueda 3: CFOs y VPs de Finanzas de Grandes Compañías Mineras
```text
(CFO OR "VP Finanzas" OR "Gerente de Finanzas" OR "Gerente de Administración") AND (Antofagasta Minerals OR BHP OR Codelco OR Lundin OR Teck OR Collahuasi OR Anglo American OR Sierra Gorda)
```
👉 *Filtro de Ubicación*: Chile.

---

## 📋 2. Lista de Contactos Clave Identificados para Contactar Hoy

| Ejecutivo / Perfil | Cargo / Institución | Enfoque de Conversación | Tipo de Nota |
| :--- | :--- | :--- | :--- |
| **Jorge Riesco Valdés** | Presidente SONAMI | Estructuración patrimonial y certeza de capitales | Perfil 1 (Líder Gremial) |
| **Reinaldo Salazar** | Vicepresidente SONAMI | Protección de liquidez y contingencia normativa | Perfil 1 (Líder Gremial) |
| **Patricio Céspedes** | Vicepresidente SONAMI | Eficiencia de dividendos y estructuras familiares | Perfil 1 (Líder Gremial) |
| **Fundadores / CEOs Proveedores Mineros** | Heavy Equipment, Sondajes, Logística | Separación de riesgo operacional vs. patrimonio familiar | Perfil 2 (Dueños Proveedores) |
| **CFOs / VPs de Finanzas Mineras** | Codelco, Antofagasta, BHP, Lundin | Reliquidación IGC (Art. 47 bis), APV Colectivo y USD | Perfil 3 (CFOs y VPs) |

---

## 💬 3. Notas de Invitación Cortas para LinkedIn (<= 300 Caracteres)

⚠️ **IMPORTANTE**: Al presionar **"Añadir una nota"** en LinkedIn, el límite máximo permitido es de **300 caracteres**. Utiliza estas plantillas exactas:

---

### 📩 Opción A: Para Presidentes y Directores (Líderes SONAMI)
> *Estimado/a [Nombre], le saluda Francisco Valencia, Managing Partner de FV Asesorías (MFO).*
>
> *Seguí sus planteamientos en SONAMI sobre la certeza de capitales en minería. En nuestro Multi-Family Office apoyamos a líderes del sector a auditar su patrimonio 360° mediante IA (ALTUS AI).*
>
> *Un gusto conectar.*

*(Longitud: 295 caracteres)*

---

### 📩 Opción B: Para Dueños / Fundadores de Empresas Proveedoras Mineras
> *Hola [Nombre], felicitaciones por la gestión en [Empresa].*
>
> *Como MFO Digital (FV Asesorías), ayudamos a empresarios proveedores mineros a separar el riesgo operativo de su patrimonio personal, optimizar la salida de dividendos y proteger su legado.*
>
> *Será un placer conectar por este medio. Saludos.*

*(Longitud: 288 caracteres)*

---

### 📩 Opción C: Para CFOs, VPs de Finanzas y Altos Ejecutivos
> *Estimado/a [Nombre], gusto en saludarle.*
>
> *En FV Asesorías (Multi-Family Office) ayudamos a altos ejecutivos mineros a reliquidar impuestos por bonos (Art. 47 bis) y rentabilizar sus portafolios en USD mediante nuestro software cuantitativo ALTUS AI.*
>
> *Quedo a su disposición para conectar.*

*(Longitud: 279 caracteres)*

---

## ✉️ 4. Mensaje Completo de Seguimiento (Para enviar una vez que ACEPTEN la invitación)

Una vez que acepten tu solicitud de conexión, envíales de inmediato este mensaje por chat:

```text
Estimado/a [Nombre], muchas gracias por conectar.

Como le mencionaba, en FV Asesorías e Inversiones somos un Multi-Family Office Digital impulsado por nuestro software cuantitativo privado de Inteligencia Artificial (ALTUS AI). 

Combinamos la agilidad tecnológica de una WealthTech con la exclusividad de una oficina patrimonial privada, auditando en 360° la situación tributaria, inmobiliaria, composición familiar, seguros e inversiones para proteger el legado de nuestros clientes a través de las generaciones.

En vista de los recientes cambios de la Reforma Tributaria 2026, nos encantaría coordinar una breve reunión virtual de 15 minutos para presentarle nuestro Diagnóstico Patrimonial 360° sin costo.

¿Le acomodaría revisar agenda para esta semana?

Un cordial saludo,
Francisco Valencia
Managing Partner | Asesor Financiero Senior
FV Asesorías e Inversiones
📱 +56 9 6677 9662 • 📩 contacto@fv-inversiones.com
```
"""

with open(artifact_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Artefacto actualizado con éxito en: {artifact_path}")
