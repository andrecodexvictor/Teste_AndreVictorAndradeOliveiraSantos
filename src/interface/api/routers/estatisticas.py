from __future__ import annotations
# =============================================================
# estatisticas.py - Router para Endpoints de Estatísticas
# =============================================================
# ARQUITETURA: Clean Architecture - Interface Layer
#
# Este router agrupa endpoints de agregação e analytics.
# São queries mais pesadas, então implementamos cache.
# =============================================================
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from functools import lru_cache
from datetime import datetime, timedelta
from typing import List

from src.infrastructure.database.connection import get_db
from src.infrastructure.database.repositories import DespesaRepository
from src.infrastructure.database.models import DespesaORM, OperadoraORM
from src.infrastructure.rate_limiter import limiter
from src.interface.api.schemas import (
    EstatisticasResponse,
    TopOperadoraResponse,
    DistribuicaoUFResponse,
    OperadoraAcimaMediaResponse,
)


router = APIRouter(
    prefix="/api/estatisticas",
    tags=["Estatísticas"],
)


# =============================================================
# CACHE DE ESTATÍSTICAS
# =============================================================
# DECISÃO: Usar cache em memória (lru_cache) para estatísticas.
# JUSTIFICATIVA:
# - Query de agregação é custosa (processa milhares de registros).
# - Dados atualizados trimestralmente (não precisa real-time).
# - Cache de 15 minutos é suficiente.
#
# TRADE-OFF:
# - Em produção com múltiplas instâncias, usaríamos Redis.
# - lru_cache funciona apenas em processo único.
# - Para este protótipo, é suficiente.
#
# IMPLEMENTAÇÃO:
# - Cache com timestamp (invalida após 15 min).
# - Simples mas efetivo para MVP.
# =============================================================
_cache_estatisticas = None
_cache_timestamp = None
_cache_acima_media = None
_cache_acima_media_timestamp = None
CACHE_TTL_MINUTES = 15


def get_cached_estatisticas():
    """Retorna estatísticas cacheadas ou None se expirado."""
    global _cache_estatisticas, _cache_timestamp
    
    if _cache_estatisticas is None:
        return None
    
    if datetime.now() - _cache_timestamp > timedelta(minutes=CACHE_TTL_MINUTES):
        _cache_estatisticas = None
        return None
    
    return _cache_estatisticas


def set_cached_estatisticas(data):
    """Armazena estatísticas no cache."""
    global _cache_estatisticas, _cache_timestamp
    _cache_estatisticas = data
    _cache_timestamp = datetime.now()


def get_cached_acima_media():
    """Retorna cache de operadoras acima da média."""
    global _cache_acima_media, _cache_acima_media_timestamp
    
    if _cache_acima_media is None:
        return None
    
    if datetime.now() - _cache_acima_media_timestamp > timedelta(minutes=CACHE_TTL_MINUTES):
        _cache_acima_media = None
        return None
    
    return _cache_acima_media


def set_cached_acima_media(data):
    """Armazena operadoras acima da média no cache."""
    global _cache_acima_media, _cache_acima_media_timestamp
    _cache_acima_media = data
    _cache_acima_media_timestamp = datetime.now()


# =============================================================
# GET /api/estatisticas - Estatísticas gerais
# =============================================================
@router.get(
    "",
    response_model=EstatisticasResponse,
    summary="Estatísticas agregadas de despesas",
    description="""
    Retorna estatísticas agregadas de todas as despesas.
    
    **Inclui:**
    - Total geral de despesas
    - Média por registro
    - Quantidade total de registros
    - Top 5 operadoras com maiores despesas
    
    **Cache:**
    Resultados são cacheados por 15 minutos para melhor performance.
    
    **Rate Limit:** 50 requisições/minuto por IP (query pesada)
    """,
)
@limiter.limit("50/minute")
async def obter_estatisticas(
    request: Request,  # Required for rate limiter
    db: Session = Depends(get_db),
):
    """
    Calcula estatísticas gerais de despesas.
    
    PERFORMANCE:
    - Query agrega todos os registros (pode ser lenta).
    - Cache de 15 min evita recálculo desnecessário.
    
    DECISÃO: Calcular na hora (com cache) ao invés de pré-calcular.
    JUSTIFICATIVA:
    - Dados mudam apenas na ingestão (uma vez por trimestre).
    - Pré-calcular adicionaria complexidade (tabela materializada).
    - Cache simples resolve para este volume (~10K registros).
    """
    # Tenta cache primeiro
    cached = get_cached_estatisticas()
    if cached:
        return cached
    
    # Calcula estatísticas
    repo = DespesaRepository(db)
    stats = await repo.get_estatisticas_gerais()
    
    result = EstatisticasResponse(
        total_despesas=stats["total_despesas"],
        media_despesas=stats["media_despesas"],
        quantidade_registros=stats["quantidade_registros"],
        top_5_operadoras=[
            TopOperadoraResponse(**op) for op in stats["top_5_operadoras"]
        ],
    )
    
    # Armazena no cache
    set_cached_estatisticas(result)
    
    return result


