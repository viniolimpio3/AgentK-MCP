# Dockerfile para AgentK MCP Server
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos primeiro (para cache das camadas)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ ./app/

# Definir propriedade dos arquivos para o usuário agentk
RUN chown -R agentk:agentk /app

# Mudar para usuário não-root
USER agentk

# Expor porta 3333 para o serviço HTTP
EXPOSE 3333

# Comando padrão para iniciar o servidor via HTTP na porta 3333
CMD ["python", "app/main.py", "--port", "3333"]

# Health check para verificar se o servidor está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:3333/sse/ --max-time 5 > /dev/null 2>&1 || exit 1