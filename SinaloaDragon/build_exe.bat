@echo off
echo ============================================
echo Chen Toka - Sinaloa Dragon
echo Compilando ejecutable para Windows...
echo ============================================

REM Verificar que el entorno virtual existe
if not exist ".venv" (
    echo ERROR: Entorno virtual no encontrado
    echo Ejecuta run.bat primero para configurar el proyecto
    pause
    exit /b 1
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Instalar PyInstaller si no está disponible
echo Verificando PyInstaller...
.venv\Scripts\pip install pyinstaller

if errorlevel 1 (
    echo ERROR: No se pudo instalar PyInstaller
    pause
    exit /b 1
)

REM Limpiar builds anteriores
echo Limpiando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "ChenToka.spec" del "ChenToka.spec"

echo.
echo Compilando ejecutable...
echo Esto puede tomar varios minutos...
echo.

REM Compilar con PyInstaller
.venv\Scripts\pyinstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "ChenToka" ^
    --icon "assets/icon.ico" ^
    --add-data "assets;assets" ^
    --add-data "levels;levels" ^
    --add-data "save;save" ^
    --distpath "dist" ^
    --workpath "build" ^
    src/main.py

if errorlevel 1 (
    echo.
    echo ERROR: La compilación falló
    echo Revisa que:
    echo 1. El juego funcione correctamente con run.bat
    echo 2. Todos los archivos estén presentes
    echo 3. No haya procesos usando archivos del proyecto
    echo.
    echo Para debug, ejecuta:
    echo .venv\Scripts\pyinstaller --console src/main.py
    pause
    exit /b 1
)

echo.
echo ============================================
echo ¡Compilación exitosa!
echo.
echo El ejecutable se encuentra en:
echo %cd%\dist\ChenToka.exe
echo.
echo Tamaño del archivo:
for %%A in ("dist\ChenToka.exe") do echo %%~zA bytes
echo.
echo Para distribuir, copia todo el contenido de la carpeta dist/
echo ============================================

REM Opcional: Abrir la carpeta dist
choice /M "¿Abrir la carpeta dist"
if errorlevel 2 goto :end
if errorlevel 1 explorer "dist"

:end
echo.
echo Presiona cualquier tecla para salir...
pause >nul