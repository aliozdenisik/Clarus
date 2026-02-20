from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"

    jwt_secret_key: str = ""  # Legacy: Better Auth JWKS is primary auth. Set via JWT_SECRET_KEY env var if needed.
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
    public_rate_limit_per_minute: int = 120

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
    debug: bool = False

    # Sentry Configuration
    sentry_enabled: bool = False
    sentry_dsn_backend: str = ""
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 1.0

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "console"  # "console" or "json"
    log_file: str | None = None

    # Admin Authorization
    admin_emails: str = ""  # Comma-separated admin email addresses

    # i18n Configuration
    supported_locales: list[str] = ["tr", "en"]
    default_locale: str = "tr"

    @property
    def admin_emails_list(self) -> list[str]:
        """Parse comma-separated admin emails into list."""
        if not self.admin_emails:
            return []
        return [e.strip() for e in self.admin_emails.split(",") if e.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def validate_production_settings(self) -> None:
        """Raise RuntimeError if dangerous settings are used in production."""
        if self.cors_allow_credentials and "*" in self.cors_origins_list:
            raise RuntimeError(
                "CORS misconfiguration: allow_credentials=true cannot be used with wildcard origins. "
                "Set explicit CORS_ORIGINS values."
            )

        if self.debug and self.app_env == "production":
            raise RuntimeError("Debug mode must be disabled in production (set DEBUG=false)")

        if self.app_env == "production" and not self.rate_limit_enabled:
            raise RuntimeError("Rate limiting must be enabled in production (set RATE_LIMIT_ENABLED=true)")

        if self.app_env == "production" and not self.redis_password:
            raise RuntimeError(
                "REDIS_PASSWORD must be set in production. "
                "An unauthenticated Redis instance exposes the JWT blacklist, rate-limit counters, "
                "and cached query data to any network-reachable process. "
                "Generate a strong password with: openssl rand -hex 32"
            )

        if self.app_env == "production":
            production_urls = {
                "database_url": self.database_url,
                "better_auth_jwks_url": self.better_auth_jwks_url,
                "better_auth_issuer": self.better_auth_issuer,
            }

            for key, value in production_urls.items():
                parsed = urlparse(value)
                host = (parsed.hostname or "").lower()
                if host in {"localhost", "127.0.0.1", "::1"}:
                    raise RuntimeError(f"{key} cannot point to localhost in production")

            if self.better_auth_jwks_url.startswith("http://"):
                raise RuntimeError("BETTER_AUTH_JWKS_URL must use HTTPS in production")

            if self.better_auth_issuer.startswith("http://"):
                raise RuntimeError("BETTER_AUTH_ISSUER must use HTTPS in production")

            for origin in self.cors_origins_list:
                parsed = urlparse(origin)
                host = (parsed.hostname or "").lower()
                if host in {"localhost", "127.0.0.1", "::1"}:
                    raise RuntimeError("CORS_ORIGINS cannot contain localhost in production")

        # JWT secret validation: check for weak/default values
        _weak_jwt_patterns = (
            "",
            "your-secret-key-change-in-production",
            "holly-search-secret-key-change-in-production-abc123",
            "change-in-production",
            "your-secret-key",
            "secret",
            "jwt-secret",
            "jwt_secret",
            "development",
            "test",
            "change-me",
        )
        if self.jwt_secret_key:
            jwt_lower = self.jwt_secret_key.lower()
            is_weak_pattern = any(p in jwt_lower for p in _weak_jwt_patterns if p)
            is_too_short = len(self.jwt_secret_key) < 32
            if is_weak_pattern or is_too_short:
                raise RuntimeError(
                    "JWT_SECRET_KEY is set but is too weak or uses a known default pattern. "
                    "Generate a strong secret with: openssl rand -hex 32"
                )
        elif self.app_env == "production":
            import logging

            logging.getLogger(__name__).warning(
                "JWT_SECRET_KEY is not set. Better Auth JWKS is the primary auth mechanism. "
                "Set JWT_SECRET_KEY only if legacy JWT auth is still needed."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
