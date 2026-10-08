@echo off
title GIS Data Auditor - Lanzador
echo =======================================================
echo          GIS DATA AUDITOR - INICIANDO APLICACION
echo =======================================================
echo.

cd /d "%~dp0"

:: 1. Buscar si python de miniconda en la cuenta actual existe
if exist "%USERPROFILE%\miniconda3\python.exe" (
    echo Utilizando Python detectado en Miniconda...
    "%USERPROFILE%\miniconda3\python.exe" -m streamlit run gis_data_auditor/ui/app_streamlit.py
    goto END
)

:: 2. Buscar si Python de ArcGIS Pro existe
if exist "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" (
    echo Utilizando Python detectado de ArcGIS Pro...
    "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" -m streamlit run gis_data_auditor/ui/app_streamlit.py
    goto END
)

:: 3. Intentar comando python por defecto del sistema (PATH)
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Utilizando Python por defecto del sistema...
    python -m streamlit run gis_data_auditor/ui/app_streamlit.py
    goto END
)

echo.
echo ====================================================================
echo ERROR: No se encontro una instalacion de Python con Streamlit.
echo ====================================================================
echo Por favor asegurese de instalar las dependencias necesarias:
echo pip install streamlit fiona geopandas pandas openpyxl pydantic
echo ====================================================================
pause

:END
