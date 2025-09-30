# 🛡️ AgentK - Especialista em Configurações YAML Kubernetes

AgentK é um assistente inteligente especializado em **análise, otimização e gestão de configurações YAML do Kubernetes**. Utilizando GPT-4 e MCP (Model Context Protocol), oferece orientações baseadas em boas práticas para criação e manutenção de recursos Kubernetes de qualidade profissional.

<p align="center">
  <img src="docs/AgentK-color.png" alt="AgentK" width="200" />
</p>

## 🎯 Objetivo Principal

**AgentK é seu consultor especializado em YAML Kubernetes**, focado em:
- ✅ **Extrair e analisar** configurações existentes do cluster
- ✅ **Sugerir melhorias** baseadas em boas práticas de produção
- ✅ **Validar configurações** antes da aplicação (dry-run)
- ✅ **Implementar recursos** com verificação automática de conflitos
- ✅ **Orientar na criação** de YAMLs seguindo padrões de qualidade

> **💡 Importante**: AgentK **não é uma ferramenta de monitoramento**, mas sim um especialista em configurações YAML e aplicação de boas práticas.

## 🌟 Capacidades Principais

### 📋 **Gestão Completa de Recursos (CRUD)**
- 📋 **Listar** recursos do cluster por tipo
- 📄 **Extrair** configurações YAML de recursos existentes  
- 🎯 **Obter** YAML específico por nome e namespace
- 🚀 **Implementar** recursos (create/update automático com prevenção de conflitos)
- 🗑️ **Deletar** recursos individuais do cluster
- ✅ **Validar** YAMLs com dry-run antes da aplicação

### 🎯 **Foco em Boas Práticas**
- 🏷️ **Labels e annotations** consistentes
- 💾 **Resource limits e requests** adequados
- 🔐 **Configurações de segurança** apropriadas 
- 📝 **Estrutura YAML** limpa e legível

### 🔧 **Recursos Suportados**
- **Namespaced**: `pods`, `services`, `deployments`, `configmaps`, `secrets`, `ingresses`, `persistent_volume_claims`, `replicasets`, `statefulsets`, `cronjobs`, `jobs`, `horizontal_pod_autoscalers`, `replication_controllers`, `daemon_sets`  
- **Cluster-wide**: `nodes`, `persistent_volumes`, `namespaces`

### 📊 **Exportação de Histórico**
- **Relatórios em Markdown** com estatísticas da sessão
- **Métricas de performance** (tempo de execução, tokens utilizados)
- **Histórico completo** de conversas e chamadas MCP

## 🚀 Tecnologias

- 🖥️ **FastMCP** + **Kubernetes Python Client** (Servidor)
- 🌐 **Streamlit** + **GPT-4** (Cliente)
- 🛠️ **6 MCP Tools** para operações CRUD completas
- ⚙️ **Configuração Externa** (`resource_config.yaml`)

## ⚙️ Instalação

### 🐳 Deploy com Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/viniolimpio3/AgentK-MCP.git
cd AgentK-MCP

# 2. Configure variáveis de ambiente (OBRIGATÓRIO)
cp .env.example .env
# Edite .env e configure: OPENAI_API_KEY e MCP_SERVER_URL

# 3. Configure acesso ao Kubernetes:
# Windows: Descomente no docker-compose.yml:
# - ${USERPROFILE}/.kube/config:/app/.kube/config:ro

# Linux/Mac: Descomente no docker-compose.yml:
# - ${HOME}/.kube/config:/app/.kube/config:ro

# 4. Execute
docker-compose up --build -d

# 5. Acesse a aplicação
# http://localhost:8501
```

### 🚀 Deploy Automático

O projeto possui **GitHub Actions** configurado para CI/CD:
- 🔄 **Deploy automático** a cada push na branch `master`
- ⏪ **Rollback manual** disponível via workflow
- 🔍 **Health checks** automáticos pós-deploy

> **⚠️ Pré-requisito**: Arquivo `.env` deve existir na VM de destino com as variáveis `OPENAI_API_KEY` e `MCP_SERVER_URL` configuradas.

### 🔧 Instalação Local

```bash
# 1. Clone e instale dependências
git clone https://github.com/viniolimpio3/AgentK-MCP.git
cd AgentK-MCP
pip install -r client/requirements.txt
pip install -r server/requirements.txt

# 2. Configure variáveis de ambiente (OBRIGATÓRIO)
cp .env.example .env
# Edite .env e configure: OPENAI_API_KEY e MCP_SERVER_URL

# 3. Execute a aplicação
# Certifique-se que kubectl está configurado
cd client
streamlit run app/main.py
```

## ✨ Principais Diferenciais

- 🎯 **Boas Práticas Integradas**: Sugestões de melhorias automáticas
- ✅ **Dry-run Integrado**: Validação antes da aplicação
- 💬 **Interface Conversacional**: Interação natural via chat
- 🔧 **Configuração Externa**: Flexibilidade e customização

## 🏗️ Arquitetura

<p align="center">
  <img src="docs/agent-k-arch.png" alt="AgentK" width="500" />
</p>

## 📚 Documentação Adicional

- 📖 [Guia de Deploy](docs/DEPLOY.md)
- 🧪 [Exemplos de Uso](docs/tests/)
- 🏗️ [Arquitetura do Sistema](docs/agent-k-arch.png)

---

**Orientador:** Professor Dr. Fábio Henrique Cabrini
**AgentK** - Seu especialista em configurações YAML Kubernetes