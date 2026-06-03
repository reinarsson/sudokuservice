from __future__ import annotations

from typing import Protocol

from domain.models.token import TokenPair
from domain.models.user import User


class AuthService(Protocol):
    """Port defining the authentication use cases."""

    async def register(self, username: str, email: str, password: str) -> User:
        """Register a new user."""
        ...

    async def login(self, username: str, password: str) -> TokenPair:
        """Authenticate a user and return tokens."""
        ...

    async def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token."""
        ...

    async def refresh(self, refresh_token: str) -> TokenPair:
        """Issue a new token pair from a valid refresh token."""
        ...
