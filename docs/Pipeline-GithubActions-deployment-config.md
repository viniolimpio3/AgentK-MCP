# 🚀 Deploy Automático com GitHub Actions

Este guia explica como configurar o deploy automático do AgentK-MCP para uma VM na AWS usando GitHub Actions.

## 📋 Pré-requisitos

1. **VM na AWS** com Ubuntu 40.04+ 
2. **Repositório no GitHub** com acesso de administrador
3. **Chave SSH** para acesso à VM
4. **Chave da OpenAI**

## 🔐 Configuração dos Secrets no GitHub

Vá em **Settings > Secrets and variables > Actions** do seu repositório e adicione:

| Secret | Valor | Descrição |
|--------|--------|-----------|
| `AWS_VM_SSH_KEY` | Sua chave SSH privada | Conteúdo completo do arquivo .pem |
| `AWS_VM_HOST` | IP público da VM | Ex: 54.123.45.67 |
| `AWS_VM_USER` | ubuntu | Usuário da VM (geralmente 'ubuntu') |

### Como obter a chave SSH privada:
```bash
# No Windows (PowerShell)
Get-Content C:\caminho\para\sua-chave.pem | Out-String

# No Linux/Mac
cat /caminho/para/sua-chave.pem
```

## 🎯 Como Funciona

### Deploy Automático
- ✅ **Trigger:** Push na branch `master`
- ✅ **Ação:** Build e deploy automático na VM
- ✅ **Health Check:** Verifica se a aplicação está funcionando
- ✅ **Logs:** Todos os passos são logados no GitHub

### Deploy Manual
- ✅ **Trigger:** Aba "Actions" > "Deploy to AWS VM" > "Run workflow"
- ✅ **Quando usar:** Para deploys fora do fluxo normal

### Rollback
- ✅ **Trigger:** Aba "Actions" > "Rollback Deployment" > "Run workflow"
- ✅ **Opção:** Pode especificar um commit específico ou voltar 1 commit

## 📊 Monitoramento

### Verificar Status da Aplicação:
```bash
# Na VM
docker-compose ps
docker-compose logs -f
```

### URLs da Aplicação:
- **Servidor MCP:** `http://SEU-IP:3333`
- **Cliente Web:** `http://SEU-IP:8501`

## 🛠️ Comandos Úteis na VM

```bash
# Verificar logs
docker-compose logs -f

# Restart manual
docker-compose restart

# Verificar saúde
curl http://localhost:3333/health
curl http://localhost:8501

# Limpar recursos Docker
docker system prune -f
```

## 🚨 Troubleshooting

### Deploy falhou?
1. Verifique os logs na aba "Actions" do GitHub
2. Verifique se os secrets estão corretos
3. Teste conexão SSH manualmente

### Aplicação não responde?
1. Verifique se os containers estão rodando: `docker-compose ps`
2. Verifique logs: `docker-compose logs -f`
3. Use o workflow de rollback se necessário