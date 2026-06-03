from __future__ import annotations

from pydantic import BaseModel


class TokenPair(BaseModel):
    """Access and refresh token pair returned on login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
