# 🐍 Source Code - Backend Python

> Código-fonte principal seguindo Clean Architecture

---

## 📋 Visão Geral

O backend foi desenvolvido com:

- **FastAPI** — Framework web assíncrono de alta performance
- **SQLAlchemy** — ORM para acesso ao banco de dados
- **Pydantic V2** — Validação e serialização de dados
- **Clean Architecture** — Separação de responsabilidades

---

## 🏗️ Estrutura de Camadas

```
src/
├── domain/           # Regras de negócio puras
├── application/      # Interfaces abstratas (contratos)
├── infrastructure/   # Implementações concretas
├── interface/        # API REST (FastAPI)
├── etl/              # Pipeline de ingestão de dados
├── config.py         # Configurações centralizadas
└── main.py           # Ponto de entrada da aplicação
```

### Diagrama de Dependências

```
┌─────────────────────────────────────────────────────┐
│  INTERFACE (FastAPI)                                │
│  → Recebe HTTP, valida schemas, retorna JSON        │
├─────────────────────────────────────────────────────┤
│  APPLICATION (Interfaces)                           │
│  → Define contratos abstratos (IRepository)         │
├─────────────────────────────────────────────────────┤
│  DOMAIN (Entities)                                  │
│  → Regras de negócio, validações, enums            │
├─────────────────────────────────────────────────────┤
│  INFRASTRUCTURE (MySQL, Cache)                      │
│  → Implementa interfaces, acesso a dados           │
└─────────────────────────────────────────────────────┘
        ↑ Dependências apontam para dentro
```

---

## 📁 Arquivos por Camada

### 🔹 Domain (`domain/`)

Contém **regras de negócio puras** sem dependências externas:

| Arquivo | Conteúdo |
|---------|----------|
| `entities.py` | Classes `Operadora`, `DespesaFinanceira`, `CNPJ` |
| `__init__.py` | Exports públicos |

```python
# Exemplo de Entity
class Operadora(BaseModel):
    cnpj: str
    razao_social: str
    registro_ans: Optional[str]
    modalidade: Optional[ModalidadeOperadora]
    uf: Optional[str]
    
    @field_validator('cnpj')
    def validar_cnpj(cls, v):
        if not v.isdigit() or len(v) != 14:
            raise ValueError('CNPJ inválido')
        return v
```

### 🔹 Application (`application/`)

Define **contratos abstratos** que Infrastructure implementa:

| Arquivo | Conteúdo |
|---------|----------|
| `interfaces.py` | `IOperadoraRepository`, `IDespesaRepository` |

```python
# Exemplo de Interface
class IOperadoraRepository(ABC):
    @abstractmethod
    async def get_by_cnpj(self, cnpj: str) -> Optional[Operadora]:
        pass
    
    @abstractmethod
    async def list_all(self, page: int, limit: int) -> Tuple[List[Operadora], int]:
        pass
```

### 🔹 Infrastructure (`infrastructure/`)

**Implementações concretas** das interfaces:

| Subpasta/Arquivo | Conteúdo |
|------------------|----------|
| `database/connection.py` | Engine SQLAlchemy, session factory |
| `database/models.py` | Modelos ORM (`OperadoraORM`, `DespesaORM`) |
| `database/repositories.py` | Implementação de `IOperadoraRepository` |
| `observability.py` | Logging, métricas, tracing |
| `rate_limiter.py` | Configuração SlowAPI |

```python
# Exemplo de Repository
class OperadoraRepository(IOperadoraRepository):
    def __init__(self, db: Session):
        self.db = db
    
    async def get_by_cnpj(self, cnpj: str) -> Optional[Operadora]:
        result = self.db.query(OperadoraORM).filter_by(cnpj=cnpj).first()
        return result.to_entity() if result else None
```

### 🔹 Interface (`interface/`)

**Routers FastAPI** e schemas de validação:

| Subpasta/Arquivo | Conteúdo |
|------------------|----------|
| `api/operadoras.py` | Endpoints `/api/operadoras` |
| `api/estatisticas.py` | Endpoints `/api/estatisticas` |
| `api/schemas.py` | Pydantic schemas de request/response |

```python
# Exemplo de Router
@router.get("/operadoras", response_model=PaginatedResponse[OperadoraResponse])
async def listar_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    razao_social: Optional[str] = None,
    db: Session = Depends(get_db)
):
    repo = OperadoraRepository(db)
    items, total = await repo.list_all(page, limit, razao_social)
    return PaginatedResponse(items=items, total=total, page=page)
```

### 🔹 ETL (`etl/`)

**Pipeline de ingestão** de dados da ANS:

| Arquivo | Conteúdo |
|---------|----------|
| `downloader.py` | Download de arquivos CSV da ANS |
| `processor.py` | Parsing e validação de dados |
| `consolidator.py` | Agregação e consolidação |

```python
# Fluxo do ETL
async def run_etl(trimestres: int = 3):
    # 1. Download dos arquivos
    files = await download_demonstracoes(trimestres)
    
    # 2. Processamento
    for file in files:
        data = await process_csv(file)
        await validate_cnpjs(data)
    
    # 3. Consolidação
    await consolidate_and_insert(data)
    
    # 4. Export CSVs
    await export_csvs()
```

---

## 🔧 Configuração (`config.py`)

Configurações centralizadas com Pydantic Settings:

```python
class Settings(BaseSettings):
    # Banco de dados
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = ""
    DATABASE_NAME: str = "intuitive_care"
    
    # API
    API_DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Ambiente
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
```

---

## 🚀 Ponto de Entrada (`main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.interface.api import operadoras, estatisticas
from src.infrastructure.observability import setup_logging
from src.infrastructure.rate_limiter import limiter

app = FastAPI(
    title="API de Despesas ANS",
    version="1.0.0",
    docs_url="/docs"
)

# Middlewares
app.add_middleware(CORSMiddleware, ...)
app.state.limiter = limiter

# Routers
app.include_router(operadoras.router, prefix="/api")
app.include_router(estatisticas.router, prefix="/api")

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}
```

---

## 💡 Padrões e Boas Práticas

### Dependency Injection

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/operadoras/{cnpj}")
async def obter_operadora(
    cnpj: str,
    db: Session = Depends(get_db)  # Injetado automaticamente
):
    ...
```

### Error Handling

```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": request.state.request_id,
            "path": str(request.url.path)
        }
    )
```

### Logging Estruturado

```python
from loguru import logger

logger.bind(
    request_id=request_id,
    endpoint=request.url.path
).info("Request processed", status_code=200)
```

---

*Última atualização: Janeiro 2026*
