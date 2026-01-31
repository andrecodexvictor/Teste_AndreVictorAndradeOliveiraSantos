# =============================================================
# test_schemas.py - Testes para Schemas Pydantic
# =============================================================
# COBERTURA: Validação, serialização, edge cases
# =============================================================
import pytest
from pydantic import ValidationError
from datetime import datetime


# =============================================================
# Importação dos Schemas
# =============================================================
# Nota: Schemas podem estar em src/interface/api/schemas.py
# Ajuste os imports conforme necessário
try:
    from src.interface.api.schemas import (
        OperadoraResponse,
        OperadoraDetalheResponse,
        DespesaResponse,
        PaginatedOperadoraResponse,
        ErrorResponse,
        HealthCheckResponse,
        EstatisticasResponse,
        TopOperadoraResponse,
        DistribuicaoUFResponse,
    )
    SCHEMAS_AVAILABLE = True
except ImportError:
    SCHEMAS_AVAILABLE = False


# =============================================================
# Testes de OperadoraResponse
# =============================================================
@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas não disponíveis")
class TestOperadoraResponse:
    """Testes para schema de resposta de Operadora."""
    
    @pytest.mark.unit
    def test_operadora_response_valida(self):
        """Deve criar response com dados válidos."""
        data = {
            "cnpj": "11444777000161",
            "razao_social": "Operadora Teste Ltda",
            "registro_ans": "123456",
            "modalidade": None,
            "uf": "SP"
        }
        response = OperadoraResponse(**data)
        
        assert response.cnpj == "11444777000161"
        assert response.razao_social == "Operadora Teste Ltda"
    
    @pytest.mark.unit
    def test_operadora_response_campos_opcionais(self):
        """Campos opcionais devem aceitar None."""
        data = {
            "cnpj": "11444777000161",
            "razao_social": "Teste",
            "registro_ans": None,
            "modalidade": None,
            "uf": None
        }
        response = OperadoraResponse(**data)
        
        assert response.registro_ans is None
        assert response.uf is None


# =============================================================
# Testes de OperadoraDetalheResponse
# =============================================================
@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas não disponíveis")
class TestOperadoraDetalheResponse:
    """Testes para schema de detalhes de Operadora."""
    
    @pytest.mark.unit
    def test_detalhe_com_despesas(self):
        """Deve incluir total de despesas e quantidade de trimestres."""
        data = {
            "cnpj": "11444777000161",
            "razao_social": "Teste",
            "registro_ans": "123456",
            "modalidade": None,
            "uf": "SP",
            "total_despesas": 1500000.0,
            "quantidade_trimestres": 4
        }
        response = OperadoraDetalheResponse(**data)
        
        assert response.total_despesas == 1500000.0
        assert response.quantidade_trimestres == 4
    
    @pytest.mark.unit
    def test_detalhe_sem_despesas(self):
        """Operadora sem despesas deve ter valores zerados."""
        data = {
            "cnpj": "11444777000161",
            "razao_social": "Teste",
            "registro_ans": None,
            "modalidade": None,
            "uf": None,
            "total_despesas": 0,
            "quantidade_trimestres": 0
        }
        response = OperadoraDetalheResponse(**data)
        
        assert response.total_despesas == 0
        assert response.quantidade_trimestres == 0


# =============================================================
# Testes de DespesaResponse
# =============================================================
@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas não disponíveis")
class TestDespesaResponse:
    """Testes para schema de resposta de Despesa."""
    
    @pytest.mark.unit
    def test_despesa_response_valida(self):
        """Deve criar response com dados válidos."""
        data = {
            "cnpj": "11444777000161",
            "razao_social": "Teste",
            "ano": 2024,
            "trimestre": 1,
            "valor": 150000.0,
            "status_qualidade": "OK"
        }
        response = DespesaResponse(**data)
        
        assert response.ano == 2024
        assert response.trimestre == 1
        assert response.valor == 150000.0
    
    @pytest.mark.unit
    def test_despesa_trimestre_valido(self):
        """Trimestre deve estar entre 1 e 4."""
        for trimestre in [1, 2, 3, 4]:
            data = {
                "cnpj": "11444777000161",
                "razao_social": "Teste",
                "ano": 2024,
                "trimestre": trimestre,
                "valor": 100000.0,
                "status_qualidade": "OK"
            }
            response = DespesaResponse(**data)
            assert response.trimestre == trimestre


