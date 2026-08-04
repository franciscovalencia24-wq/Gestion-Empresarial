# Reglas de Generación de Imágenes e Infografías

Siempre que se deba generar, exportar o renderizar imágenes a partir de HTML (como con `html2image`) o código, se DEBE cumplir el siguiente estándar de máxima calidad para asegurar la nitidez al aplicar zoom en dispositivos móviles:

1. **Vectores sobre Raster:** Siempre priorizar y utilizar las versiones vectoriales (`.svg`) de los logos institucionales (FV, Altus, etc.) que se encuentren en la carpeta `assets` en lugar de `.jpg` o `.png`. Si se inyectan en base64, usar `image/svg+xml`.
2. **Formato Lossless:** Las imágenes finales deben guardarse siempre en formato `.png` (compresión sin pérdida) en lugar de `.jpg`, para evitar ruido y desenfoques alrededor del texto y los gráficos.
3. **Escala 2x (Renderizado 4K):** Para asegurar alta definición, el renderizado base desde HTML debe forzarse a doble resolución. En HTML esto se logra aplicando `style="zoom: 2;"` al `<body>` y multiplicando al menos por 2 el ancho y alto del `viewport` en la herramienta de captura (ej. pasando de `1080x4000` a `2160x8000`).
4. **Proporciones Correctas:** Asegurarse de que los logos tengan el peso visual correcto en los diseños finales, utilizando tamaños generosos (ej. 160px a 220px de alto en lienzos de 1080px/2160px) que sean legibles sin necesidad de acercamiento.
