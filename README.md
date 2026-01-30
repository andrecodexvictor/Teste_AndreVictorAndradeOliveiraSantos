# 🏥 Meu Projeto: API de Análise de Despesas de Operadoras

> **Olá!** Esse é o meu projeto para o Teste de Estágio da Intuitive Care.
> Aqui eu documento não só *o que* eu fiz, mas principalmente *por que* tomei cada decisão.

---

## 👋 Sobre Este Projeto

Eu construí uma **API REST completa** para analisar despesas de operadoras de planos de saúde, consumindo dados públicos da ANS. O projeto inclui:

- **Backend** em Python/FastAPI com arquitetura limpa
- **Frontend** em Vue.js com dashboard e gráficos
- **ETL** para baixar, processar e validar dados da ANS
- **Banco de dados** MySQL com queries analíticas

**Por que essas tecnologias?** Explico cada escolha mais abaixo! 👇

---

## 🎯 O Que Eu Construí

| Componente | O Que Faz | Status |
|------------|-----------|--------|
| 📥 **ETL** | Baixa dados da ANS, valida CNPJs, consolida trimestres | ✅ Pronto |
| 🔌 **API** | 4 endpoints RESTful com documentação automática | ✅ Pronto |
| 🖥️ **Frontend** | Dashboard com gráficos e tabela paginada | ✅ Pronto |
| 🗄️ **Banco** | Schema MySQL + 3 queries analíticas | ✅ Pronto |
| 📊 **Observabilidade** | Logging estruturado, métricas, health check | ✅ Pronto |
| 🧪 **Testes** | Suite pytest com fixtures | ✅ Estrutura Pronta |

---

## 🏗️ Por Que Escolhi Clean Architecture?

Quando comecei o projeto, pensei: *"Qual arquitetura me permite mudar de banco de dados sem reescrever a API?"*

A resposta foi **Clean Architecture**. Veja como organizei:

```
src/
├── domain/          # 💎 O coração: regras de negócio puras
│   └── entities.py  # Operadora, Despesa, CNPJ (sem dependências!)
│
├── application/     # 📋 Orquestração: o que o sistema FAZ
│   └── interfaces.py # Contratos abstratos (Repository Pattern)
│
├── infrastructure/  # 🔧 Implementações concretas
│   └── database/    # SQLAlchemy, MySQL
│
├── interface/       # 🌐 Como o mundo externo interage
│   └── api/         # FastAPI routers
│
└── etl/             # 📥 Pipeline de ingestão de dados
```

**O benefício prático?** Se amanhã eu precisar trocar MySQL por PostgreSQL, só mudo os arquivos em `infrastructure/`. O resto do código nem percebe.

---

## 🛠️ Minhas Escolhas Técnicas (e Por Quê)

### FastAPI ao invés de Flask

Eu poderia ter usado Flask (que já conheço bem), mas escolhi FastAPI porque:

1. **Documentação automática**: Swagger UI gerado sem escrever uma linha
2. **Validação nativa**: Pydantic valida requests automaticamente
3. **Async nativo**: Preparado para escalar se precisar

*Trade-off aceito*: Curva de aprendizado inicial maior.

### MySQL ao invés de PostgreSQL

Sinceramente? **Familiaridade operacional**. Eu sei debugar MySQL mais rápido, e para ~5000 operadoras, as features avançadas do PostgreSQL não fariam diferença.

*Se o volume fosse maior*: PostgreSQL seria minha escolha pela performance em queries analíticas complexas.

### Paginação Offset ao invés de Cursor

Escolhi offset-based (`?page=1&limit=20`) porque:

- O frontend precisa mostrar "Página 3 de 15"
- Os dados são estáticos (atualizados trimestralmente)
- ~5000 registros não causam degradação perceptível

*Quando eu mudaria*: Se tivesse milhões de registros com alta frequência de inserção.

---

## 🚀 Como Executar

### Pré-requisitos

Você vai precisar de:
- Python 3.9 ou superior
- MySQL 8.0 (ou MariaDB 10.5+)
- Node.js 18+ (para o frontend)
- Git

### 1. Clone o Projeto

```bash
git clone https://github.com/andrecodexvictor/intuitive-Care---Healthtech-de-SaaS-Vertical-test.git
cd intuitive-Care---Healthtech-de-SaaS-Vertical-test
```

### 2. Configure o Backend

```bash
# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configure o Banco de Dados

```bash
# Crie o banco no MySQL
mysql -u root -p -e "CREATE DATABASE intuitive_care_test CHARACTER SET utf8mb4;"
```

Crie um arquivo `.env` na raiz:

```env
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=sua_senha_aqui
DATABASE_NAME=intuitive_care_test
API_DEBUG=true
LOG_LEVEL=INFO
```

### 4. Inicie a API

```bash
uvicorn src.main:app --reload --port 8000
```

Acesse a documentação em: **http://localhost:8000/docs** 🎉

### 5. Inicie o Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse o dashboard em: **http://localhost:5173** 🎉

---

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/operadoras` | Lista paginada com filtros |
| GET | `/api/operadoras/{cnpj}` | Detalhes de uma operadora |
| GET | `/api/operadoras/{cnpj}/despesas` | Histórico de despesas |
| GET | `/api/estatisticas` | Agregações e rankings |
| GET | `/health` | Health check |
| GET | `/metrics` | Métricas de performance |

### Exemplo de Uso

```bash
# Listar operadoras (página 1, 20 por página)
curl http://localhost:8000/api/operadoras?page=1&limit=20

# Buscar por nome
curl http://localhost:8000/api/operadoras?razao_social=UNIMED

# Ver estatísticas
curl http://localhost:8000/api/estatisticas
```

---

## 🧪 Rodando os Testes

```bash
pytest
```

---

## ⚖️ Trade-offs Que Eu Fiz

Aqui está um resumo honesto das decisões que envolvem compromissos:

| Decisão | O Que Ganhei | O Que Perdi |
|---------|--------------|-------------|
| Offset pagination | URLs simples, frontend fácil | Performance degrada com milhões |
| Cache em memória | Sem Redis pra instalar | Não escala horizontal |
| Manter dados inválidos | Transparência, auditoria | Frontend precisa filtrar |
| MySQL | Setup fácil, familiaridade | Menos features que PostgreSQL |

---

## 📁 Estrutura Completa do Projeto

```
├── src/
│   ├── main.py              # Entry point da API
│   ├── config.py            # Configurações centralizadas
│   ├── domain/              # Entidades de negócio
│   ├── application/         # Interfaces e contratos
│   ├── infrastructure/      # Implementações (DB, observabilidade)
│   ├── interface/           # Routers FastAPI
│   └── etl/                 # Pipeline de dados
├── frontend/                # Vue.js 3 + Vite
├── sql/                     # Schema e queries analíticas
├── tests/                   # Pytest suite
├── docs/                    # Postman collection
└── README.md                # Você está aqui! 👋
```

---

## 🔮 O Que Eu Faria Com Mais Tempo

1. **Executar ETL real**: Baixar dados atuais da ANS
2. **Aumentar cobertura de testes**: Meta de 80%+
3. **Docker Compose**: Subir tudo com um comando
4. **CI/CD**: GitHub Actions para testes automáticos
5. **Monitoramento**: Prometheus + Grafana

---

## 👤 Sobre Mim

Esse projeto foi desenvolvido como parte do processo seletivo para estágio na **Intuitive Care**.

Tentei mostrar não apenas que sei programar, mas que sei **tomar decisões técnicas fundamentadas** e **documentá-las claramente**.

Se você chegou até aqui, obrigado por ler! 🙏

---

*Última atualização: Janeiro 2026*
