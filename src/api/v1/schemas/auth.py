from __future__ import annotations

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    username: str
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    """Response schema after successful registration."""

    id: str
    username: str
    email: str


class LoginRequest(BaseModel):
    """Request schema for user login."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Response schema containing an access/refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Request schema for logout (token revocation)."""

    refresh_token: str


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
