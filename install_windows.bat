@echo off
echo ===================================================
echo     Instalador de OmniFloat para Windows
echo ===================================================

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Por favor instala Python desde python.org marcando "Add Python to PATH".
    pause
    exit /b 1
)

echo -> Instalando OmniFloat y dependencias con pip...
python -m pip install --upgrade pip
python -m pip install -e .

echo -> Creando accesos directos en Escritorio y Menu Inicio...
python install_shortcuts.py

echo.
echo ===================================================
echo    OmniFloat ha sido instalado exitosamente!
echo ===================================================
echo Se han creado accesos directos en:
echo   - Tu Escritorio
echo   - Tu Menu Inicio (busca "OmniFloat")
echo.
echo Iniciando OmniFloat ahora...
start "" "%~dp0OmniFloat.lnk"
timeout /t 3 >nul
exit /b 0
