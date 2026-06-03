from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt


class JwtHandler:
    """Adapter for creating and decoding JSON Web Tokens."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_minutes: int = 10080,
    ) -> None:
        self._secret = secret_key
        self._algorithm = algorithm
        self._access_expire = timedelta(minutes=access_token_expire_minutes)
        self._refresh_expire = timedelta(minutes=refresh_token_expire_minutes)

    def create_access_token(self, subject: str) -> str:
        """Create a short-lived access token."""
        now = datetime.now(UTC)
        payload = {
            "sub": subject,
            "type": "access",
            "jti": str(uuid.uuid4()),
            "exp": now + self._access_expire,
            "iat": now,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def create_refresh_token(self, subject: str) -> str:
        """Create a long-lived refresh token."""
        now = datetime.now(UTC)
        payload = {
            "sub": subject,
            "type": "refresh",
            "jti": str(uuid.uuid4()),
            "exp": now + self._refresh_expire,
            "iat": now,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT, raising ValueError on failure."""
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError as exc:
            raise ValueError(f"Invalid token: {exc}") from exc
