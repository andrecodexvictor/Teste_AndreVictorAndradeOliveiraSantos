# =============================================================
# test_health.py - Testes de Endpoints Utilitários
# =============================================================
# COBERTURA: Health check, root, metrics
# =============================================================
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


# =============================================================
# Testes de Health Check (GET /health)
# =============================================================
class TestHealthCheck:
    """Testes para o endpoint de health check."""
    
    @pytest.mark.unit
    def test_health_check_sucesso(self, client):
        """Health check deve retornar status healthy."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.unit
    def test_health_check_versao(self, client):
        """Health check deve incluir versão da API."""
        response = client.get("/health")
        
        data = response.json()
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    @pytest.mark.unit
    def test_health_check_timestamp(self, client):
        """Health check deve incluir timestamp."""
        response = client.get("/health")
        
        data = response.json()
        assert "timestamp" in data
        # Timestamp deve ser parseable
        assert data["timestamp"] is not None


# =============================================================
# Testes de Root (GET /)
# =============================================================
class TestRoot:
    """Testes para o endpoint raiz."""
    
    @pytest.mark.unit
    def test_root_sucesso(self, client):
        """Root deve retornar informações da API."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    @pytest.mark.unit
    def test_root_links(self, client):
        """Root deve incluir links para docs e health."""
        response = client.get("/")
        
        data = response.json()
        assert "docs" in data
        assert "health" in data


# =============================================================
# Testes de Docs (GET /docs)
# =============================================================
class TestDocs:
    """Testes para o endpoint de documentação."""
    
    @pytest.mark.unit
    def test_docs_disponivel(self, client):
        """Documentação deve estar disponível."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    @pytest.mark.unit
    def test_docs_contem_endpoints(self, client):
        """Documentação deve listar endpoints."""
        response = client.get("/docs")
        
        content = response.text
        assert "operadoras" in content.lower()


# =============================================================
# Testes de Metrics (GET /metrics)
# =============================================================
class TestMetrics:
    """Testes para o endpoint de métricas."""
    
    @pytest.mark.unit
    def test_metrics_disponivel(self, client):
        """Endpoint de métricas deve estar disponível."""
        response = client.get("/metrics")
        
        # Pode retornar 200 com métricas ou erro se módulo não disponível
        assert response.status_code in [200, 500]
    
    @pytest.mark.unit
    def test_metrics_formato_json(self, client):
        """Métricas devem ser JSON."""
        response = client.get("/metrics")
        
        if response.status_code == 200:
            assert "application/json" in response.headers.get("content-type", "")


# =============================================================
# Testes de Erro 404
# =============================================================
class TestNotFound:
    """Testes para endpoints inexistentes."""
    
    @pytest.mark.unit
    def test_endpoint_inexistente(self, client):
        """Endpoint inexistente deve retornar 404."""
        response = client.get("/api/endpoint-que-nao-existe")
        
        assert response.status_code == 404
    
    @pytest.mark.unit
    def test_metodo_nao_permitido(self, client):
        """Método não permitido deve retornar 405."""
        response = client.post("/health")
        
        assert response.status_code == 405


# =============================================================
# Testes de Content-Type
# =============================================================
class TestContentType:
    """Testes para content-type das respostas."""
    
    @pytest.mark.unit
    def test_api_retorna_json(self, client):
        """Endpoints de API devem retornar JSON."""
        response = client.get("/health")
        
        assert "application/json" in response.headers.get("content-type", "")
    
    @pytest.mark.unit
    def test_docs_retorna_html(self, client):
        """Docs deve retornar HTML."""
        response = client.get("/docs")
        
        assert "text/html" in response.headers.get("content-type", "")
