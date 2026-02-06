from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"
    )

    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 60 * 24
    jwt_refresh_expire_minutes: int = 60 * 24 * 30

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    # Better Auth JWKS Configuration
    better_auth_jwks_url: str = "http://localhost:3000/api/auth/jwks"
    better_auth_issuer: str = "http://localhost:3000"
    jwt_jwks_cache_ttl: int = 3600  # 1 hour

    rate_limit_per_day: int = 50
    rate_limit_enabled: bool = True

    openrouter_api_key: str = ""

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0

    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    cors_allow_credentials: bool = True

    query_max_length: int = 500
    query_min_length: int = 1

    app_env: str = "development"
    debug: bool = True

    # Sentry Configuration
    sentry_enabled: bool = False
    sentry_dsn_backend: str = ""
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 1.0

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "console"  # "console" or "json"
    log_file: Optional[str] = None

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
