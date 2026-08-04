@echo off
cd /d "C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR"
set PYTHONPATH=%cd%
"venv\Scripts\python.exe" -m src.osint.market_data_engine