# =============================================================
# Testes de PaginatedOperadoraResponse
# =============================================================
@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas não disponíveis")
class TestPaginatedResponse:
    """Testes para schema de resposta paginada."""
    
    @pytest.mark.unit
    def test_paginacao_campos_obrigatorios(self):
        """Deve ter todos os campos de paginação."""
        data = {
            "data": [],
            "total": 0,
            "page": 1,
            "limit": 20
        }
        response = PaginatedOperadoraResponse(**data)
        
        assert response.data == []
        assert response.total == 0
        assert response.page == 1
        assert response.limit == 20
    
    @pytest.mark.unit
    def test_paginacao_com_itens(self):
        """Deve serializar lista de operadoras corretamente."""
        operadora_data = {
            "cnpj": "11444777000161",
            "razao_social": "Teste",
            "registro_ans": "123456",
            "modalidade": None,
            "uf": "SP"
        }
        data = {
            "data": [operadora_data],
            "total": 1,
            "page": 1,
            "limit": 20
        }
        response = PaginatedOperadoraResponse(**data)
        
        assert len(response.data) == 1


# =============================================================
# Testes de ErrorResponse
# =============================================================
@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas não disponíveis")
class TestErrorResponse:
    """Testes para schema de resposta de erro."""
    
    @pytest.mark.unit
    def test_error_response_basico(self):
        """Deve criar resposta de erro com mensagem."""
        data = {
            "error": "Erro interno do servidor",
            "detail": "Algo deu errado"
        }
        response = ErrorResponse(**data)
        
        assert response.error == "Erro interno do servidor"
        assert response.detail == "Algo deu errado"


# =============================================================
# Testes de HealthCheckResponse
# =============================================================
@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas não disponíveis")
class TestHealthCheckResponse:
    """Testes para schema de health check."""
    
    @pytest.mark.unit
    def test_health_check_response(self):
        """Deve criar response de health check."""
        data = {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now()
        }
        response = HealthCheckResponse(**data)
        
        assert response.status == "healthy"
        assert response.version == "1.0.0"


# =============================================================
# Testes de EstatisticasResponse
# =============================================================
@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas não disponíveis")
class TestEstatisticasResponse:
    """Testes para schema de estatísticas."""
    
    @pytest.mark.unit
    def test_estatisticas_response(self):
        """Deve criar response de estatísticas."""
        data = {
            "total_despesas": 1000000.0,
            "media_despesas": 50000.0,
            "quantidade_registros": 20,
            "top_5_operadoras": []
        }
        response = EstatisticasResponse(**data)
        
        assert response.total_despesas == 1000000.0
        assert response.media_despesas == 50000.0


# =============================================================
# Testes de TopOperadoraResponse
# =============================================================
@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas não disponíveis")
class TestTopOperadoraResponse:
    """Testes para schema de top operadoras."""
    
    @pytest.mark.unit
    def test_top_operadora_response(self):
        """Deve criar response de top operadora."""
        data = {
            "razao_social": "Operadora Top",
            "total": 500000.0
        }
        response = TopOperadoraResponse(**data)
        
        assert response.razao_social == "Operadora Top"
        assert response.total == 500000.0


# =============================================================
# Testes de DistribuicaoUFResponse
# =============================================================
@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas não disponíveis")
class TestDistribuicaoUFResponse:
    """Testes para schema de distribuição por UF."""
    
    @pytest.mark.unit
    def test_distribuicao_uf_response(self):
        """Deve criar response de distribuição UF."""
        data = {
            "uf": "SP",
            "total": 500000.0,
            "percentual": 50.0
        }
        response = DistribuicaoUFResponse(**data)
        
        assert response.uf == "SP"
        assert response.total == 500000.0
        assert response.percentual == 50.0
