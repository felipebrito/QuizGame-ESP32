@echo off
echo Iniciando o Quiz Game Manager...
echo A interface estara disponivel em http://localhost:5001/gerenciador
echo API disponivel em http://localhost:5001/api
echo Pressione Ctrl+C para encerrar

REM Verificar se o Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Python nao encontrado. Por favor, instale o Python 3.
    pause
    exit /b 1
)

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Verificar se as dependências estão instaladas
python -c "import flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Instalando dependencias necessarias...
    pip install -r requirements.txt
)

REM Iniciar a aplicação
python app.py

REM Desativar ambiente virtual ao sair
call venv\Scripts\deactivate.bat

pause 