# 🚨 Resumo das Misconfigurations Intencionais Adicionadas

> **📅 Última revisão**: 05/11/2025  

## 📋 Análise Completa dos Arquivos de Teste

| # | Arquivo | Aplicação | Recursos K8s | Credenciais Expostas | Imagem sem Tag | Erro Semântico/Lógico |
|---|---------|-----------|-------------|---------------------|----------------|-----------------------|
| 1 | `1-orion.yaml` | FIWARE Orion IoT | Deployment, Service, HPA | DB_PASSWORD, API_KEY, dbpwd (em args) | fiware/orion-ld | Service selector: `app: orionlds` (Deployment usa `app: orionld`) |
| 2 | `2-frontend.yaml` | Frontend Nginx | Deployment | PASSWORD_SERVICE_HOST | nginxs | Imagem `nginxs` inválida (typo de `nginx`) |
| 3 | `3-mysql.yaml` | MySQL Database | Pod | MYSQL_ROOT_PASSWORD, MYSQL_PASSWORD | my-sql | Imagem `my-sql` não existe (deveria ser `mysql`) |
| 4 | `4-vllm.yaml` | Mock vLLM Server | Deployment | HUGGING_FACE_HUB_TOKEN, ADMIN_PASSWORD | python:3.9-slim | Comando `python5` inválido (não existe) |
| 5 | `5-nginx.yaml` | Nginx HTTPS Proxy | Service, RC | SSL_CERT_PASSWORD, DB_CONNECTION | ymqytw/nginxhttps | Path: `/hom/auto-reload-nginx.sh` (typo de `/home`) + Label mismatch (RC: `app: nginxs`, Service: `app: nginx`) |
| 6 | `6-selenium.yaml` | Selenium Grid Hub | Deployment, Service | GRID_HUB_PASSWORD, DATABASE_URL | selenium/hub | Service selector: `app: sellenium-hub` (typo - Deployment usa `app: selenium-hub`) |
| 7 | `7-elasticsearch.yaml` | Elasticsearch Cluster | Service, RC | ELASTIC_PASSWORD, KIBANA_PASSWORD | quay.io/pires/docker-elasticsearch-kubernetes | Env var path: `/variavel/run/secrets...` (typo de `/var/run`) |
| 8 | `8-newrelic.yaml` | New Relic Agent | DaemonSet | NEW_RELIC_LICENSE_KEY, API_SECRET | newrelic/infrastructure | Imagem correta (era `newrelic/infrastructure`, não `nrsysmond`), sem erros de sintaxe detectados no command |
| 9 | `9-storm.yaml` | Apache Storm Worker | Deployment | STORM_NIMBUS_PASSWORD | storm | Imagem `storm` (não `mattf/storm-trabalhador`) - sem erro evidente de nome de container |
| 10 | `10-mongodb.yaml` | MongoDB Database | Deployment, Service | MONGO_INITDB_ROOT_PASSWORD, MONGODB_URL (com credenciais) | mongo | Service selector: `app: nonexistent-mongodb` (Deployment usa `app: mongodb-app`) |

## 🎯 Tipos de Misconfigurations Implementadas

### 1. 🔓 **Credenciais Expostas** (10/10 arquivos)
- **Senhas hardcoded** em variáveis de ambiente
- **Tokens de API** em plain text (ex: `HUGGING_FACE_HUB_TOKEN`, `API_KEY`)
- **Strings de conexão** com credenciais embutidas (ex: `MONGODB_URL`, `DB_CONNECTION`)
- **Chaves de licença** expostas (ex: `NEW_RELIC_LICENSE_KEY`)
- **Senhas em argumentos** (ex: arquivo 1 com `-dbpwd` nos args)

### 2. 🏷️ **Imagens sem Tag** (10/10 arquivos)
- Remoção de tags específicas das imagens
- Uso de `latest` implícito em todas as imagens
- **Risco**: Versões inconsistentes entre deployments
- **Exemplos**: `mongo`, `nginx`, `selenium/hub`, `fiware/orion-ld`, `python:3.9-slim`, `storm`

### 3. ⚠️ **Erros Semânticos/Lógicos** (9/10 arquivos)
> Configurações sintaticamente válidas, mas semanticamente incorretas que causam falhas em runtime

#### 3.1. **Label Mismatch (Selector Inválido)** - 4 ocorrências
- **Arquivo 1**: Service selector `app: orionlds` ≠ Deployment `app: orionld`
- **Arquivo 5**: ReplicationController `app: nginxs` ≠ Service `app: nginx`
- **Arquivo 6**: Service selector `app: sellenium-hub` (typo) ≠ Deployment `app: selenium-hub`
- **Arquivo 10**: Service selector `app: nonexistent-mongodb` ≠ Deployment `app: mongodb-app`

#### 3.2. **Imagens Inválidas/Typos** - 2 ocorrências
- **Arquivo 2**: Imagem `nginxs` (typo de `nginx`)
- **Arquivo 3**: Imagem `my-sql` (não existe, deveria ser `mysql`)

#### 3.3. **Comandos/Paths Inválidos** - 2 ocorrências
- **Arquivo 4**: Comando `python5` (não existe, deveria ser `python` ou `python3`)
- **Arquivo 5**: Path `/hom/auto-reload-nginx.sh` (typo de `/home`)

