# Dockerfile para AgentK Streamlit Client
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash streamlit

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

# Definir propriedade dos arquivos para o usuário streamlit
RUN chown -R streamlit:streamlit /app

# Mudar para usuário não-root
USER streamlit

# Expor porta 443 (porta padrão do Streamlit)
EXPOSE 443

# Comando padrão para iniciar o Streamlit
CMD ["streamlit", "run", "app/main.py", "--server.port=443", "--server.address=0.0.0.0", "--server.headless=true", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]

# Health check para verificar se o Streamlit está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:443/_stcore/health || exit 1