from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from api.main import create_app
from core.dependencies import _token_repo, _user_repo


@pytest.fixture(autouse=True)
def _reset_repositories() -> None:
    """Clear in-memory state between tests."""
    _user_repo._users.clear()
    _token_repo._revoked.clear()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Provide an async HTTP client bound to the FastAPI app."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
REFRESH_URL = "/api/v1/auth/refresh"

VALID_USER = {"username": "testuser", "email": "test@example.com", "password": "SecurePass123"}


# ── Register endpoint ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register_success_returns_201(client: AsyncClient) -> None:
    response = await client.post(REGISTER_URL, json=VALID_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_username_returns_400(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    response = await client.post(REGISTER_URL, json=VALID_USER)
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_400(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    second_user = {"username": "other", "email": "test@example.com", "password": "Pass123"}
    response = await client.post(REGISTER_URL, json=second_user)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(client: AsyncClient) -> None:
    bad_user = {"username": "testuser", "email": "not-an-email", "password": "Pass123"}
    response = await client.post(REGISTER_URL, json=bad_user)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_fields_returns_422(client: AsyncClient) -> None:
    response = await client.post(REGISTER_URL, json={"username": "testuser"})
    assert response.status_code == 422


# ── Login endpoint ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_success_returns_tokens(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    response = await client.post(
        LOGIN_URL, json={"username": "testuser", "password": "SecurePass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_returns_400(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    response = await client.post(
        LOGIN_URL, json={"username": "testuser", "password": "WrongPass"}
    )
    assert response.status_code == 400
    assert "Invalid username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user_returns_400(client: AsyncClient) -> None:
    response = await client.post(
        LOGIN_URL, json={"username": "ghost", "password": "Pass123"}
    )
    assert response.status_code == 400
    assert "Invalid username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_missing_fields_returns_422(client: AsyncClient) -> None:
    response = await client.post(LOGIN_URL, json={"username": "testuser"})
    assert response.status_code == 422


# ── Logout endpoint ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_logout_success_returns_message(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await client.post(
        LOGIN_URL, json={"username": "testuser", "password": "SecurePass123"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    response = await client.post(LOGOUT_URL, json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


@pytest.mark.asyncio
async def test_logout_invalid_token_returns_400(client: AsyncClient) -> None:
    response = await client.post(LOGOUT_URL, json={"refresh_token": "invalid.token.here"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_logout_revoked_token_cannot_refresh(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await client.post(
        LOGIN_URL, json={"username": "testuser", "password": "SecurePass123"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    await client.post(LOGOUT_URL, json={"refresh_token": refresh_token})
    response = await client.post(REFRESH_URL, json={"refresh_token": refresh_token})
    assert response.status_code == 400
    assert "revoked" in response.json()["detail"].lower()


# ── Refresh endpoint ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_refresh_success_returns_new_tokens(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await client.post(
        LOGIN_URL, json={"username": "testuser", "password": "SecurePass123"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    response = await client.post(REFRESH_URL, json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token  # token rotation


@pytest.mark.asyncio
async def test_refresh_with_access_token_returns_400(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await client.post(
        LOGIN_URL, json={"username": "testuser", "password": "SecurePass123"}
    )
    access_token = login_resp.json()["access_token"]

    response = await client.post(REFRESH_URL, json={"refresh_token": access_token})
    assert response.status_code == 400
    assert "Invalid token type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_invalid_token_returns_400(client: AsyncClient) -> None:
    response = await client.post(REFRESH_URL, json={"refresh_token": "garbage"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_refresh_old_token_revoked_after_rotation(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await client.post(
        LOGIN_URL, json={"username": "testuser", "password": "SecurePass123"}
    )
    old_refresh = login_resp.json()["refresh_token"]

    await client.post(REFRESH_URL, json={"refresh_token": old_refresh})
    response = await client.post(REFRESH_URL, json={"refresh_token": old_refresh})
    assert response.status_code == 400
    assert "revoked" in response.json()["detail"].lower()
