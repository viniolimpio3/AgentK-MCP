@echo off
REM Script para testar a aplicação AgentK com Docker
REM Autor: Vinícius

echo 🚀 AgentK Docker Setup Script
echo ================================

REM Verificar se o Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não encontrado! Por favor, instale o Docker primeiro.
    pause
    exit /b 1
)

REM Verificar se o Docker Compose está instalado
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose não encontrado! Por favor, instale o Docker Compose primeiro.
    pause
    exit /b 1
)

REM Verificar se o arquivo .env existe
if not exist .env (
    echo ⚠️ Arquivo .env não encontrado. Copiando .env.example...
    copy .env.example .env
    echo ✅ Arquivo .env criado! Por favor, configure sua OPENAI_API_KEY em .env
    echo 📝 Abrindo .env para edição...
    notepad .env
    echo Pressione qualquer tecla quando terminar de configurar o .env...
    pause >nul
)

REM Verificar se OPENAI_API_KEY está configurada
findstr /C:"OPENAI_API_KEY=sk-" .env >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ OPENAI_API_KEY não parece estar configurada corretamente no .env
    echo Por favor, configure uma chave válida da OpenAI
    pause
    exit /b 1
)

echo ✅ Pré-requisitos verificados!
echo.

REM Menu de opções
echo Escolha uma opção:
echo 1) Construir e executar (primeira vez)
echo 2) Executar serviços existentes
echo 3) Parar serviços
echo 4) Ver logs
echo 5) Rebuild completo
echo 6) Limpeza completa

set /p option="Opção [1-6]: "

if "%option%"=="1" (
    echo 🔨 Construindo e executando pela primeira vez...
    docker-compose up --build -d
    goto :success
)

if "%option%"=="2" (
    echo ▶️ Executando serviços...
    docker-compose up -d
    goto :success
)

if "%option%"=="3" (
    echo ⏹️ Parando serviços...
    docker-compose down
    goto :end
)

if "%option%"=="4" (
    echo 📋 Mostrando logs...
    docker-compose logs -f
    goto :end
)

if "%option%"=="5" (
    echo 🔄 Rebuild completo...
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    goto :success
)

if "%option%"=="6" (
    echo 🧹 Limpeza completa...
    docker-compose down -v
    docker system prune -f
    docker volume prune -f
    goto :end
)

echo ❌ Opção inválida!
pause
exit /b 1

:success
echo.
echo 🎉 Serviços iniciados!
echo ================================
echo 📱 Streamlit Client: http://localhost:8501
echo 🔧 MCP Server: http://localhost:3333/mcp
echo.
echo Para ver logs em tempo real:
echo docker-compose logs -f
echo.
echo Para parar os serviços:
echo docker-compose down

:end
echo.
pause