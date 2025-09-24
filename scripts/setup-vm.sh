#!/bin/bash

# Script de setup inicial para VM AWS
# Execute este script uma única vez na VM para preparar o ambiente

set -e

echo "🚀 Configurando VM AWS para AgentK-MCP..."

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Docker
echo "🐳 Instalando Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
echo "📦 Instalando Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar Git
echo "📝 Instalando Git..."
sudo apt install -y git curl

# Clonar repositório
echo "⬇️ Clonando repositório AgentK-MCP..."
cd /home/$USER
git clone https://github.com/viniolimpio3/AgentK-MCP.git
cd AgentK-MCP

# Criar arquivo .env
echo "⚙️ Configurando variáveis de ambiente..."
cat > .env << 'EOL'
# Configurações do AgentK-MCP
MCP_SERVER_URL=http://agentk-server:3333
OPENAI_API_KEY=your_openai_api_key_here

# Configurações específicas para produção
PYTHONUNBUFFERED=1
FASTMCP_LOG_LEVEL=INFO
EOL

echo "📝 Arquivo .env criado. IMPORTANTE: Edite o arquivo .env e adicione sua OPENAI_API_KEY!"
echo "Comando: nano .env"

# Configurar firewall
echo "🔒 Configurando firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 3333/tcp  # AgentK Server
sudo ufw allow 8501/tcp  # Streamlit
sudo ufw --force enable

# Configurar logs
echo "📊 Configurando logs..."
sudo mkdir -p /var/log/agentk
sudo chown $USER:$USER /var/log/agentk

# Primeiro build
echo "🔨 Fazendo primeiro build..."
docker-compose build

echo "✅ Setup da VM concluído!"
echo ""
echo "🔧 Próximos passos:"
echo "1. Edite o arquivo .env e adicione sua OPENAI_API_KEY:"
echo "   nano /home/$USER/AgentK-MCP/.env"
echo ""
echo "2. Configure os secrets no GitHub:"
echo "   - AWS_VM_SSH_KEY: Sua chave SSH privada"
echo "   - AWS_VM_HOST: $(curl -s ifconfig.me)"
echo "   - AWS_VM_USER: $USER"
echo ""
echo "3. Para testar manualmente:"
echo "   cd /home/$USER/AgentK-MCP && docker-compose up -d"
echo ""
echo "🌐 Após configurar, sua aplicação estará em:"
echo "   - Servidor MCP: http://$(curl -s ifconfig.me):3333"
echo "   - Cliente Web: http://$(curl -s ifconfig.me):8501"