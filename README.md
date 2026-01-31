# 🏥 API de Análise de Despesas de Operadoras de Saúde

> **Teste Técnico para Estágio** — Intuitive Care  
> Este documento apresenta a solução desenvolvida, com foco nas decisões técnicas e justificativas adotadas.

---

## 📋 Sumário Executivo

Este projeto consiste em uma **API REST completa** para análise de despesas de operadoras de planos de saúde, utilizando dados públicos da ANS (Agência Nacional de Saúde Suplementar).

### Componentes Desenvolvidos

| Componente | Descrição | Status |
|------------|-----------|--------|
| **ETL** | Pipeline de ingestão: download, validação de CNPJs, consolidação de trimestres | ✅ Implementado |
| **API REST** | 4 endpoints RESTful com documentação OpenAPI automática | ✅ Implementado |
| **Frontend** | Dashboard Vue.js com visualizações e tabela paginada | ✅ Implementado |
| **Banco de Dados** | Schema MySQL + 3 queries analíticas conforme requisitos | ✅ Implementado |
| **Observabilidade** | Logging estruturado, métricas de performance, health check | ✅ Implementado |
| **Testes** | Suite pytest com 18 testes automatizados | ✅ Implementado |

---

## 🏗️ Arquitetura

Foi adotada a **Clean Architecture** para garantir separação de responsabilidades e facilitar manutenção futura.

### Estrutura de Camadas

```
src/
├── domain/          # Regras de negócio puras (sem dependências externas)
│   └── entities.py  # Operadora, Despesa, CNPJ
│
├── application/     # Orquestração e contratos
│   └── interfaces.py # Interfaces abstratas (Repository Pattern)
│
├── infrastructure/  # Implementações concretas
│   └── database/    # SQLAlchemy, MySQL
│
├── interface/       # Camada de apresentação
│   └── api/         # Routers FastAPI
│
└── etl/             # Pipeline de ingestão de dados
```

### Justificativa da Escolha

1. **Testabilidade**: Camada de Domain sem dependências possibilita testes unitários puros
2. **Manutenibilidade**: Migração de banco de dados afeta apenas a camada Infrastructure
3. **Clareza**: Responsabilidades bem definidas facilitam onboarding de novos desenvolvedores

---

## 🛠️ Stack Tecnológica

| Tecnologia | Justificativa |
|------------|---------------|
| **FastAPI** | Documentação automática, validação nativa com Pydantic, suporte async |
| **SQLAlchemy** | ORM maduro com suporte a múltiplos bancos de dados |
| **MySQL 8.0** | Familiaridade operacional, adequado ao volume do projeto |
| **Pydantic V2** | Performance 10x superior à V1, integração nativa com FastAPI |
| **Vue.js 3** | Composition API moderna, excelente developer experience |
| **Loguru** | Logging estruturado com API simplificada |

---

## 🚀 Instruções de Execução

## 🚀 Instruções de Execução

### Pré-requisitos

- **Python 3.10+** (Requisito atualizado para compatibilidade de tipos modernos)
- MySQL 8.0+
- Node.js 18+

### 1. Configuração do Ambiente

```bash
# Clone o repositório
git clone https://github.com/andrecodexvictor/intuitive-Care---Healthtech-de-SaaS-Vertical-test.git
cd intuitive-Care---Healthtech-de-SaaS-Vertical-test

# Ambiente virtual Python
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalação de dependências
pip install -r requirements.txt
```

### 2. Configuração do Banco de Dados

```bash
mysql -u root -p -e "CREATE DATABASE intuitive_care_test CHARACTER SET utf8mb4;"
```

Crie o arquivo `.env` na raiz do projeto:

```env
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=sua_senha
DATABASE_NAME=intuitive_care_test
API_DEBUG=false
LOG_LEVEL=INFO
```

### 3. Carga de Dados (ETL)

Este projeto inclui um pipeline ETL capaz de processar milhões de registros reais da ANS.

```bash
# Executa o pipeline completo (Download -> Processamento -> Inserção Otimizada)
# Duração estimada: ~10 minutos (1.4 Milhão de registros)
python run_etl.py
```

### 4. Execução da API

```bash
uvicorn src.main:app --reload --port 8000
```

**Documentação disponível em:** http://localhost:8000/docs

### 5. Execução do Frontend

```bash
cd frontend
npm install
npm run dev
```

**Dashboard disponível em:** http://localhost:5173

> **Nota:** O frontend está configurado para conectar em `http://127.0.0.1:8000` para evitar problemas de resolução de DNS no Windows.

---

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/operadoras` | Lista paginada com filtros |
| GET | `/api/operadoras/{cnpj}` | Detalhes de uma operadora |
| GET | `/api/operadoras/{cnpj}/despesas` | Histórico de despesas |
| GET | `/api/estatisticas` | Agregações e rankings |
| GET | `/health` | Verificação de saúde do serviço |
| GET | `/metrics` | Métricas de performance |

### Exemplos de Requisição

```bash
# Listar operadoras com paginação
curl "http://localhost:8000/api/operadoras?page=1&limit=20"

# Filtrar por razão social
curl "http://localhost:8000/api/operadoras?razao_social=UNIMED"

# Obter estatísticas gerais
curl "http://localhost:8000/api/estatisticas"
```

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Resultado esperado: 18 passed, 5 skipped
```

Os testes de integração são automaticamente ignorados quando o MySQL não está disponível.

---

## ⚖️ Trade-offs e Decisões

| Decisão | Benefício | Custo | Justificativa |
|---------|-----------|-------|---------------|
| **Bulk Insert** | Performance extrema (1.4M rows em 5min) | Maior uso de memória durante carga | Essencial para volume real de dados |
| Paginação Offset | URLs simples, cálculo de páginas direto | Performance degrada com alto volume | ~5000 registros é gerenciável |
| Cache em Memória | Sem dependências adicionais | Não escala horizontalmente | Instância única suficiente |
| Manter Dados Inválidos | Preservação para auditoria | Requer filtros no frontend | Transparência prioritária |
| MySQL | Setup simplificado, familiaridade | Menos features que PostgreSQL | Adequado ao caso de uso |

---

## 📁 Estrutura do Projeto

```
├── src/                     # Código-fonte backend
├── frontend/                # Vue.js 3 + Vite
├── sql/                     # Schema e queries analíticas
├── tests/                   # Suite de testes pytest
├── docs/                    # Postman collection
├── requirements.txt         # Dependências Python
├── run_etl.py               # Script de ingestão de dados
└── README.md                # Documentação principal
```

---

## 🔮 Melhorias Futuras

Com mais tempo disponível, implementaria:

1. **Docker Compose** para ambiente de desenvolvimento unificado
2. **CI/CD** com GitHub Actions
3. **Monitoramento** com Prometheus e Grafana
4. **Cache Distribuído** (Redis) para ambiente clusterizado

---

## 👤 Autor

**André Victor Andrade Oliveira Santos**

Este projeto foi desenvolvido como parte do processo seletivo para estágio na **Intuitive Care**.

O objetivo foi demonstrar não apenas habilidades técnicas de programação, mas também a capacidade de **tomar decisões técnicas fundamentadas** e **documentá-las de forma clara e profissional**.

---

*Última atualização: Janeiro 2026*
