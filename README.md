# 🛡️ AgentK - Especialista em Configurações YAML Kubernetes

AgentK é um assistente inteligente especializado em **análise, otimização e gestão de configurações YAML do Kubernetes**. Utilizando GPT-4.1 e MCP (Model Context Protocol), oferece orientações baseadas em boas práticas para criação e manutenção de recursos Kubernetes de qualidade profissional.

<p align="center">
  <img src="docs/AgentK-color.png" alt="AgentK" width="200" />
</p>

## Objetivo Principal

**AgentK é seu consultor especializado em YAML Kubernetes**, focado em:
- **Extrair e analisar** configurações existentes do cluster
- **Sugerir melhorias** baseadas em boas práticas de produção
- **Validar configurações** antes da aplicação (dry-run)
- **Implementar recursos** com verificação automática de conflitos
- **Orientar na criação** de YAMLs seguindo padrões de qualidade

> **Importante**: AgentK **não é uma ferramenta de monitoramento**, mas sim um especialista em configurações YAML e aplicação de boas práticas.

## Capacidades Principais

### Gestão Completa de Recursos (CRUD)
- **Listar** recursos do cluster por tipo
- **Extrair** configurações YAML de recursos existentes  
- **Obter** YAML específico por nome e namespace
- **Implementar** recursos (create/update automático com prevenção de conflitos)
- **Deletar** recursos individuais do cluster
- **Validar** YAMLs com dry-run antes da aplicação

### Foco em Boas Práticas
- **Labels e annotations** consistentes
- **Resource limits e requests** adequados
- **Configurações de segurança** apropriadas 
- **Estrutura YAML** limpa e legível

### Recursos Suportados
- **Namespaced**: `pods`, `services`, `deployments`, `configmaps`, `secrets`, `ingresses`, `persistent_volume_claims`, `replicasets`, `statefulsets`, `cronjobs`, `jobs`, `horizontal_pod_autoscalers`, `replication_controllers`, `daemon_sets`  
- **Cluster-wide**: `nodes`, `persistent_volumes`, `namespaces`

### Exportação de Histórico
- **Relatórios em Markdown** com estatísticas da sessão
- **Métricas de performance** (tempo de execução, tokens utilizados)
- **Histórico completo** de conversas e chamadas MCP

## 🚀 Tecnologias

- **FastMCP** + **Kubernetes Python Client** (Servidor)
- **Streamlit** + **GPT-4** (Cliente)
- **6 MCP Tools** para operações CRUD completas
- **Configuração Externa** (`resource_config.yaml`)

## 🚀 Início Rápido

### Pré-requisitos
- Docker e Docker Compose instalados
- Acesso a um cluster Kubernetes (`kubectl` configurado)
- Chave de API da OpenAI

### Deploy Rápido

```bash
# 1. Clone e configure
git clone https://github.com/viniolimpio3/AgentK-MCP.git
cd AgentK-MCP
cp .env.example .env  # Configure OPENAI_API_KEY e MCP_SERVER_URL

# 2. Execute com Docker
docker-compose up --build -d

# 3. Acesse: http://localhost:8501
```

> 📖 **Para instalação detalhada, configuração de produção e CI/CD:**  
> Consulte a [documentação completa de deploy](#-documentação-completa)

## Principais Diferenciais

- **Boas Práticas Integradas**: Sugestões de melhorias automáticas
- **Dry-run Integrado**: Validação antes da aplicação
- **Interface Conversacional**: Interação natural via chat
- **Configuração Externa**: Flexibilidade e customização

## 🏗️ Arquitetura

<p align="center">
  <img src="docs/agent-k-arch.png" alt="AgentK" width="500" />
</p>

## 📚 Documentação Completa

### 📖 Guias de Configuração e Deploy
- **[Configuração do Ambiente na VM](docs/VM-environment-config.md)** - Setup completo do ambiente de produção
- **[Pipeline CI/CD com GitHub Actions](docs/Pipeline-GithubActions-deployment-config.md)** - Deploy automático e rollback

### 🧪 Testes e Validação
- **[Procedimento de Testes do AgentK](docs/Procedimento-Testes-AgentK.md)** - Metodologia completa dos 50 testes realizados
- **[Resumo das Misconfigurations](docs/Resumo-misconfigurations-tests.md)** - Detalhamento das misconfigurations intencionais
- **[Arquivos de Teste YAML](docs/tests/)** - 10 arquivos com misconfigurations + 50 resultados exportados

### 📊 Resultados e Métricas
**Taxa de Detecção:**
- ✅ Credenciais Expostas: **100%** (50/50)
- ✅ Versão de Imagem: **100%** (50/50)
- ✅ Erros Semânticos: **96%** (48/50)

**Taxa de Implementação:** **88%** (44/50 testes bem-sucedidos)

### 🎨 Recursos Visuais
- **[Arquitetura do Sistema](docs/agent-k-arch.png)** - Diagrama da arquitetura MCP
- **[Exemplos de YAML](docs/)** - `basic-example.yaml` e `orion-example.yaml`

### 🔗 Links Rápidos
| Documento | Descrição |
|-----------|-----------|
| [Procedimento de Testes](docs/Procedimento-Testes-AgentK.md) | Metodologia, resultados e análise dos 50 testes |
| [Misconfigurations](docs/Resumo-misconfigurations-tests.md) | 29 misconfigurations em 10 arquivos de teste |
| [Resultados dos Testes](docs/tests/results/) | 50 sessões exportadas com timestamps |
| [VM Setup](docs/VM-environment-config.md) | Configuração do ambiente de produção |
| [CI/CD Pipeline](docs/Pipeline-GithubActions-deployment-config.md) | Deploy automatizado com GitHub Actions |

---

**Orientador:** Professor Dr. Fábio Henrique Cabrini  
**Instituição:** Faculdade Engenheiro Salvador Arena