# Reglas de Despliegue para Streamlit Community Cloud

Cuando trabajes en este proyecto (BD SENIOR / Gestión Empresarial), debes seguir estrictamente estas reglas en relación con la aplicación web (`fv-gestion.streamlit.app`):

1. **Entorno de Ejecución Remoto**: La aplicación está alojada en Streamlit Community Cloud, el cual lee el código fuente EXCLUSIVAMENTE desde la rama `main` en GitHub.
2. **Ediciones Locales No Son Suficientes**: Cualquier modificación de código o corrección aplicada localmente en los archivos (ej. `empresa_app.py`, `app.py`, etc.) NO se reflejará en la aplicación web en vivo hasta que los cambios sean subidos al repositorio.
3. **ACCIÓN OBLIGATORIA POST-EDICIÓN**: Cada vez que modifiques, arregles o agregues código destinado a solucionar un problema en la página web, DEBES ejecutar obligatoriamente `git add .`, `git commit -m "..."` y `git push origin main`.
4. **No Pedir Probar Hasta Haber Pusheado**: NUNCA le digas al usuario que "el código ya está arreglado" ni le pidas que presione F5 o recargue la página web hasta que hayas ejecutado exitosamente `git push` y confirmado que el código está en GitHub.
5. **Almacenamiento Efímero en la Nube**: Streamlit Cloud borra sus bases de datos SQLite locales cuando la aplicación se "duerme". Asegúrate siempre de que cualquier nuevo punto de entrada (`app.py`, `empresa_app.py`, `app_onboarding.py`, etc.) incluya la rutina de sincronización de inicio (`download_db_from_gcs()`) mediante `@st.cache_resource` antes de inicializar el motor de la base de datos.
