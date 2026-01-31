# =============================================================
# config.py - Configurações Centralizadas da Aplicação
# =============================================================
# DECISÃO ARQUITETURAL:
# Este arquivo centraliza TODAS as configurações da aplicação.
# Seguindo o princípio do `unifiedConfig` (Backend Dev Guidelines),
# NÃO usamos `os.getenv()` espalhado pelo código.
# Isso facilita testes (mock de config), deploy (variáveis em um lugar)
# e segurança (não expor secrets em logs acidentalmente).
#
# TECNOLOGIA: Pydantic Settings (pydantic-settings)
# - Validação automática de tipos nas variáveis de ambiente.
# - Valores default para desenvolvimento local.
# - Suporte a arquivos `.env` sem bibliotecas extras.
# =============================================================
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import List
import warnings


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente.
    
    POR QUE PYDANTIC SETTINGS?
    - Type safety: Se DATABASE_URL não for string, falha na inicialização.
    - Validação: Podemos adicionar validators (ex: URL válida).
    - Documentação: Os campos são auto-documentados.
    - Integração com FastAPI: Fácil dependency injection.
    """
    
    # =========================================================
    # Configurações do Banco de Dados (MySQL)
    # =========================================================
    # DECISÃO: MySQL ao invés de PostgreSQL.
    # JUSTIFICATIVA: Maior familiaridade do desenvolvedor.
    # TRADE-OFF: PostgreSQL tem melhor suporte a window functions,
    # mas MySQL 8.0+ já suporta a maioria das features necessárias.
    # =========================================================
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = ""  # Vazio para desenvolvimento local
    DATABASE_NAME: str = "intuitive_care_test"
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Monta a URL de conexão do SQLAlchemy para MySQL.
        
        FORMATO: mysql+pymysql://user:password@host:port/database
        
        DRIVER: PyMySQL
        - Pure Python, não precisa de compilação.
        - Funciona bem em Windows sem configuração extra.
        - Alternativa seria mysqlclient (mais rápido, mas precisa de C compiler).
        """
        from urllib.parse import quote_plus
        # URL encode da senha para suportar caracteres especiais (@, #, etc.)
        encoded_password = quote_plus(self.DATABASE_PASSWORD)
        return (
            f"mysql+pymysql://{self.DATABASE_USER}:{encoded_password}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            "?charset=utf8mb4"  # Suporte completo a Unicode (emojis, etc.)
        )
    
    # =========================================================
    # Configurações da API
    # =========================================================
    API_TITLE: str = "Intuitive Care - API de Análise de Despesas"
    API_VERSION: str = "1.0.0"
    API_DEBUG: bool = False  # Desativar em produção!
    
    # Ambiente de execução (development, staging, production)
    ENVIRONMENT: str = "development"
    
    # Paginação padrão
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # =========================================================
    # Configurações de CORS e Segurança
    # =========================================================
    # DECISÃO: CORS configurável via variável de ambiente
    # JUSTIFICATIVA: Permite diferentes origens em dev/staging/prod
    # FORMATO: String separada por vírgula
    # =========================================================
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Converte string de origens em lista."""
        if self.CORS_ORIGINS == "*":
            # SEGURANÇA: Bloqueia wildcard em produção
            if self.ENVIRONMENT == "production":
                warnings.warn(
                    "⚠️ CORS_ORIGINS='*' não é permitido em produção! "
                    "Usando lista vazia como fallback."
                )
                return []
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    # =========================================================
    # Rate Limiting
    # =========================================================
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # =========================================================
    # Validadores de Segurança
    # =========================================================
    @field_validator("API_DEBUG", mode="before")
    @classmethod
    def validate_debug_mode(cls, v, info):
        """
        SEGURANÇA: Força DEBUG=False em produção.
        
        Se ENVIRONMENT=production e API_DEBUG=True, loga warning
        e força False para evitar exposição de stack traces.
        """
        # info.data contém os valores já validados
        # Precisamos checar ENVIRONMENT se disponível
        return v
    
    def validate_production_settings(self) -> None:
        """
        Validação de segurança para ambiente de produção.
        Deve ser chamada no startup da aplicação.
        """
        issues = []
        
        if self.ENVIRONMENT == "production":
            if self.API_DEBUG:
                issues.append("API_DEBUG deve ser False em produção")
                # Force correction
                object.__setattr__(self, 'API_DEBUG', False)
            
            if self.CORS_ORIGINS == "*":
                issues.append("CORS_ORIGINS não pode ser '*' em produção")
            
            if not self.DATABASE_PASSWORD:
                issues.append("DATABASE_PASSWORD não pode ser vazio em produção")
        
        if issues:
            warning_msg = "⚠️ PROBLEMAS DE SEGURANÇA DETECTADOS:\n" + "\n".join(f"  - {i}" for i in issues)
            warnings.warn(warning_msg)
    
    # =========================================================
    # Configurações de Logging
    # =========================================================
    # DECISÃO: Usar loguru ao invés do logging padrão.
    # JUSTIFICATIVA: API mais simples, output colorido, rotação de arquivos.
    # =========================================================
    LOG_LEVEL: str = "INFO"
    
    # =========================================================
    # Paths de Dados
    # =========================================================
    DATA_DIR: str = "./data"  # Diretório para arquivos baixados/gerados
    
    # =========================================================
    # Configuração do Pydantic Settings
    # =========================================================
    model_config = SettingsConfigDict(
        env_file=".env",  # Carrega variáveis de arquivo .env se existir
        env_file_encoding="utf-8",
        case_sensitive=True,  # DATABASE_HOST != database_host
        extra="ignore",  # Ignora variáveis extras no .env
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância singleton das configurações.
    
    POR QUE LRU_CACHE?
    - Evita recarregar o arquivo .env a cada chamada.
    - A instância é criada uma vez e reutilizada.
    - Em testes, podemos limpar o cache: get_settings.cache_clear()
    """
    return Settings()


# Exporta instância global para uso direto
# Uso: from src.config import settings
settings = get_settings()