#### 3.4. **Variáveis de Ambiente com Paths Incorretos** - 1 ocorrência
- **Arquivo 7**: `KUBERNETES_CA_CERTIFICATE_FILE: /variavel/run/secrets...` (typo de `/var/run`)

## 🎯 **Como Usar os Testes**

1. **Detecção de credenciais** - AgentK identifica senhas expostas
2. **Validação de imagens** - Sugere uso de tags específicas  
3. **Correção de erros** - Identifica valores inválidos e typos
4. **Boas práticas** - Recomenda Secrets e ConfigMaps

### Detalhamento por Gravidade:

| Gravidade | Tipo | Quantidade | Impacto |
|-----------|------|------------|---------|
| 🔴 **Crítica** | Credenciais expostas | 20+ | Vazamento de senhas, tokens, conexões |
| 🟡 **Alta** | Label mismatch | 4 | Services não conseguem rotear tráfego |
| 🟡 **Alta** | Imagens inválidas | 2 | Falha no pull da imagem |
| 🟠 **Média** | Imagens sem tag | 10 | Inconsistência de versões |
| 🟠 **Média** | Comandos inválidos | 2 | Falha na inicialização do container |
| 🟢 **Baixa** | Typos em paths | 2 | Possível falha em runtime |

## � **Detalhamento das Misconfigurations por Arquivo**

### 1️⃣ `1-orion.yaml` - FIWARE Orion
- ❌ **Credenciais**: `DB_PASSWORD`, `API_KEY` em env + senha `-dbpwd` nos args
- ❌ **Imagem sem tag**: `fiware/orion-ld`
- ❌ **Label mismatch**: Service procura `app: orionlds` mas Deployment tem `app: orionld`

### 2️⃣ `2-frontend.yaml` - Frontend
- ❌ **Credenciais**: `PASSWORD_SERVICE_HOST: "123456"`
- ❌ **Imagem inválida**: `nginxs` (typo de `nginx`)

### 3️⃣ `3-mysql.yaml` - MySQL
- ❌ **Credenciais**: `MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD`
- ❌ **Imagem inválida**: `my-sql` (não existe, deveria ser `mysql`)

### 4️⃣ `4-vllm.yaml` - vLLM Server
- ❌ **Credenciais**: `HUGGING_FACE_HUB_TOKEN`, `ADMIN_PASSWORD`
- ❌ **Imagem sem tag**: `python:3.9-slim`
- ❌ **Comando inválido**: `python5` (não existe)

### 5️⃣ `5-nginx.yaml` - Nginx HTTPS
- ❌ **Credenciais**: `SSL_CERT_PASSWORD`, `DB_CONNECTION` (com credenciais)
- ❌ **Imagem sem tag**: `ymqytw/nginxhttps`
- ❌ **Path inválido**: `/hom/auto-reload-nginx.sh` (typo de `/home`)
- ❌ **Label mismatch**: RC usa `app: nginxs`, Service procura `app: nginx`

### 6️⃣ `6-selenium.yaml` - Selenium Hub
- ❌ **Credenciais**: `GRID_HUB_PASSWORD`, `DATABASE_URL`
- ❌ **Imagem sem tag**: `selenium/hub`
- ❌ **Label mismatch**: Service procura `app: sellenium-hub` (typo) mas Deployment tem `app: selenium-hub`

### 7️⃣ `7-elasticsearch.yaml` - Elasticsearch
- ❌ **Credenciais**: `ELASTIC_PASSWORD`, `KIBANA_PASSWORD`
- ❌ **Imagem sem tag**: `quay.io/pires/docker-elasticsearch-kubernetes`
- ❌ **Path inválido**: `KUBERNETES_CA_CERTIFICATE_FILE: /variavel/run/...` (typo de `/var/run`)

### 8️⃣ `8-newrelic.yaml` - New Relic
- ❌ **Credenciais**: `NEW_RELIC_LICENSE_KEY`, `API_SECRET`
- ❌ **Imagem sem tag**: `newrelic/infrastructure`
- ❌ **Sem erros semânticos detectados** 

### 9️⃣ `9-storm.yaml` - Apache Storm
- ❌ **Credenciais**: `STORM_NIMBUS_PASSWORD`
- ❌ **Imagem sem tag**: `storm`
- ❌ **Erro semântico detectado** (container name `storm-trabalhar` está incorreto)

### 🔟 `10-mongodb.yaml` - MongoDB
- ❌ **Credenciais**: `MONGO_INITDB_ROOT_PASSWORD`, `MONGODB_URL` (com credenciais embutidas)
- ❌ **Imagem sem tag**: `mongo`
- ❌ **Label mismatch**: Service procura `app: nonexistent-mongodb` mas Deployment tem `app: mongodb-app`

## 💬 **Template de Prompt para Testes**

Use o seguinte prompt padrão para avaliar cada arquivo YAML:

```
[service, deployment, whatever]: [nomes..]
Analise os arquivos YAML dos recursos Kubernetes acima, procurando por misconfigurations e possíveis incoerências, considerando o deploy em ambiente de produção.

Verifique se as configurações estão corretas de acordo com as especificações do Kubernetes e identifique qualquer problema que possa comprometer a funcionalidade ou coerência com as boas práticas.

Para cada problema encontrado, sugira uma correção específica.
```