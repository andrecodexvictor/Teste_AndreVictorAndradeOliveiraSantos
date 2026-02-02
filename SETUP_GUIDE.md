# 📖 Guia de Setup - Tutorial Detalhado

> **Documento completo** para executar o projeto do zero em qualquer ambiente.  
> **Última atualização:** Fevereiro 2026

---

## 📋 Índice

1. [Pré-requisitos](#-pré-requisitos)
2. [Opção 1: Docker (Recomendado)](#-opção-1-docker-recomendado)
3. [Opção 2: Instalação Manual](#-opção-2-instalação-manual)
4. [Verificação do Ambiente](#-verificação-do-ambiente)
5. [Comandos ETL](#-comandos-etl)
6. [Troubleshooting](#-troubleshooting)
7. [Estrutura de URLs](#-estrutura-de-urls)

---

## ✅ Pré-requisitos de Sistema

- [ ] Docker Desktop instalado e **rodando**
- [ ] Portas livres: **3000**, **8000**, **3307**
- [ ] Conexão com internet (para o ETL baixar dados)
- [ ] Mínimo 4GB RAM disponível
- [ ] Mínimo 2GB espaço em disco (dados + imagens Docker)

### 📦 O que NÃO precisa instalar
- ❌ Python
- ❌ Node.js
- ❌ MySQL
- ❌ Nenhuma dependência manual

---

## 🐳 Opção 1: Docker (Recomendado)

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/andrecodexvictor/Teste_AndreVictorAndradeOliveiraSantos
cd Teste_AndreVictorAndradeOliveiraSantos
```

### Passo 2: Iniciar os Containers

```bash
# Inicia MySQL + API + Frontend
docker-compose up -d

# Aguarde ~30 segundos para o MySQL inicializar
# Verifique o status:
docker-compose ps
```

**Saída esperada:**
```
NAME                  STATUS (health)   PORTS
intuitive_care_mysql  healthy           3306
intuitive_care_api    running           8000
intuitive_care_frontend running         3000
```

### Passo 3: Executar ETL (Carregar Dados)

```bash
# Executa o ETL (baixa e processa dados da ANS)
docker-compose --profile etl up etl

# Aguarde ~5 minutos (processa ~1.4M registros)
```

> ⚠️ **Importante:** O ETL precisa de internet para baixar dados da ANS (~500MB).

### Passo 4: Acessar a Aplicação

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🌐 **Dashboard** | http://localhost:3000 | Interface principal |
| 📡 **API REST** | http://localhost:8000 | Endpoints JSON |
| 📖 **Swagger Docs** | http://localhost:8000/docs | Documentação interativa |
| 💚 **Health Check** | http://localhost:8000/health | Status da API |

### Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f api

# Reiniciar a API após alterações
docker-compose restart api

# Parar todos os serviços
docker-compose down

# Reset completo (remove banco de dados)
docker-compose down -v

# Rebuild após alterações de código
docker-compose up -d --build
```

---

## 💻 Opção 2: Instalação Manual

### Passo 1: Clonar e Configurar Python

#### Windows (PowerShell)
```powershell
# Clone
git clone https://github.com/andrecodexvictor/Teste_AndreVictorAndradeOliveiraSantos
cd Teste_AndreVictorAndradeOliveiraSantos

# Ambiente virtual
python -m venv venv
.\venv\Scripts\Activate

# Dependências
pip install -r requirements.txt
```

#### Linux/macOS
```bash
# Clone
git clone https://github.com/andrecodexvictor/Teste_AndreVictorAndradeOliveiraSantos
cd Teste_AndreVictorAndradeOliveiraSantos

# Ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Dependências
pip install -r requirements.txt
```

### Passo 2: Configurar Banco de Dados MySQL

```sql
-- Conecte ao MySQL como root
mysql -u root -p

-- Criar database
CREATE DATABASE intuitive_care_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Criar usuário (opcional)
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'sua_senha_segura';
GRANT ALL PRIVILEGES ON intuitive_care_test.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

### Passo 3: Configurar Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto:

```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=intuitive_care_test
DATABASE_USER=root
DATABASE_PASSWORD=sua_senha

# API
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENVIRONMENT=development
```

### Passo 4: Criar Schema do Banco

```bash
# Executar schema SQL
mysql -u root -p intuitive_care_test < sql/schema.sql

# (Opcional) Adicionar índices de performance
mysql -u root -p intuitive_care_test < sql/migration_add_indexes.sql
```

### Passo 5: Executar ETL

```bash
# Ative o ambiente virtual se não estiver ativo
# Windows: .\venv\Scripts\Activate
# Linux: source venv/bin/activate

# Execute o ETL
python run_etl.py
```

### Passo 6: Iniciar API Backend

```bash
# Inicia a API em modo desenvolvimento
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Passo 7: Iniciar Frontend

```bash
# Em outro terminal
cd frontend

# Instalar dependências (primeira vez)
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

---

## ✅ Verificação do Ambiente

### Teste 1: Health Check da API

```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Teste 2: Listar Operadoras

```bash
curl http://localhost:8000/api/operadoras?limit=3
```

### Teste 3: Estatísticas Gerais

```bash
curl http://localhost:8000/api/estatisticas
```

### Teste 4: Query 3 (Operadoras Acima da Média)

```bash
curl http://localhost:8000/api/estatisticas/operadoras-acima-media?limit=5
```

**Resposta esperada:**
```json
[
  {
    "cnpj": "92693118000160",
    "razao_social": "BRADESCO SAÚDE S.A.",
    "total_trimestres": 38,
    "trimestres_acima_media": 33,
    "media_operadora": 3147140988.84,
    "total_despesas": 119591357576.0
  }
]
```

---

## 📥 Comandos ETL

### ETL Completo (Recomendado)

```bash
# Docker
docker-compose --profile etl up etl

# Manual
python run_etl.py
```

### ETL com Parâmetros

```bash
# Definir quantidade de trimestres (padrão: 4)
python run_etl.py --trimestres 8

# Apenas operadoras (sem despesas)
python run_etl.py --operadoras-only

# Forçar re-download
python run_etl.py --force-download
```

### Seed Rápido (Dados de Teste)

```bash
# Para desenvolvimento/testes rápidos
python seed_database.py
```

---

## 🔧 Troubleshooting

### Problema: "Connection refused" no Docker

**Causa:** API tentando conectar antes do MySQL estar pronto.

**Solução:**
```bash
# Aguarde o MySQL ficar healthy
docker-compose ps

# Se necessário, reinicie a API
docker-compose restart api
```

### Problema: "Access denied for user"

**Causa:** Senha incorreta no .env

**Solução:**
1. Verifique a senha no arquivo `.env`
2. Para Docker, a senha padrão é `adm@123`

### Problema: ETL demora muito

**Causa:** Download de ~500MB de dados da ANS

**Solução:**
- ETL inicial demora ~5-10 minutos
- Nas próximas execuções, dados são cacheados localmente

### Problema: Frontend não conecta na API

**Causa:** CORS ou proxy incorreto

**Solução Docker:**
- O Nginx já configura o proxy automaticamente
- Certifique-se de acessar via `http://localhost:3000`

**Solução Manual:**
- Configure `VITE_API_URL=http://localhost:8000` no frontend

### Problema: Queries muito lentas (~100s)

**Causa:** Índices não criados

**Solução:**
```bash
# Docker
docker exec -i intuitive_care_mysql mysql -uroot -padm@123 intuitive_care_test < sql/migration_add_indexes.sql

# Manual
mysql -u root -p intuitive_care_test < sql/migration_add_indexes.sql
```

---

## 🌐 Estrutura de URLs

### API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| GET | `/api/operadoras` | Lista operadoras (paginado) |
| GET | `/api/operadoras/{cnpj}` | Detalhes de operadora |
| GET | `/api/operadoras/{cnpj}/despesas` | Despesas de operadora |
| GET | `/api/estatisticas` | Estatísticas gerais |
| GET | `/api/estatisticas/distribuicao-uf` | Distribuição por UF |
| GET | `/api/estatisticas/operadoras-acima-media` | Query 3: Operadoras acima da média |

### Parâmetros de Query

```bash
# Paginação
GET /api/operadoras?page=1&limit=20

# Filtro por nome
GET /api/operadoras?razao_social=bradesco

# Filtro por CNPJ
GET /api/operadoras?cnpj=92693118

# Filtro por UF
GET /api/operadoras?uf=SP

# Query 3 com limite
GET /api/estatisticas/operadoras-acima-media?limit=10
```

---

## 📊 Arquitetura de Containers

```
┌──────────────────────────────────────────────────────────┐
│                    DOCKER NETWORK                         │
│                   (172.28.0.0/16)                         │
│                                                           │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│  │   MySQL     │   │    API      │   │  Frontend   │    │
│  │ 172.28.1.10 │   │ 172.28.1.20 │   │ 172.28.1.30 │    │
│  │   :3306     │   │   :8000     │   │    :80      │    │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘    │
│         │                 │                  │           │
│         └────────┬────────┴────────┬────────┘           │
│                  │                 │                     │
└──────────────────┼─────────────────┼─────────────────────┘
                   │                 │
              localhost:3306    localhost:3000
              localhost:8000
```

---

## 🎯 Comandos Rápidos

```bash
# Setup completo (Docker)
docker-compose up -d && docker-compose --profile etl up etl

# Ver logs
docker-compose logs -f

# Acessar MySQL
docker exec -it intuitive_care_mysql mysql -uroot -padm@123 intuitive_care_test

# Executar testes
docker exec intuitive_care_api pytest tests/ -v

# Rebuild tudo
docker-compose down -v && docker-compose up -d --build
```

---

**André Victor Andrade Oliveira Santos**  
*Fevereiro 2026*
