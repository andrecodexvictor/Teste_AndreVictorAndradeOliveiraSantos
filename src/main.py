# =============================================================
# main.py - Entry Point da Aplicação FastAPI
# =============================================================
# ARQUITETURA: Clean Architecture - Infraestrutura (Framework)
#
# Este arquivo é o ponto de entrada da aplicação.
# Responsabilidades:
# 1. Criar instância do FastAPI.
# 2. Configurar middleware (CORS, logging, errors).
# 3. Registrar routers.
# 4. Definir eventos de lifecycle (startup, shutdown).
#
# EXECUÇÃO:
# uvicorn src.main:app --reload --port 8000
#
# DOCUMENTAÇÃO AUTOMÁTICA:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - OpenAPI JSON: http://localhost:8000/openapi.json
# =============================================================
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
from loguru import logger
import sys

from src.config import settings
from src.infrastructure.database.connection import create_tables, engine
from src.interface.api.routers import operadoras, estatisticas
from src.interface.api.schemas import HealthCheckResponse, ErrorResponse


# =============================================================
# CONFIGURAÇÃO DE LOGGING (Loguru)
# =============================================================
# DECISÃO: Usar Loguru ao invés do logging padrão.
# JUSTIFICATIVA:
# - API mais simples: logger.info() vs logging.getLogger().info()
# - Output colorido no console (facilita debugging)
# - Rotação automática de arquivos de log
# - Captura automática de exceptions com traceback
# =============================================================
logger.remove()  # Remove handler padrão
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True,
)

# Log para arquivo (opcional, descomente se quiser)
# logger.add(
#     "logs/app_{time}.log",
#     rotation="500 MB",
#     retention="10 days",
#     level=settings.LOG_LEVEL,
# )


# =============================================================
# LIFECYCLE EVENTS (Startup e Shutdown)
# =============================================================
# DECISÃO: Usar asynccontextmanager (FastAPI moderno).
# JUSTIFICATIVA:
# - Substitui on_startup/on_shutdown deprecated.
# - Garantia de cleanup com try/finally.
# - Permite inicialização de recursos async.
# =============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia ciclo de vida da aplicação.
    
    STARTUP:
    - Cria tabelas do banco (se não existirem).
    - Loga início da aplicação.
    
    SHUTDOWN:
    - Fecha conexões do banco.
    - Loga encerramento.
    """
    # === STARTUP ===
    logger.info("🚀 Iniciando aplicação...")
    logger.info(f"📊 Modo debug: {settings.API_DEBUG}")
    logger.info(f"💾 Banco de dados: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")
    
    # Cria tabelas (em dev; produção usaria migrations)
    try:
        create_tables()
        logger.info("✅ Tabelas do banco criadas/verificadas")
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível criar tabelas: {e}")
        logger.warning("   Verifique se o MySQL está rodando e o banco existe")
    
    yield  # Aplicação roda aqui
    
    # === SHUTDOWN ===
    logger.info("🔌 Encerrando aplicação...")
    engine.dispose()  # Fecha pool de conexões
    logger.info("👋 Aplicação encerrada com sucesso")


# =============================================================
# CRIAÇÃO DA APLICAÇÃO FASTAPI
# =============================================================
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="""
    ## API de Análise de Despesas de Operadoras de Planos de Saúde
    
    Esta API fornece acesso aos dados de despesas das operadoras
    de planos de saúde registradas na ANS (Agência Nacional de Saúde Suplementar).
    
    ### Funcionalidades:
    
    * **Operadoras**: Listagem, busca e detalhes de operadoras
    * **Despesas**: Histórico de despesas por operadora
    * **Estatísticas**: Agregações e rankings
    
    ### Trade-offs Técnicos:
    
    * **Paginação**: Offset-based (simples, adequado para ~5000 operadoras)
    * **Cache**: In-memory para estatísticas (TTL 15 min)
    * **Banco**: MySQL 8.0 com SQLAlchemy ORM
    """,
    lifespan=lifespan,
    docs_url=None,  # Desabilitado - usando /docs customizado
    redoc_url=None,  # Desabilitado
    openapi_url=None,  # Desabilitado
)


# =============================================================
# MIDDLEWARE: CORS
# =============================================================
# DECISÃO: Permitir todas as origens em desenvolvimento.
# JUSTIFICATIVA:
# - Facilita testes com frontend local (localhost:5173).
# - Em produção, restringir aos domínios conhecidos.
#
# CUIDADO: Em produção, trocar allow_origins=["*"] por lista específica!
# =============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restringir em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================
# MIDDLEWARE: Logging de Requests
# =============================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Loga todas as requisições HTTP.
    
    Útil para debugging e auditoria.
    Mostra: método, path, tempo de resposta.
    """
    start_time = datetime.now()
    
    # Processa requisição
    response = await call_next(request)
    
    # Calcula tempo de resposta
    process_time = (datetime.now() - start_time).total_seconds() * 1000
    
    # Loga requisição
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Tempo: {process_time:.2f}ms"
    )
    
    return response


