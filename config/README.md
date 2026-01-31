# =============================================================
# Config - Arquivos de Configuração
# =============================================================

Este diretório contém templates e configurações de ambiente
para diferentes cenários de deploy.

## 📁 Estrutura

```
config/
├── env/
│   ├── .env.example      # Template base (copiar para raiz)
│   ├── .env.development  # Configurações para dev local
│   ├── .env.docker       # Configurações para Docker Compose
│   └── .env.production   # Template para produção
└── README.md             # Este arquivo
```

## 🚀 Como Usar

### Desenvolvimento Local

```bash
# Copie o template de desenvolvimento
cp config/env/.env.development .env

# Edite com suas credenciais locais
nano .env  # ou notepad .env no Windows
```

### Docker Compose

O docker-compose.yml usa `config/env/.env.docker` automaticamente.
Não precisa copiar arquivos.

```bash
docker-compose --env-file config/env/.env.docker up -d
```

### Produção

⚠️ **NUNCA use os arquivos .env diretamente em produção!**

Use um gerenciador de secrets:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Kubernetes Secrets

## 🔒 Segurança

| Arquivo | Git | Descrição |
|---------|-----|-----------|
| `.env.example` | ✅ Commitar | Template sem dados sensíveis |
| `.env.development` | ✅ Commitar | Apenas defaults de dev |
| `.env.docker` | ✅ Commitar | Valores padrão do container |
| `.env.production` | ⚠️ Template | Nunca com dados reais |
| `.env` (raiz) | ❌ Ignorar | Dados locais do desenvolvedor |

## 📋 Variáveis Disponíveis

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_HOST` | Host do MySQL | localhost |
| `DATABASE_PORT` | Porta do MySQL | 3306 |
| `DATABASE_USER` | Usuário do MySQL | root |
| `DATABASE_PASSWORD` | Senha do MySQL | - |
| `DATABASE_NAME` | Nome do banco | intuitive_care_test |
| `API_DEBUG` | Modo debug | false |
| `ENVIRONMENT` | Ambiente | development |
| `CORS_ORIGINS` | Origens CORS | localhost:5173 |
| `RATE_LIMIT_PER_MINUTE` | Limite de req/min | 100 |
| `LOG_LEVEL` | Nível de log | INFO |
| `DATA_DIR` | Diretório de dados | ./data |
