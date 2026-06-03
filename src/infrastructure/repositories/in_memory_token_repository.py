from __future__ import annotations


class InMemoryTokenRepository:
    """In-memory adapter for the TokenRepository port."""

    def __init__(self) -> None:
        self._revoked: set[str] = set()

    async def revoke(self, token_jti: str) -> None:
        """Mark a refresh token as revoked."""
        self._revoked.add(token_jti)

    async def is_revoked(self, token_jti: str) -> bool:
        """Check whether a refresh token has been revoked."""
        return token_jti in self._revoked
