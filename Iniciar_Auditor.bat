@echo off
title GIS Data Auditor - Lanzador
echo =======================================================
echo          GIS DATA AUDITOR - INICIANDO APLICACION
echo =======================================================
echo.

set "PYTHON_EXE=C:\Users\Nacho\miniconda3\python.exe"

if exist "%PYTHON_EXE%" (
    echo Entorno de Python detectado en: %PYTHON_EXE%
    echo Abriendo interfaz grafica en el navegador web local...
    echo.
    cd /d "%~dp0"
    "%PYTHON_EXE%" -m streamlit run gis_data_auditor/ui/app_streamlit.py
) else (
    echo Entorno de Python principal no encontrado, buscando en el sistema...
    cd /d "%~dp0"
    python -m streamlit run gis_data_auditor/ui/app_streamlit.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo =======================================================
    echo ERROR: Ocurrio un problema al iniciar Streamlit.
    echo =======================================================
    pause
)
