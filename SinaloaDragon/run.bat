@echo off
echo ============================================
echo Chen Toka - Sinaloa Dragon
echo Inicializando entorno de desarrollo...
echo ============================================

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.11+ desde https://python.org
    pause
    exit /b 1
)

REM Crear entorno virtual si no existe
if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)

REM Activar entorno virtual e instalar dependencias
echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo Instalando/actualizando dependencias...
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    echo Revisa tu conexión a internet y el archivo requirements.txt
    pause
    exit /b 1
)

echo.
echo ============================================
echo Iniciando Chen Toka - Sinaloa Dragon...
echo ============================================
echo.

REM Ejecutar el juego
.venv\Scripts\python -m src.main

if errorlevel 1 (
    echo.
    echo El juego terminó con errores. Presiona cualquier tecla para salir.
    pause >nul
) else (
    echo.
    echo ¡Gracias por jugar Chen Toka!
    timeout /t 3 >nul
)