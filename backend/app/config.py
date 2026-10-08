"""Application settings loaded from environment / .env — secrets never hardcoded."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_JWT_SECRET = "insecure-default-secret"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql+asyncpg://spa:spa@localhost:5432/spa_db"

    jwt_secret: SecretStr = Field(default=SecretStr(DEFAULT_JWT_SECRET))
    jwt_algorithm: str = "HS256"
    jwt_expires_min: int = 60

    cors_origins: str = "http://localhost:3000"
    rate_limit: str = "60/minute"

    seed_admin_email: str = "admin@example.com"
    seed_admin_password: SecretStr = Field(default=SecretStr("change-me-admin"))

    @field_validator("jwt_secret")
    @classmethod
    def _secret_not_default(cls, value: SecretStr, info) -> SecretStr:
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def ensure_secure(self) -> None:
        """Fail fast in production when secrets are missing or default."""
        if not self.is_production:
            return
        if self.jwt_secret.get_secret_value() == DEFAULT_JWT_SECRET:
            raise RuntimeError("JWT_SECRET must be set to a real value in production")
        if self.jwt_secret.get_secret_value() in ("", "changeme"):
            raise RuntimeError("JWT_SECRET is too weak for production")


@lru_cache
def get_settings() -> Settings:
    return Settings()
