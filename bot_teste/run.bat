@echo off
setlocal

REM Ir para a pasta do script
cd /d "%~dp0"

REM Se estivermos na raiz, entrar em bot_teste; se já estivermos em bot_teste, continuar
if exist "bot.py" goto have_src
if exist "bot_teste\bot.py" cd bot_teste
:have_src

echo ===== Preparando ambiente =====

REM Criar venv local se não existir
if exist .venv\Scripts\python.exe goto venv_ready
call :makevenv
:venv_ready

REM Ativar venv
call .venv\Scripts\activate.bat

REM Atualizar pip e instalar dependências
python -m pip install --upgrade pip >nul
echo Instalando dependências a partir de requirements.txt...
pip install -r requirements.txt

REM Criar .env de exemplo se não existir
if exist .env goto have_env
echo API_GEMINI=sua_chave_aqui> .env
echo Arquivo .env criado (preencha sua chave em API_GEMINI).
:have_env

echo ===== Iniciando bot =====
python bot.py

echo.
echo Execucao finalizada.
pause
endlocal
goto :eof

:makevenv
echo Criando ambiente virtual (.venv)...
py -3 -m venv .venv 2>nul
if exist .venv\Scripts\python.exe goto :eof
python -m venv .venv
goto :eof

