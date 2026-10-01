@echo off
echo ========================================================
echo [ALTUS CORE] Automatizacion Mensual de Valorizacion
echo ========================================================
echo Iniciando proceso de tasacion y sincronizacion cloud...

:: Moverse a la raiz del proyecto
cd /d "%~dp0\.."

:: Ejecutar el script python de valorizacion
python scripts\utils\generate_valuation_pdf.py

echo.
echo Proceso finalizado. El PDF se ha guardado en DB y en Google Cloud.
pause
