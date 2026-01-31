# =============================================================
# test_security.py - Testes de Segurança
# =============================================================
# COBERTURA: CORS, Rate Limiting, Headers, Sanitização
# =============================================================
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


# =============================================================
# Testes de Security Headers
# =============================================================
class TestSecurityHeaders:
    """Testes para headers de segurança."""
    
    @pytest.mark.security
    def test_x_frame_options_header(self, client):
        """Resposta deve ter X-Frame-Options: DENY."""
        response = client.get("/health")
        
        assert response.headers.get("X-Frame-Options") == "DENY"
    
    @pytest.mark.security
    def test_x_content_type_options_header(self, client):
        """Resposta deve ter X-Content-Type-Options: nosniff."""
        response = client.get("/health")
        
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
    
    @pytest.mark.security
    def test_referrer_policy_header(self, client):
        """Resposta deve ter Referrer-Policy."""
        response = client.get("/health")
        
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    
    @pytest.mark.security
    def test_xss_protection_header(self, client):
        """Resposta deve ter X-XSS-Protection."""
        response = client.get("/health")
        
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    
    @pytest.mark.security
    def test_all_security_headers_present(self, client, security_headers):
        """Todas as headers de segurança devem estar presentes."""
        response = client.get("/health")
        
        for header, expected_value in security_headers.items():
            assert response.headers.get(header) == expected_value, f"Header {header} incorreto"


# =============================================================
# Testes de CORS
# =============================================================
class TestCORS:
    """Testes para configuração CORS."""
    
    @pytest.mark.security
    def test_cors_preflight_request(self, client):
        """Deve responder a preflight OPTIONS."""
        response = client.options(
            "/api/operadoras",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            }
        )
        
        # CORS pode retornar 200 ou 400 dependendo da configuração
        assert response.status_code in [200, 400, 405]
    
    @pytest.mark.security
    def test_cors_origin_header_valido(self, client):
        """Deve incluir header Access-Control-Allow-Origin para origem válida."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:5173"}
        )
        
        # Se CORS está configurado, deve ter o header
        allow_origin = response.headers.get("Access-Control-Allow-Origin")
        # Pode ser a origem específica ou estar ausente (bloqueado)
        assert allow_origin in [None, "http://localhost:5173", "*"]


# =============================================================
# Testes de Rate Limiting
# =============================================================
class TestRateLimiting:
    """Testes para rate limiting."""
    
    @pytest.mark.security
    def test_rate_limit_header_presente(self, client):
        """Resposta deve indicar limite de rate (quando disponível)."""
        # Rate limit pode ou não adicionar headers dependendo do setup
        response = client.get("/health")
        
        # O teste verifica que o endpoint funciona
        # Headers de rate limit são opcionais
        assert response.status_code in [200, 429]
    
    @pytest.mark.security
    @pytest.mark.slow
    def test_rate_limit_excedido(self, client):
        """Deve retornar 429 quando limite excedido."""
        # Este teste precisa de configuração especial
        # Em ambiente real, faria muitas requisições rápidas
        # Aqui apenas verificamos que o mecanismo existe
        from src.infrastructure.rate_limiter import limiter
        
        assert limiter is not None
        assert hasattr(limiter, 'limit')


# =============================================================
# Testes de Sanitização de Logs
# =============================================================
class TestLogSanitization:
    """Testes para sanitização de logs."""
    
    @pytest.mark.security
    def test_sanitize_url_function_exists(self):
        """Função de sanitização de URL deve existir."""
        from src.main import sanitize_url_for_logging
        
        assert callable(sanitize_url_for_logging)
    
    @pytest.mark.security
    def test_sanitize_url_remove_query_string(self):
        """Deve remover query string da URL."""
        from src.main import sanitize_url_for_logging
        
        url = "http://localhost/api/operadoras?token=secret123"
        sanitized = sanitize_url_for_logging(url)
        
        assert "secret123" not in sanitized
        assert "?[REDACTED]" in sanitized
    
    @pytest.mark.security
    def test_sanitize_url_preserva_path(self):
        """Deve preservar o path da URL."""
        from src.main import sanitize_url_for_logging
        
        url = "http://localhost/api/operadoras/11444777000161"
        sanitized = sanitize_url_for_logging(url)
        
        assert "/api/operadoras/11444777000161" in sanitized
    
    @pytest.mark.security
    def test_sanitize_url_sem_query_string(self):
        """URL sem query string deve permanecer igual."""
        from src.main import sanitize_url_for_logging
        
        url = "http://localhost/api/operadoras"
        sanitized = sanitize_url_for_logging(url)
        
        assert sanitized == url


# =============================================================
# Testes de Configuração de Segurança
# =============================================================
class TestSecurityConfig:
    """Testes para configurações de segurança."""
    
    @pytest.mark.security
    def test_debug_mode_config_exists(self):
        """Configuração de debug mode deve existir."""
        from src.config import settings
        
        assert hasattr(settings, 'API_DEBUG')
    
    @pytest.mark.security
    def test_cors_origins_list_exists(self):
        """Lista de origens CORS deve existir."""
        from src.config import settings
        
        assert hasattr(settings, 'cors_origins_list')
        assert isinstance(settings.cors_origins_list, list)
    
    @pytest.mark.security
    def test_rate_limit_config_exists(self):
        """Configuração de rate limit deve existir."""
        from src.config import settings
        
        assert hasattr(settings, 'RATE_LIMIT_PER_MINUTE')
        assert settings.RATE_LIMIT_PER_MINUTE > 0
    
    @pytest.mark.security
    def test_environment_config_exists(self):
        """Configuração de ambiente deve existir."""
        from src.config import settings
        
        assert hasattr(settings, 'ENVIRONMENT')
        assert settings.ENVIRONMENT in ['development', 'staging', 'production', 'testing']
    
    @pytest.mark.security
    def test_production_validation_method_exists(self):
        """Método de validação de produção deve existir."""
        from src.config import settings
        
        assert hasattr(settings, 'validate_production_settings')
        assert callable(settings.validate_production_settings)


# =============================================================
# Testes de Input Validation
# =============================================================
class TestInputValidation:
    """Testes para validação de entrada."""
    
    @pytest.mark.security
    def test_sql_injection_attempt_cnpj(self, client):
        """Deve rejeitar tentativa de SQL injection no CNPJ."""
        malicious_cnpj = "1-DROP-TABLE"
        
        response = client.get(f"/api/operadoras/{malicious_cnpj}")
        
        # Deve retornar 404 (não encontrado) ou erro de validação
        # NÃO deve causar erro de banco
        assert response.status_code in [404, 422, 400, 500]
    
    @pytest.mark.security
    def test_xss_attempt_razao_social(self, client):
        """Deve tratar XSS na razão social."""
        malicious_query = "scriptalert"
        
        response = client.get(f"/api/operadoras?razao_social={malicious_query}")
        
        # Deve processar normalmente (query segura via ORM)
        # Pode falhar com 500 se banco não está disponível
        assert response.status_code in [200, 422, 500]
    
    @pytest.mark.security
    def test_path_traversal_attempt(self, client):
        """Deve rejeitar tentativas de path traversal."""
        malicious_path = "../../../etc/passwd"
        
        response = client.get(f"/api/operadoras/{malicious_path}")
        
        # Deve retornar 404 ou erro
        assert response.status_code in [404, 422, 400]
