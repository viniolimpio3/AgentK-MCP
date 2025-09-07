# 🛡️ AgentK - Kubernetes Management Assistant

AgentK é um assistente inteligente para gerenciamento de clusters Kubernetes que utiliza GPT-4 e MCP (Model Context Protocol) para interagir com seu cluster de forma conversacional.

## 🌟 Recursos Principais

1. **Interface Conversacional**: Interface amigável baseada em chat para interagir com seu cluster Kubernetes
2. **Integração com GPT-4**: Utiliza GPT-4 para entender comandos em linguagem natural
3. **MCP (Model Context Protocol)**: Comunicação bidirecional eficiente entre o cliente e o servidor
4. **Monitoramento de Recursos**: Capacidade de listar e analisar diferentes recursos do Kubernetes

## 🎯 Funcionalidades

- 🔍 **Listagem de Recursos**: Lista pods, nodes, services, deployments e outros recursos
- 📝 **Detalhes de Objetos**: Obtém informações detalhadas sobre objetos específicos
- 🤖 **Interface Intuitiva**: Comunicação natural através do Streamlit
- 🔐 **Segurança**: Suporte a certificados e autenticação do Kubernetes

## 📸 AgentK

<p align="center">
  <img src="docs/AgentK-color.png" alt="AgentK" width="500" />
</p>

## 🚀 Tecnologias Utilizadas

### Servidor (MCP)
- Python 3.10+
- MCP (Model Context Protocol)
- Requests
- Python-dotenv
- Logging

### Cliente
- Python 3.10+
- Streamlit
- OpenAI GPT-4
- MCP Client
- AsyncIO

---

## 📦 Requisitos

- Python 3.10 ou superior
- Cluster Kubernetes configurado (local ou remoto)
- Certificados de acesso ao cluster
- pip (gerenciador de pacotes do Python)
- Chave de API OpenAI

## ⚙️ Instalação e Configuração

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/AgentK-MCP.git
cd AgentK-MCP
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
# No diretório server/
cp .env.example .env

# Configure as seguintes variáveis:
# - GPT_API_KEY_OPENAI: Sua chave da API OpenAI
# - K8S_BASE_URL: URL do seu cluster Kubernetes
# - K8S_CERT_PATH: Caminho para o certificado do cliente
# - K8S_KEY_CERT_PATH: Caminho para a chave do cliente
# - K8S_CA_PATH: Caminho para o certificado CA
```

## ⚙️ Execução

<!-- 1. Inicie o servidor MCP:
```bash
cd server
python app/main.py
``` -->

2. Em outro terminal, inicie o cliente Streamlit:
```bash
cd client
python -m streamlit run app/main.py
```

3. Acesse a interface web através do navegador (geralmente em http://localhost:8501)

## 💡 Uso

O AgentK oferece uma interface conversacional onde você pode:

1. **Listar recursos do cluster**:
   - Pods
   - Nodes
   - Services
   - Deployments
   - ReplicaSets
   - Namespaces
   - CronJobs

2. **Obter detalhes específicos**:
   - Informações detalhadas de recursos
   - Status dos pods
   - Configurações dos serviços

3. **Interagir naturalmente**:
   - Faça perguntas em linguagem natural
   - Receba respostas formatadas e contextualizadas
   - Analise problemas e receba sugestões

## 🔐 Segurança

O AgentK utiliza:
- Certificados TLS para comunicação com o cluster
- Autenticação via certificados do cliente
- Variáveis de ambiente para configurações sensíveis
- Logs para auditoria de operações
