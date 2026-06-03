from __future__ import annotations

from domain.interfaces.token_repository import TokenRepository
from domain.interfaces.user_repository import UserRepository
from domain.models.token import TokenPair
from domain.models.user import User
from infrastructure.security.jwt_handler import JwtHandler
from infrastructure.security.password_hasher import PasswordHasher


class AuthServiceImpl:
    """Concrete implementation of the AuthService use cases."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: TokenRepository,
        password_hasher: PasswordHasher,
        jwt_handler: JwtHandler,
    ) -> None:
        self._user_repo = user_repository
        self._token_repo = token_repository
        self._hasher = password_hasher
        self._jwt = jwt_handler

    async def register(self, username: str, email: str, password: str) -> User:
        """Register a new user after validating uniqueness."""
        existing = await self._user_repo.get_by_username(username)
        if existing is not None:
            raise ValueError("Username already taken")

        existing_email = await self._user_repo.get_by_email(email)
        if existing_email is not None:
            raise ValueError("Email already registered")

        hashed = self._hasher.hash(password)
        user = User(username=username, email=email, hashed_password=hashed)
        return await self._user_repo.save(user)

    async def login(self, username: str, password: str) -> TokenPair:
        """Authenticate user credentials and return a token pair."""
        user = await self._user_repo.get_by_username(username)
        if user is None:
            raise ValueError("Invalid username or password")

        if not self._hasher.verify(password, user.hashed_password):
            raise ValueError("Invalid username or password")

        access_token = self._jwt.create_access_token(subject=user.id)
        refresh_token = self._jwt.create_refresh_token(subject=user.id)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def logout(self, refresh_token: str) -> None:
        """Revoke the given refresh token."""
        payload = self._jwt.decode_token(refresh_token)
        jti = payload.get("jti")
        if jti is None:
            raise ValueError("Invalid refresh token")
        await self._token_repo.revoke(jti)

    async def refresh(self, refresh_token: str) -> TokenPair:
        """Issue new tokens from a valid, non-revoked refresh token."""
        payload = self._jwt.decode_token(refresh_token)
        jti = payload.get("jti")
        if jti is None:
            raise ValueError("Invalid refresh token")

        if await self._token_repo.is_revoked(jti):
            raise ValueError("Refresh token has been revoked")

        token_type = payload.get("type")
        if token_type != "refresh":
            raise ValueError("Invalid token type")

        # Revoke old refresh token (rotation)
        await self._token_repo.revoke(jti)

        subject = payload["sub"]
        access_token = self._jwt.create_access_token(subject=subject)
        new_refresh_token = self._jwt.create_refresh_token(subject=subject)
        return TokenPair(access_token=access_token, refresh_token=new_refresh_token)
