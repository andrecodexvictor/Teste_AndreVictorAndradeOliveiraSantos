# =============================================================
# Docker - Configurações de Containerização
# =============================================================

Este diretório contém todos os arquivos necessários para 
containerização do projeto.

## 📁 Estrutura

```
docker/
├── api/
│   ├── Dockerfile       # Imagem da API FastAPI
│   └── .dockerignore    # Arquivos ignorados no build
├── frontend/
│   ├── Dockerfile       # Imagem do Frontend Vue.js
│   ├── nginx.conf       # Configuração do Nginx com proxy
│   └── .dockerignore    # Arquivos ignorados no build
└── README.md            # Este arquivo
```

## 🌐 Rede Interna (Intranet Docker)

Para evitar problemas de DNS no Windows, usamos uma subnet fixa:

| Serviço | IP Fixo | Hostname | Aliases |
|---------|---------|----------|---------|
| MySQL | 172.28.1.10 | mysql | database, db |
| API | 172.28.1.20 | api | backend |
| Frontend | 172.28.1.30 | frontend | web |
| ETL | 172.28.1.40 | etl | - |

**Subnet:** `172.28.0.0/16`  
**Gateway:** `172.28.0.1`

### Por que IPs fixos?

1. **DNS do Docker no Windows** pode falhar em algumas configurações
2. **Evita conflitos** com redes corporativas e VPNs
3. **Conexões estáveis** entre containers
4. **Debugging facilitado** - sempre sabe onde cada serviço está

## 🚀 Uso Rápido

### Windows (PowerShell)

```powershell
# Na raiz do projeto
.\docker-start.ps1              # Inicia tudo
.\docker-start.ps1 -WithETL     # Inicia + carrega dados
.\docker-start.ps1 -Clean       # Reset completo
```

### Linux/Mac

```bash
chmod +x docker-start.sh
./docker-start.sh               # Inicia tudo
./docker-start.sh --with-etl    # Inicia + carrega dados
./docker-start.sh --clean       # Reset completo
```

### Docker Compose direto

```bash
docker-compose up -d
docker-compose --profile etl up etl  # Carregar dados
```

## 📊 Imagens

| Serviço | Base Image | Tamanho Final |
|---------|------------|---------------|
| API | python:3.11-slim | ~200MB |
| Frontend | nginx:alpine | ~25MB |

## 🔧 Configuração

As variáveis de ambiente são definidas em:
- `config/env/.env.example` - Template
- `config/env/.env.docker` - Valores para Docker

## 🐛 Troubleshooting

### "Não consigo conectar ao MySQL"

```powershell
# Verifica se MySQL está saudável
docker inspect --format='{{.State.Health.Status}}' intuitive_care_mysql

# Testa conexão direta
docker exec -it intuitive_care_mysql mysql -u root -pintuitive_care_2024 -e "SELECT 1"
```

### "API não responde"

```powershell
# Verifica logs
docker-compose logs api

# Testa conectividade interna
docker exec intuitive_care_api curl -s http://172.28.1.10:3306 || echo "MySQL acessível"
```

### "Frontend não carrega dados"

```powershell
# Verifica se nginx está fazendo proxy
docker exec intuitive_care_frontend curl -s http://172.28.1.20:8000/api/health
```

### Limpar tudo e recomeçar

```powershell
docker-compose down -v
docker system prune -f
.\docker-start.ps1 -Clean -WithETL
```
