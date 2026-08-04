@echo off
schtasks /create /tn "FVA_AutoPost_Daily" /tr "\"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\scripts\auto_post_daily.bat\"" /sc daily /st 08:45 /f
echo Tarea programada exitosamente.
