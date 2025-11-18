"""
Infrastructure layer - Configuration management
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Service info
    service_name: str = "identity-svc"
    service_port: int = 8000
    
    # JWT settings
    jwt_algorithm: str = "RS256"
    jwt_expiration_minutes: int = 30
    refresh_token_expiration_days: int = 7
    
    # RSA key settings
    rsa_key_size: int = 2048
    keys_directory: str = "keys"
    
    # CORS settings
    cors_origins: list = ["*"]
    
    # OpenID Connect metadata
    issuer: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
