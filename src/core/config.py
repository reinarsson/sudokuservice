from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 10080
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    dash_port: int = 8050

    model_config = {"env_prefix": "AUTH_"}
