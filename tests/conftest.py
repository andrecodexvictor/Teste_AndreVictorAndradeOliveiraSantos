# =============================================================
# conftest.py - Configuração Global de Testes
# =============================================================
# Pytest fixtures compartilhadas entre todos os testes
# 
# ARQUITETURA DE TESTES:
# - Unit tests: Mock do banco, testes rápidos
# - Integration tests: TestClient + banco real/mock
# - Fixtures factories para entidades
# =============================================================
import pytest
import sys
from pathlib import Path
from typing import Generator, List
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

# Adicionar src ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importações do projeto (após path fix)
from src.domain.entities import Operadora, DespesaFinanceira, CNPJ, StatusQualidade


# =============================================================
# CONFIGURAÇÃO ASSÍNCRONA
# =============================================================
@pytest.fixture(scope="session")
def anyio_backend():
    """Backend para testes assíncronos."""
    return "asyncio"


# =============================================================
# FIXTURES DE APLICAÇÃO
# =============================================================
@pytest.fixture
def app():
    """Aplicação FastAPI para testes."""
    from src.main import app
    return app


@pytest.fixture
def client(app):
    """
    TestClient para testes de integração HTTP.
    
    Uso:
        def test_endpoint(client):
            response = client.get("/api/operadoras")
            assert response.status_code == 200
    """
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c


@pytest.fixture
def async_client(app):
    """
    AsyncClient para testes assíncronos.
    
    Uso:
        @pytest.mark.asyncio
        async def test_endpoint(async_client):
            response = await async_client.get("/api/operadoras")
    """
    import httpx
    from httpx import ASGITransport
    return httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# =============================================================
# FIXTURES DE BANCO DE DADOS (MOCK)
# =============================================================
@pytest.fixture
def mock_db_session():
    """
    Mock da sessão do banco para testes unitários.
    
    Evita dependência de MySQL real.
    """
    session = MagicMock()
    session.query.return_value = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    return session


@pytest.fixture
def mock_operadora_repository():
    """
    Mock do OperadoraRepository para testes unitários.
    """
    repo = Mock()
    repo.list_all = AsyncMock(return_value=([], 0))
    repo.get_by_cnpj = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_despesa_repository():
    """
    Mock do DespesaRepository para testes unitários.
    """
    repo = Mock()
    repo.get_by_operadora = AsyncMock(return_value=[])
    repo.get_estatisticas_gerais = AsyncMock(return_value={
        "total_despesas": 0,
        "media_despesas": 0,
        "quantidade_registros": 0,
        "top_5_operadoras": []
    })
    return repo


# =============================================================
# FACTORY FIXTURES - Entidades de Domínio
# =============================================================
@pytest.fixture
def operadora_factory():
    """
    Factory para criar Operadoras de teste.
    
    Uso:
        def test_algo(operadora_factory):
            op = operadora_factory(razao_social="UNIMED")
    """
    def _create(
        cnpj: str = "11444777000161",
        razao_social: str = "Operadora Teste Ltda",
        registro_ans: str = "123456",
        modalidade = None,
        uf: str = "SP"
    ) -> Operadora:
        return Operadora(
            cnpj=cnpj,
            razao_social=razao_social,
            registro_ans=registro_ans,
            modalidade=modalidade,
            uf=uf
        )
    return _create


@pytest.fixture
def despesa_factory():
    """
    Factory para criar DespesaFinanceira de teste.
    """
    def _create(
        cnpj: str = "11444777000161",
        razao_social: str = "Operadora Teste Ltda",
        ano: int = 2024,
        trimestre: int = 1,
        valor: float = 100000.0,
        status_qualidade: StatusQualidade = StatusQualidade.OK
    ) -> DespesaFinanceira:
        return DespesaFinanceira(
            cnpj=cnpj,
            razao_social=razao_social,
            ano=ano,
            trimestre=trimestre,
            valor=valor,
            status_qualidade=status_qualidade
        )
    return _create


@pytest.fixture
def sample_operadoras_list(operadora_factory) -> List[Operadora]:
    """Lista de 10 operadoras para testes de paginação."""
    ufs = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "PE", "CE", "GO"]
    return [
        operadora_factory(
            cnpj=f"{10000000000000 + i:014d}",
            razao_social=f"Operadora Teste {i}",
            registro_ans=f"{100000 + i}",
            uf=ufs[i % len(ufs)]
        )
        for i in range(10)
    ]


@pytest.fixture
def sample_despesas_list(despesa_factory) -> List[DespesaFinanceira]:
    """Lista de despesas para múltiplos trimestres."""
    return [
        despesa_factory(ano=2024, trimestre=q, valor=100000.0 * q)
        for q in range(1, 5)
    ]


# =============================================================
# FIXTURES DE CNPJ
# =============================================================
@pytest.fixture
def valid_cnpj() -> str:
    """CNPJ válido para testes."""
    return "11444777000161"


@pytest.fixture
def invalid_cnpj() -> str:
    """CNPJ inválido para testes."""
    return "12345678901234"


@pytest.fixture
def formatted_cnpj() -> str:
    """CNPJ formatado com máscara."""
    return "11.444.777/0001-61"


# =============================================================
# FIXTURES DE CONFIGURAÇÃO
# =============================================================
@pytest.fixture
def mock_settings():
    """
    Mock das configurações para testes.
    
    Permite sobrescrever valores de configuração sem afetar produção.
    """
    with patch("src.config.settings") as mock:
        mock.DATABASE_HOST = "localhost"
        mock.DATABASE_PORT = 3306
        mock.DATABASE_NAME = "test_db"
        mock.API_DEBUG = True
        mock.ENVIRONMENT = "testing"
        mock.CORS_ORIGINS = "http://localhost:5173"
        mock.cors_origins_list = ["http://localhost:5173"]
        mock.RATE_LIMIT_PER_MINUTE = 1000  # Alto para testes
        mock.DEFAULT_PAGE_SIZE = 20
        mock.MAX_PAGE_SIZE = 100
        yield mock


# =============================================================
# FIXTURES PARA TESTES DE SEGURANÇA
# =============================================================
@pytest.fixture
def security_headers():
    """Headers de segurança esperados nas respostas."""
    return {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "X-XSS-Protection": "1; mode=block",
    }


# =============================================================
# MARCADORES CUSTOMIZADOS
# =============================================================
def pytest_configure(config):
    """Registra marcadores customizados."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "security: marks tests as security-related")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")

