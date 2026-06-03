from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.v1.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from core.dependencies import get_auth_service
from domain.interfaces.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(body: RegisterRequest, auth_service: AuthServiceDep) -> RegisterResponse:
    """Register a new user account."""
    user = await auth_service.register(
        username=body.username,
        email=body.email,
        password=body.password,
    )
    return RegisterResponse(id=user.id, username=user.username, email=user.email)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, auth_service: AuthServiceDep) -> TokenResponse:
    """Authenticate and return access/refresh tokens."""
    token_pair = await auth_service.login(
        username=body.username,
        password=body.password,
    )
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(body: LogoutRequest, auth_service: AuthServiceDep) -> MessageResponse:
    """Revoke a refresh token."""
    await auth_service.logout(refresh_token=body.refresh_token)
    return MessageResponse(message="Successfully logged out")


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, auth_service: AuthServiceDep) -> TokenResponse:
    """Issue new tokens from a valid refresh token."""
    token_pair = await auth_service.refresh(refresh_token=body.refresh_token)
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
    )
