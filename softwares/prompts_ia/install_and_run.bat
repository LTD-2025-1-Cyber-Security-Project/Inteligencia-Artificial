@echo off
echo ======================================================
echo   NEURA AI - INSTALADOR E INICIALIZADOR
echo ======================================================
echo.

REM Verificar se Python está instalado
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python não encontrado! Por favor, instale o Python 3.7 ou superior.
    echo Visite https://www.python.org/downloads/
    pause
    exit
)

echo Python encontrado! Verificando dependências...

REM Instalar dependências
echo.
echo Instalando dependências necessárias...
python -m pip install --upgrade pip
python -m pip install requests Pillow python-dotenv reportlab

echo.
echo Todas as dependências foram instaladas com sucesso!
echo.

REM Criar diretórios necessários
if not exist "histórico" mkdir "histórico"
if not exist "cache" mkdir "cache"
if not exist "tmp" mkdir "tmp"

echo Diretórios necessários criados ou verificados.
echo.

REM Iniciar aplicativo
echo Iniciando Neura AI...
echo.
python run.py

pause