#!/bin/bash

echo "Iniciando o Quiz Game Manager..."
echo "A interface estará disponível em http://localhost:5001/gerenciador"
echo "API disponível em http://localhost:5001/api"
echo "Pressione Ctrl+C para encerrar"

# Verificar se o Python está instalado
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Erro: Python não encontrado. Por favor, instale o Python 3."
    exit 1
fi

# Verificar se as dependências estão instaladas
$PYTHON_CMD -c "import flask" &>/dev/null
if [ $? -ne 0 ]; then
    echo "Instalando dependências necessárias..."
    $PYTHON_CMD -m pip install -r requirements.txt
fi

# Iniciar a aplicação
$PYTHON_CMD app.py 