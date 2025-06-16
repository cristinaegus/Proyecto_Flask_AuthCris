@echo off
cd /d %~dp0..
call venv\Scripts\activate.bat
python -m Ejercicio_Pagina_Personalizada.app_ejerciciologin
pause