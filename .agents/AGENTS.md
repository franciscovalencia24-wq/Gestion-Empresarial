# Reglas de Generación de Imágenes e Infografías

Siempre que se deba generar, exportar o renderizar imágenes a partir de HTML (como con `html2image`) o código, se DEBE cumplir el siguiente estándar de máxima calidad para asegurar la nitidez al aplicar zoom en dispositivos móviles:

1. **Vectores sobre Raster:** Siempre priorizar y utilizar las versiones vectoriales (`.svg`) de los logos institucionales (FV, Altus, etc.) que se encuentren en la carpeta `assets` en lugar de `.jpg` o `.png`. Si se inyectan en base64, usar `image/svg+xml`.
2. **Formato Lossless:** Las imágenes finales deben guardarse siempre en formato `.png` (compresión sin pérdida) en lugar de `.jpg`, para evitar ruido y desenfoques alrededor del texto y los gráficos.
3. **Escala 2x (Renderizado 4K):** Para asegurar alta definición, el renderizado base desde HTML debe forzarse a doble resolución. En HTML esto se logra aplicando `style="zoom: 2;"` al `<body>` y multiplicando al menos por 2 el ancho y alto del `viewport` en la herramienta de captura (ej. pasando de `1080x4000` a `2160x8000`).
4. **Proporciones Correctas:** Asegurarse de que los logos tengan el peso visual correcto en los diseños finales, utilizando tamaños generosos (ej. 160px a 220px de alto en lienzos de 1080px/2160px) que sean legibles sin necesidad de acercamiento.

# Contexto del Proyecto y Aislamiento de Memoria (Regla Estricta para Agentes)

Para evitar la mezcla de contextos o alucinaciones entre proyectos de Francisco, CUALQUIER AGENTE LLM debe acatar estrictamente estas definiciones para el workspace actual (`BD SENIOR`):

1. **Identidad del Proyecto actual ("FV Gestión"):** Este repositorio contiene el código de **FV Gestión**, una intranet/CRM privado construido en Python/Streamlit que corre en `fv-gestion.streamlit.app`. Es de uso exclusivo para Francisco y Natalia.
2. **NO confundir con "FV Web Pública":** Este código NO TIENE NADA QUE VER con la página web de acceso público de FV (landing pages, marketing, clientes). Si el usuario pide algo para la web pública, debes advertirle que está en el repositorio equivocado o pedirle que cambie de workspace.
3. **Rol de ALTUS en este proyecto:** "Altus" no es una API de terceros a eliminar, ni otro proyecto de software separado. Altus (ALTUS AI SpA) es una de las "Empresas" administradas *dentro* de FV Gestión, junto con FV Asesorías SpA. Nunca ofrezcas "borrar Altus" a menos que el usuario pida explícitamente borrar un registro comercial.
4. **NO confundir "Desarrollo en local" con "Archivos locales vs Nube":** Aunque el código se desarrolle localmente en el PC del usuario, la base de datos `crm_database.db` se sincroniza obligatoriamente con Google Cloud Storage (GCS) usando un mecanismo de "Bóveda" para prevenir pérdida de datos.
