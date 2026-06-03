from __future__ import annotations

from domain.models.user import User


class InMemoryUserRepository:
    """In-memory adapter for the UserRepository port."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    async def get_by_username(self, username: str) -> User | None:
        """Return user by username, or None if not found."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    async def get_by_email(self, email: str) -> User | None:
        """Return user by email, or None if not found."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def save(self, user: User) -> User:
        """Persist a user in memory and return it."""
        self._users[user.id] = user
        return user
