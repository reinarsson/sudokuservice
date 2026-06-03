from __future__ import annotations

from functools import lru_cache

from core.config import Settings
from domain.services.auth_service import AuthServiceImpl
from domain.services.sudoku_service import SudokuServiceImpl
from infrastructure.repositories.in_memory_token_repository import InMemoryTokenRepository
from infrastructure.repositories.in_memory_user_repository import InMemoryUserRepository
from infrastructure.security.jwt_handler import JwtHandler
from infrastructure.security.password_hasher import PasswordHasher

_user_repo = InMemoryUserRepository()
_token_repo = InMemoryTokenRepository()


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


def get_auth_service() -> AuthServiceImpl:
    """Build and return the AuthService with all dependencies wired."""
    settings = get_settings()
    jwt_handler = JwtHandler(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_minutes=settings.refresh_token_expire_minutes,
    )
    password_hasher = PasswordHasher()
    return AuthServiceImpl(
        user_repository=_user_repo,
        token_repository=_token_repo,
        password_hasher=password_hasher,
        jwt_handler=jwt_handler,
    )


def get_sudoku_service() -> SudokuServiceImpl:
    """Return a SudokuService instance."""
    return SudokuServiceImpl()
