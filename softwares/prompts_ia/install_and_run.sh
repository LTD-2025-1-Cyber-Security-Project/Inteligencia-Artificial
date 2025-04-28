#!/bin/bash

echo "======================================================"
echo "  NEURA AI - INSTALADOR E INICIALIZADOR"
echo "======================================================"
echo ""

# Verificar se Python está instalado
if command -v python3 &>/dev/null; then
    echo "Python encontrado!"
else
    echo "Python não encontrado! Por favor, instale o Python 3.7 ou superior."
    echo "Visite https://www.python.org/downloads/"
    read -p "Pressione Enter para sair..."
    exit 1
fi

echo "Verificando dependências..."

# Instalar dependências
echo ""
echo "Instalando dependências necessárias..."
python3 -m pip install --upgrade pip
python3 -m pip install requests Pillow python-dotenv reportlab

echo ""
echo "Todas as dependências foram instaladas com sucesso!"
echo ""

# Criar diretórios necessários
mkdir -p "histórico" "cache" "tmp"

echo "Diretórios necessários criados ou verificados."
echo ""

# Tornar o script executável
chmod +x run.py

# Iniciar aplicativo
echo "Iniciando Neura AI..."
echo ""
python3 run.py

read -p "Pressione Enter para sair..."