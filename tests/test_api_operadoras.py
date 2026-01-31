# =============================================================
# test_api_operadoras.py - Testes de Integração da API de Operadoras
# =============================================================
# COBERTURA: Endpoints HTTP, paginação, filtros, erros
# ESTRATÉGIA: TestClient com mocks de repositório
# =============================================================
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from src.domain.entities import Operadora


# =============================================================
# Testes de Listagem (GET /api/operadoras)
# =============================================================
class TestListarOperadoras:
    """Testes para o endpoint de listagem de operadoras."""
    
    @pytest.mark.unit
    def test_listar_operadoras_sucesso(self, client, sample_operadoras_list):
        """Deve retornar lista paginada de operadoras."""
        # Mock do repositório
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.list_all = AsyncMock(return_value=(sample_operadoras_list[:5], 10))
            mock_repo_class.return_value = mock_repo
            
            response = client.get("/api/operadoras?page=1&limit=5")
            
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "total" in data
            assert data["total"] == 10
            assert len(data["data"]) == 5
            assert data["page"] == 1
            assert data["limit"] == 5
    
    @pytest.mark.unit
    def test_listar_operadoras_lista_vazia(self, client):
        """Deve retornar lista vazia quando não há operadoras."""
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.list_all = AsyncMock(return_value=([], 0))
            mock_repo_class.return_value = mock_repo
            
            response = client.get("/api/operadoras")
            
            assert response.status_code == 200
            data = response.json()
            assert data["data"] == []
            assert data["total"] == 0
    
    @pytest.mark.unit
    def test_listar_operadoras_paginacao_segunda_pagina(self, client, sample_operadoras_list):
        """Deve retornar corretamente a segunda página."""
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.list_all = AsyncMock(return_value=(sample_operadoras_list[5:], 10))
            mock_repo_class.return_value = mock_repo
            
            response = client.get("/api/operadoras?page=2&limit=5")
            
            assert response.status_code == 200
            data = response.json()
            assert data["page"] == 2
    
    @pytest.mark.unit
    def test_listar_operadoras_filtro_razao_social(self, client, operadora_factory):
        """Deve filtrar por razão social."""
        operadora = operadora_factory(razao_social="UNIMED SUL")
        
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.list_all = AsyncMock(return_value=([operadora], 1))
            mock_repo_class.return_value = mock_repo
            
            response = client.get("/api/operadoras?razao_social=UNIMED")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert "UNIMED" in data["data"][0]["razao_social"]
    
    @pytest.mark.unit
    def test_listar_operadoras_filtro_cnpj(self, client, operadora_factory):
        """Deve filtrar por CNPJ parcial."""
        operadora = operadora_factory(cnpj="11444777000161")
        
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.list_all = AsyncMock(return_value=([operadora], 1))
            mock_repo_class.return_value = mock_repo
            
            response = client.get("/api/operadoras?cnpj=11444")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
    
    @pytest.mark.unit
    def test_listar_operadoras_limite_maximo(self, client):
        """Deve respeitar limite máximo de itens por página."""
        response = client.get("/api/operadoras?limit=500")
        
        # FastAPI retorna 422 para validação
        assert response.status_code == 422
    
    @pytest.mark.unit
    def test_listar_operadoras_pagina_invalida(self, client):
        """Deve retornar erro para página inválida."""
        response = client.get("/api/operadoras?page=0")
        
        assert response.status_code == 422
    
    @pytest.mark.unit
    def test_listar_operadoras_limite_invalido(self, client):
        """Deve retornar erro para limite inválido."""
        response = client.get("/api/operadoras?limit=-1")
        
        assert response.status_code == 422


# =============================================================
# Testes de Detalhes (GET /api/operadoras/{cnpj})
# =============================================================
class TestObterOperadora:
    """Testes para o endpoint de detalhes de operadora."""
    
    @pytest.mark.unit
    def test_obter_operadora_sucesso(self, client, operadora_factory, despesa_factory, valid_cnpj):
        """Deve retornar detalhes da operadora."""
        operadora = operadora_factory(cnpj=valid_cnpj)
        despesas = [despesa_factory(cnpj=valid_cnpj, valor=100000.0)]
        
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_op_repo:
            with patch("src.interface.api.routers.operadoras.DespesaRepository") as mock_desp_repo:
                mock_op_repo.return_value.get_by_cnpj = AsyncMock(return_value=operadora)
                mock_desp_repo.return_value.get_by_operadora = AsyncMock(return_value=despesas)
                
                response = client.get(f"/api/operadoras/{valid_cnpj}")
                
                assert response.status_code == 200
                data = response.json()
                assert data["cnpj"] == valid_cnpj
                assert data["razao_social"] == operadora.razao_social
                assert "total_despesas" in data
    
    @pytest.mark.unit
    def test_obter_operadora_nao_encontrada(self, client, valid_cnpj):
        """Deve retornar 404 para operadora inexistente."""
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_repo:
            mock_repo.return_value.get_by_cnpj = AsyncMock(return_value=None)
            
            response = client.get(f"/api/operadoras/{valid_cnpj}")
            
            assert response.status_code == 404
            assert "não encontrada" in response.json()["detail"]
    
    @pytest.mark.unit
    def test_obter_operadora_sem_despesas(self, client, operadora_factory, valid_cnpj):
        """Deve retornar operadora com total_despesas = 0."""
        operadora = operadora_factory(cnpj=valid_cnpj)
        
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_op_repo:
            with patch("src.interface.api.routers.operadoras.DespesaRepository") as mock_desp_repo:
                mock_op_repo.return_value.get_by_cnpj = AsyncMock(return_value=operadora)
                mock_desp_repo.return_value.get_by_operadora = AsyncMock(return_value=[])
                
                response = client.get(f"/api/operadoras/{valid_cnpj}")
                
                assert response.status_code == 200
                data = response.json()
                assert data["total_despesas"] == 0
                assert data["quantidade_trimestres"] == 0