# =============================================================
# HANDLER DE EXCEÇÕES GLOBAIS
# =============================================================
# DECISÃO: Capturar exceções não tratadas e retornar JSON padronizado.
# JUSTIFICATIVA:
# - Evita expor stack traces em produção.
# - Resposta consistente para o frontend.
# - Loga erro completo para debugging.
# =============================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para exceções não tratadas.
    
    COMPORTAMENTO:
    - Em DEBUG: Mostra mensagem e tipo da exceção.
    - Em PRODUÇÃO: Mostra mensagem genérica.
    - Sempre loga o erro completo.
    """
    logger.exception(f"Erro não tratado: {exc}")
    
    if settings.API_DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Erro interno do servidor",
                "detail": str(exc),
                "type": type(exc).__name__,
            },
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Erro interno do servidor",
                "detail": "Ocorreu um erro inesperado. Tente novamente mais tarde.",
            },
        )


# =============================================================
# REGISTRO DOS ROUTERS
# =============================================================
# Cada router agrupa endpoints relacionados.
# Prefixos são definidos nos próprios routers.
# =============================================================
app.include_router(operadoras.router)
app.include_router(estatisticas.router)


# =============================================================
# DOCUMENTAÇÃO FALLBACK (para Python < 3.10)
# =============================================================
# NOTA: Se usar Python 3.9, o Swagger automático pode falhar.
# Esta página HTML serve como fallback.
# =============================================================
from fastapi.responses import HTMLResponse

@app.get("/docs", include_in_schema=False)
async def api_docs():
    """Swagger UI customizado."""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API de Despesas - Documentação</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 40px; background: #1a1a2e; color: #eee; }
            h1 { color: #0ea5e9; }
            h2 { color: #38bdf8; border-bottom: 1px solid #333; padding-bottom: 10px; }
            .endpoint { background: #16213e; padding: 15px; border-radius: 8px; margin: 15px 0; }
            .method { display: inline-block; padding: 4px 12px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
            .get { background: #22c55e; color: #fff; }
            .post { background: #3b82f6; color: #fff; }
            code { background: #0f172a; padding: 2px 6px; border-radius: 4px; }
            a { color: #38bdf8; }
            .desc { color: #94a3b8; margin-top: 8px; }
        </style>
    </head>
    <body>
        <h1>🏥 API de Análise de Despesas</h1>
        <p>Intuitive Care - Teste Técnico para Estágio</p>
        
        <h2>📋 Operadoras</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/operadoras</code>
            <div class="desc">Lista paginada de operadoras. Params: page, limit, razao_social, cnpj</div>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/operadoras/{cnpj}</code>
            <div class="desc">Detalhes de uma operadora específica</div>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/operadoras/{cnpj}/despesas</code>
            <div class="desc">Histórico de despesas de uma operadora. Params: ano, trimestre</div>
        </div>
        
        <h2>📊 Estatísticas</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/estatisticas</code>
            <div class="desc">Estatísticas gerais: total, média, top 5 operadoras</div>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/estatisticas/distribuicao-uf</code>
            <div class="desc">Distribuição de despesas por UF</div>
        </div>
        
        <h2>🔧 Utilitários</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/health</code>
            <div class="desc">Health check - verifica se a API está saudável</div>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/metrics</code>
            <div class="desc">Métricas de performance da API</div>
        </div>
        
        <hr style="margin: 30px 0; border-color: #333;">
        <p style="color: #666;">Versão 1.0.0 | <a href="/">Voltar</a></p>
    </body>
    </html>
    """)


# =============================================================
# ENDPOINTS UTILITÁRIOS (fora dos routers)
# =============================================================
@app.get(
    "/",
    summary="Raiz da API",
    description="Retorna informações básicas da API.",
    tags=["Utilitários"],
)
async def root():
    """
    Endpoint raiz - informações da API.
    
    Útil para verificar se a API está no ar.
    """
    return {
        "message": "API de Análise de Despesas - Intuitive Care",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Verifica se a API está saudável.",
    tags=["Utilitários"],
)
async def health_check():
    """
    Health check para monitoramento.
    
    usado por:
    - Load balancers (verificar se instância está saudável).
    - Kubernetes (liveness/readiness probes).
    - Sistemas de monitoramento.
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.API_VERSION,
        timestamp=datetime.now(),
    )


@app.get(
    "/metrics",
    summary="Métricas da API",
    description="Retorna métricas de performance e uso da API.",
    tags=["Utilitários"],
)
async def metrics_endpoint():
    """
    Endpoint de métricas para observabilidade.
    
    Retorna:
    - Total de requisições
    - Taxa de erros
    - Tempo médio de resposta
    - Distribuição por status code
    - Top endpoints
    """
    try:
        from src.infrastructure.observability import metrics
        return metrics.get_metrics()
    except ImportError:
        return {
            "error": "Módulo de observabilidade não disponível",
            "message": "Use o módulo completo para métricas avançadas"
        }


# =============================================================
# EXECUÇÃO DIRETA (para desenvolvimento)
# =============================================================
# Permite rodar: python -m src.main
# Em produção, use: uvicorn src.main:app
# =============================================================
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Iniciando servidor em modo desenvolvimento...")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Hot reload em desenvolvimento
        log_level="info",
    )
