from __future__ import annotations

from typing import Protocol

from domain.models.user import User


class UserRepository(Protocol):
    """Port for persisting and retrieving users."""

    async def get_by_username(self, username: str) -> User | None:
        """Return user by username, or None if not found."""
        ...

    async def get_by_email(self, email: str) -> User | None:
        """Return user by email, or None if not found."""
        ...

    async def save(self, user: User) -> User:
        """Persist a user and return it."""
        ...