# =============================================================
# GET /api/estatisticas/distribuicao-uf - Por estado
# =============================================================
@router.get(
    "/distribuicao-uf",
    response_model=List[DistribuicaoUFResponse],
    summary="Distribuição de despesas por UF",
    description="""
    Retorna a distribuição de despesas por UF (estado).
    
    Útil para gráficos de pizza/barra no frontend.
    
    **Ordenação:** Por total de despesas (maior primeiro).
    
    **Rate Limit:** 50 requisições/minuto por IP (query pesada)
    """,
)
@limiter.limit("50/minute")
async def obter_distribuicao_uf(
    request: Request,  # Required for rate limiter
    db: Session = Depends(get_db),
):
    """
    Calcula distribuição de despesas por UF.
    
    QUERY:
    SELECT uf, SUM(valor) as total
    FROM despesas d
    JOIN operadoras o ON d.cnpj = o.cnpj
    GROUP BY uf
    ORDER BY total DESC
    """
    # Query com JOIN para pegar UF da operadora
    results = (
        db.query(
            OperadoraORM.uf,
            func.sum(DespesaORM.valor).label("total"),
        )
        .join(DespesaORM, OperadoraORM.cnpj == DespesaORM.cnpj)
        .group_by(OperadoraORM.uf)
        .order_by(desc(func.sum(DespesaORM.valor)))
        .all()
    )
    
    # Calcula total geral para percentuais
    total_geral = sum(r.total for r in results if r.total)
    
    return [
        DistribuicaoUFResponse(
            uf=r.uf or "N/A",
            total=float(r.total or 0),
            percentual=round((r.total / total_geral * 100) if total_geral else 0, 2),
        )
        for r in results
    ]


# =============================================================
# GET /api/estatisticas/operadoras-acima-media - Query 3
# =============================================================
@router.get(
    "/operadoras-acima-media",
    response_model=List[OperadoraAcimaMediaResponse],
    summary="Operadoras com despesas acima da média em 2+ trimestres",
    description="""
    **Query 3 dos requisitos:** Identifica operadoras que consistentemente
    ficaram acima da média de despesas do mercado.
    
    **Critério:** Operadoras que tiveram despesas acima da média geral
    em pelo menos 2 trimestres diferentes.
    
    **Uso:** Identificar operadoras com despesas consistentemente altas.
    
    **Cache:** Resultados são cacheados por 15 minutos.
    
    **Rate Limit:** 50 requisições/minuto por IP (query pesada)
    """,
)
@limiter.limit("50/minute")
async def obter_operadoras_acima_media(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 20,
):
    """
    Query 3: Operadoras acima da média em 2+ trimestres.
    
    ESTRATÉGIA:
    1. Calcula média geral de todas as despesas (valor > 0)
    2. Para cada operadora, conta trimestres acima da média
    3. Filtra somente operadoras com 2+ trimestres acima
    4. Ordena por total de despesas (maior primeiro)
    """
    # Tenta cache
    cached = get_cached_acima_media()
    if cached:
        return cached[:limit]
    
    # Subquery: média geral de despesas
    media_geral_query = db.query(func.avg(DespesaORM.valor)).filter(
        DespesaORM.valor > 0
    ).scalar() or 0
    
    # Query principal: operadoras com trimestres acima da média
    from sqlalchemy import case, literal
    
    results = (
        db.query(
            DespesaORM.cnpj,
            OperadoraORM.razao_social,
            func.count(DespesaORM.id).label("total_trimestres"),
            func.sum(
                case(
                    (DespesaORM.valor > media_geral_query, 1),
                    else_=0
                )
            ).label("trimestres_acima_media"),
            func.avg(DespesaORM.valor).label("media_operadora"),
            func.sum(DespesaORM.valor).label("total_despesas"),
        )
        .join(OperadoraORM, DespesaORM.cnpj == OperadoraORM.cnpj)
        .filter(DespesaORM.valor > 0)
        .group_by(DespesaORM.cnpj, OperadoraORM.razao_social)
        .having(
            func.sum(
                case(
                    (DespesaORM.valor > media_geral_query, 1),
                    else_=0
                )
            ) >= 2
        )
        .order_by(desc(func.sum(DespesaORM.valor)))
        .all()
    )
    
    response = [
        OperadoraAcimaMediaResponse(
            cnpj=r.cnpj,
            razao_social=r.razao_social,
            total_trimestres=r.total_trimestres,
            trimestres_acima_media=r.trimestres_acima_media,
            media_operadora=round(float(r.media_operadora or 0), 2),
            total_despesas=round(float(r.total_despesas or 0), 2),
        )
        for r in results
    ]
    
    # Cache
    set_cached_acima_media(response)
    
    return response[:limit]