# =============================================================
# Testes de Despesas (GET /api/operadoras/{cnpj}/despesas)
# =============================================================
class TestListarDespesas:
    """Testes para o endpoint de despesas de operadora."""
    
    @pytest.mark.unit
    def test_listar_despesas_sucesso(self, client, operadora_factory, despesa_factory, valid_cnpj):
        """Deve retornar lista de despesas."""
        operadora = operadora_factory(cnpj=valid_cnpj)
        despesas = [
            despesa_factory(cnpj=valid_cnpj, ano=2024, trimestre=q, valor=100000.0 * q)
            for q in range(1, 5)
        ]
        
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_op_repo:
            with patch("src.interface.api.routers.operadoras.DespesaRepository") as mock_desp_repo:
                mock_op_repo.return_value.get_by_cnpj = AsyncMock(return_value=operadora)
                mock_desp_repo.return_value.get_by_operadora = AsyncMock(return_value=despesas)
                
                response = client.get(f"/api/operadoras/{valid_cnpj}/despesas")
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 4
    
    @pytest.mark.unit
    def test_listar_despesas_filtro_ano(self, client, operadora_factory, despesa_factory, valid_cnpj):
        """Deve filtrar despesas por ano."""
        operadora = operadora_factory(cnpj=valid_cnpj)
        despesas_2024 = [despesa_factory(cnpj=valid_cnpj, ano=2024)]
        
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_op_repo:
            with patch("src.interface.api.routers.operadoras.DespesaRepository") as mock_desp_repo:
                mock_op_repo.return_value.get_by_cnpj = AsyncMock(return_value=operadora)
                mock_desp_repo.return_value.get_by_operadora = AsyncMock(return_value=despesas_2024)
                
                response = client.get(f"/api/operadoras/{valid_cnpj}/despesas?ano=2024")
                
                assert response.status_code == 200
    
    @pytest.mark.unit
    def test_listar_despesas_filtro_trimestre(self, client, operadora_factory, despesa_factory, valid_cnpj):
        """Deve filtrar despesas por trimestre."""
        operadora = operadora_factory(cnpj=valid_cnpj)
        despesas_q1 = [despesa_factory(cnpj=valid_cnpj, trimestre=1)]
        
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_op_repo:
            with patch("src.interface.api.routers.operadoras.DespesaRepository") as mock_desp_repo:
                mock_op_repo.return_value.get_by_cnpj = AsyncMock(return_value=operadora)
                mock_desp_repo.return_value.get_by_operadora = AsyncMock(return_value=despesas_q1)
                
                response = client.get(f"/api/operadoras/{valid_cnpj}/despesas?trimestre=1")
                
                assert response.status_code == 200
    
    @pytest.mark.unit
    def test_listar_despesas_operadora_inexistente(self, client, valid_cnpj):
        """Deve retornar 404 para operadora inexistente."""
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_repo:
            mock_repo.return_value.get_by_cnpj = AsyncMock(return_value=None)
            
            response = client.get(f"/api/operadoras/{valid_cnpj}/despesas")
            
            assert response.status_code == 404
    
    @pytest.mark.unit
    def test_listar_despesas_trimestre_invalido(self, client):
        """Deve retornar erro para trimestre inválido."""
        response = client.get("/api/operadoras/11444777000161/despesas?trimestre=5")
        
        assert response.status_code == 422
    
    @pytest.mark.unit
    def test_listar_despesas_ano_invalido(self, client):
        """Deve retornar erro para ano muito antigo."""
        response = client.get("/api/operadoras/11444777000161/despesas?ano=1900")
        
        assert response.status_code == 422


# =============================================================
# Testes de Headers e Formato
# =============================================================
class TestResponseFormat:
    """Testes para validar formato das respostas."""
    
    @pytest.mark.unit
    def test_response_content_type_json(self, client):
        """Respostas devem ter content-type JSON."""
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_repo:
            mock_repo.return_value.list_all = AsyncMock(return_value=([], 0))
            
            response = client.get("/api/operadoras")
            
            assert "application/json" in response.headers.get("content-type", "")
    
    @pytest.mark.unit
    def test_paginacao_campos_obrigatorios(self, client):
        """Resposta paginada deve ter todos os campos."""
        with patch("src.interface.api.routers.operadoras.OperadoraRepository") as mock_repo:
            mock_repo.return_value.list_all = AsyncMock(return_value=([], 0))
            
            response = client.get("/api/operadoras")
            data = response.json()
            
            assert "data" in data
            assert "total" in data
            assert "page" in data
            assert "limit" in data
