from __future__ import annotations

from typing import Protocol


class TokenRepository(Protocol):
    """Port for tracking revoked refresh tokens."""

    async def revoke(self, token_jti: str) -> None:
        """Mark a refresh token as revoked."""
        ...

    async def is_revoked(self, token_jti: str) -> bool:
        """Check whether a refresh token has been revoked."""
        ...
