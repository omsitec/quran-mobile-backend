from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Quran API - URLs CORRIGÉES
    quran_api_client_id: str
    quran_api_client_secret: str
    quran_api_oauth_endpoint: str
    quran_api_content_endpoint: str
    quran_api_oauth_scopes: str = "content"

    # Backend
    environment: str = "development"
    secret_key: str
    cors_origins: str = "http://localhost:3000"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
