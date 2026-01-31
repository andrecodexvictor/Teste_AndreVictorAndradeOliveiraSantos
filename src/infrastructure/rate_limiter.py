# =============================================================
# rate_limiter.py - Rate Limiting com SlowAPI
# =============================================================
# DECISÃO ARQUITETURAL:
# Implementar rate limiting para proteger a API contra:
# - Ataques DDoS
# - Scraping abusivo
# - Sobrecarga acidental
#
# TECNOLOGIA: SlowAPI (wrapper do limits + starlette)
# - Integração nativa com FastAPI
# - Suporte a múltiplos backends (memory, redis)
# - Decoradores simples para endpoints
# =============================================================
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from src.config import settings


def get_client_ip(request: Request) -> str:
    """
    Extrai IP do cliente considerando proxies reversos.
    
    ORDEM DE VERIFICAÇÃO:
    1. X-Forwarded-For (proxy reverso/load balancer)
    2. X-Real-IP (nginx)
    3. client.host (conexão direta)
    
    SEGURANÇA: Em produção, confie apenas em headers do seu proxy.
    """
    # Header padrão para proxies
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Pega o primeiro IP (cliente original)
        return forwarded_for.split(",")[0].strip()
    
    # Header alternativo (nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback: conexão direta
    return request.client.host if request.client else "unknown"


# =============================================================
# CONFIGURAÇÃO DO LIMITER
# =============================================================
# storage_uri: Onde armazenar contadores
# - "memory://": In-memory (bom para single instance)
# - "redis://localhost:6379": Redis (para múltiplas instâncias)
#
# DECISÃO: Usar memory por padrão, fácil migrar para Redis depois.
# =============================================================
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri="memory://",
    strategy="fixed-window",  # Alternativa: "moving-window" (mais preciso)
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Handler customizado para limite excedido.
    
    RETORNA:
    - HTTP 429 (Too Many Requests)
    - Mensagem amigável em português
    - Header Retry-After com tempo de espera
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit excedido",
            "detail": f"Você excedeu o limite de {settings.RATE_LIMIT_PER_MINUTE} requisições por minuto.",
            "retry_after": "60 segundos",
        },
        headers={
            "Retry-After": "60",
            "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
        }
    )


def setup_rate_limiter(app):
    """
    Configura rate limiter na aplicação FastAPI.
    
    DEVE ser chamado após criação do app, antes de registrar routers.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    # Middleware adiciona headers X-RateLimit-* em todas as respostas
    # app.add_middleware(SlowAPIMiddleware)  # Opcional: adiciona overhead
