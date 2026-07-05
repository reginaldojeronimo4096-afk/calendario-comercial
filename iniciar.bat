@echo off
chcp 65001 >nul
title Calendario de Acoes e Promocoes
cd /d "%~dp0"

echo ============================================
echo   Calendario de Acoes e Promocoes
echo ============================================
echo.

REM --- Verifica se o Python esta instalado ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado.
    echo.
    echo Instale o Python em: https://www.python.org/downloads/
    echo IMPORTANTE: marque a caixa "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b
)

REM --- Cria o ambiente virtual na primeira vez ---
if not exist ".venv\" (
    echo Preparando o ambiente pela primeira vez... aguarde um pouco.
    python -m venv .venv
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip >nul
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo Abrindo o calendario no seu navegador...
echo (Para FECHAR o app: volte aqui e aperte Ctrl+C, ou feche esta janela.)
echo.

streamlit run app.py

pause
