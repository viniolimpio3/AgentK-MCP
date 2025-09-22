#!/bin/bash

# Script para testar a aplicação AgentK com Docker
# Autor: Vinícius
# Data: $(date)

set -e

echo "🚀 AgentK Docker Setup Script"
echo "================================"

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado! Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se o Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado! Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️ Arquivo .env não encontrado. Copiando .env.example..."
    cp .env.example .env
    echo "✅ Arquivo .env criado! Por favor, configure sua OPENAI_API_KEY em .env"
    echo "📝 Editando .env..."
    
    # Tentar abrir editor padrão
    if command -v code &> /dev/null; then
        code .env
    elif command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    else
        echo "Por favor, edite o arquivo .env manualmente e adicione sua OPENAI_API_KEY"
    fi
    
    echo "Pressione Enter quando terminar de configurar o .env..."
    read
fi

# Verificar se OPENAI_API_KEY está configurada
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️ OPENAI_API_KEY não parece estar configurada corretamente no .env"
    echo "Por favor, configure uma chave válida da OpenAI"
    exit 1
fi

echo "✅ Pré-requisitos verificados!"
echo ""

# Menu de opções
echo "Escolha uma opção:"
echo "1) Construir e executar (primeira vez)"
echo "2) Executar serviços existentes"
echo "3) Parar serviços"
echo "4) Ver logs"
echo "5) Rebuild completo"
echo "6) Limpeza completa"

read -p "Opção [1-6]: " option

case $option in
    1)
        echo "🔨 Construindo e executando pela primeira vez..."
        docker-compose up --build -d
        ;;
    2)
        echo "▶️ Executando serviços..."
        docker-compose up -d
        ;;
    3)
        echo "⏹️ Parando serviços..."
        docker-compose down
        ;;
    4)
        echo "📋 Mostrando logs..."
        docker-compose logs -f
        ;;
    5)
        echo "🔄 Rebuild completo..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    6)
        echo "🧹 Limpeza completa..."
        docker-compose down -v
        docker system prune -f
        docker volume prune -f
        ;;
    *)
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac

if [ "$option" = "1" ] || [ "$option" = "2" ] || [ "$option" = "5" ]; then
    echo ""
    echo "🎉 Serviços iniciados!"
    echo "================================"
    echo "📱 Streamlit Client: http://localhost:8501"
    echo "🔧 MCP Server: http://localhost:3333/mcp"
    echo ""
    echo "Para ver logs em tempo real:"
    echo "docker-compose logs -f"
    echo ""
    echo "Para parar os serviços:"
    echo "docker-compose down"
fi