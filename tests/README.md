# 🧪 Tests - Suite de Testes Automatizados

> Cobertura abrangente com pytest para garantir qualidade do código

---

## 📋 Visão Geral

A suite de testes cobre:

- **114 testes automatizados** (109 passando, 5 skipped)
- **~85% de cobertura** de código
- **7 categorias** de testes
- **Testes humanizados** para QA manual

---

## 🚀 Execução

### Todos os Testes

```bash
# Executar todos
pytest

# Com output verbose
pytest -v

# Com cobertura
pytest --cov=src --cov-report=term-missing
```

### Por Categoria (Markers)

```bash
# Testes unitários (rápidos)
pytest -m unit

# Testes de integração (requer MySQL)
pytest -m integration

# Testes de segurança
pytest -m security

# Testes lentos (performance)
pytest -m slow
```

### Arquivo Específico

```bash
pytest tests/test_health.py -v
pytest tests/test_security.py::TestRateLimiting -v
```

---

## 📁 Estrutura de Arquivos

```
tests/
├── conftest.py              # Fixtures compartilhadas
├── test_health.py           # Endpoints de health check
├── test_api_operadoras.py   # CRUD de operadoras
├── test_api_estatisticas.py # Endpoints de estatísticas
├── test_schemas.py          # Validação Pydantic
├── test_security.py         # Headers, rate limiting, CORS
├── test_integration.py      # Testes de integração
├── test_operadoras.py       # Testes de domínio
└── MANUAL_TESTS.md          # Testes humanizados
```

---

## 📊 Cobertura por Arquivo

| Arquivo | Testes | Descrição |
|---------|--------|-----------|
| test_health.py | 14 | `/health`, `/`, `/docs`, `/metrics` |
| test_security.py | 21 | Headers, rate limiting, CORS, sanitização |
| test_schemas.py | 13 | Validação de CNPJ, paginação, responses |
| test_api_operadoras.py | 19 | Listagem, filtros, paginação, erros |
| test_api_estatisticas.py | 11 | Agregações, cache, distribuição UF |
| test_integration.py | 18 | Repository, transactions, performance |
| test_operadoras.py | 18 | Entities, domain logic |
| **Total** | **114** | 109 passando, 5 skipped |

---

## 🔧 Fixtures (conftest.py)

### Cliente de Teste

```python
@pytest.fixture
def client():
    """Cliente HTTP para testar a API."""
    return TestClient(app)
```

### Banco de Dados de Teste

```python
@pytest.fixture
def db_session():
    """Session de banco com transação isolada."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    transaction.rollback()
    connection.close()
```

### Factories de Dados

```python
@pytest.fixture
def operadora_factory():
    """Factory para criar operadoras de teste."""
    def create(**kwargs):
        defaults = {
            "cnpj": "11222333000181",
            "razao_social": "Operadora Teste LTDA",
            "uf": "SP"
        }
        return Operadora(**{**defaults, **kwargs})
    return create
```

---

## 🏷️ Markers Disponíveis

Definidos em `pytest.ini`:

```ini
[pytest]
markers =
    unit: Testes unitários rápidos
    integration: Testes de integração (requer MySQL)
    security: Testes de segurança
    slow: Testes lentos (performance)
    e2e: Testes end-to-end
```

### Uso

```python
@pytest.mark.unit
def test_validar_cnpj():
    assert validar_cnpj("11222333000181") is True

@pytest.mark.integration
def test_buscar_operadora_banco():
    # Requer MySQL rodando
    ...

@pytest.mark.security
def test_rate_limiting():
    # Testa limite de requisições
    ...
```

---

## 🎯 Exemplos de Testes

### Teste de Health Check

```python
def test_health_check_sucesso(client):
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
```

### Teste de Segurança

```python
def test_security_headers(client):
    response = client.get("/api/operadoras")
    
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
```

### Teste de Paginação

```python
def test_paginacao_campos_obrigatorios(client):
    response = client.get("/api/operadoras?page=1&limit=10")
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
```

### Teste de Rate Limiting

```python
@pytest.mark.security
def test_rate_limit_excedido(client):
    # Faz muitas requisições rapidamente
    for _ in range(101):
        client.get("/api/operadoras")
    
    response = client.get("/api/operadoras")
    assert response.status_code == 429
    assert "Retry-After" in response.headers
```

---

## 📋 Testes Humanizados

O arquivo `MANUAL_TESTS.md` contém **50+ cenários** em linguagem natural para:

- Validação exploratória
- Onboarding de QA
- Documentação de comportamento esperado

### Formato

| ID | Cenário | Passos | Resultado Esperado | Status |
|----|---------|--------|-------------------|--------|
| HC-01 | Health check | GET /health | JSON com status: "healthy" | ⬜ |

---

## ⚙️ Configuração CI

O pipeline GitHub Actions executa:

```yaml
test:
  runs-on: ubuntu-latest
  services:
    mysql:
      image: mysql:8.0
      env:
        MYSQL_ROOT_PASSWORD: test
        MYSQL_DATABASE: test_db
  steps:
    - run: pytest --cov=src --cov-report=xml
```

---

## 💡 Boas Práticas Aplicadas

### AAA Pattern

```python
def test_exemplo():
    # Arrange - preparação
    operadora = create_operadora()
    
    # Act - execução
    result = buscar_operadora(operadora.cnpj)
    
    # Assert - verificação
    assert result.razao_social == operadora.razao_social
```

### Isolamento

- Cada teste é independente
- Transações com rollback automático
- Fixtures limpam estado

### Nomenclatura

- `test_<funcionalidade>_<cenario>`
- `test_listar_operadoras_sucesso`
- `test_listar_operadoras_lista_vazia`

---

## 🔍 Troubleshooting

### Testes de integração falhando

```bash
# Verificar se MySQL está rodando
docker-compose up -d mysql

# Verificar variáveis de ambiente
echo $DATABASE_HOST
```

### Testes de rate limiting falhando

```bash
# Limpar cache do rate limiter
pytest --forked  # Executa em processos separados
```

### Cobertura não calculada

```bash
pip install pytest-cov
pytest --cov=src --cov-report=html
# Abrir htmlcov/index.html
```

---

*Última atualização: Janeiro 2026*
