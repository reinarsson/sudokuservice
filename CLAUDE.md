# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run all tests**
```bash
pytest
```

**Run a single test file or test by name**
```bash
pytest tests/integration/test_auth_endpoints.py
pytest -k "test_login_success"
```

**Run tests with coverage (80% minimum enforced in CI)**
```bash
pytest --cov=src --cov-fail-under=80
```

**Start the FastAPI server**
```bash
PYTHONPATH=src uvicorn api.main:app --reload
```

**Start the Dash frontend**
```bash
PYTHONPATH=src python src/web/app.py
```

**Build and run in Docker**
```bash
docker build -t sudokuservice .
docker run --rm sudokuservice
docker run --rm sudokuservice python -m pytest tests/
```

## Architecture

This is the service layer (FastAPI + Dash). Sudoku solving is provided by the **sudokulib** package (sibling directory `../sudokulib`), which is installed as an editable dependency.

### Service (FastAPI + Dash)
A full-stack authentication and sudoku service following **hexagonal (ports & adapters)** architecture:

```
src/
  domain/
    interfaces/    # Protocol definitions (ports) — AuthService, UserRepository, TokenRepository
    models/        # Pydantic domain models — User, TokenPair
    services/      # AuthServiceImpl — pure business logic, no framework imports
  infrastructure/
    repositories/  # In-memory adapters (InMemoryUserRepository, InMemoryTokenRepository)
    security/      # JwtHandler, PasswordHasher
  api/
    v1/            # FastAPI routers and Pydantic request/response schemas
  core/
    config.py      # pydantic_settings — all config via AUTH_* env vars
    dependencies.py # DI wiring — module-level singleton repos, get_auth_service()
    exceptions.py  # Global exception handlers registered on the app
  web/
    app.py         # Dash app — routing via dcc.Location + dcc.Store; /sudoku is auth-gated
    layouts/       # auth.py (login, register), sudoku.py (upload + grid renderer)
    callbacks/     # auth.py (register/login/logout via httpx), sudoku.py (upload + solve)
```

**Dependency flow:** `api/v1` → `domain/interfaces` (Protocol) ← `domain/services` ← `infrastructure`

`core/dependencies.py` is the composition root. Module-level `_user_repo` and `_token_repo` are singleton in-memory stores; `get_auth_service()` wires them with `JwtHandler` and `PasswordHasher` and is injected via FastAPI `Depends()`.

**Dash routing** (`web/app.py`): `display_page` returns a `(layout, pathname)` tuple. Unauthenticated requests to `/sudoku` are redirected to `/login`. The JWT access token is stored in `dcc.Store(id="auth-store", storage_type="session")` and passed as a Bearer header when the sudoku callback calls the solve endpoint.

**`web/callbacks/sudoku.py`** POSTs to `POST /api/v1/sudoku/solve` — this FastAPI endpoint does not yet exist and needs to be implemented. It should accept `{"board": [[int]]}` and return `{"board": [[int]], "solution": [[int]]}`.

**pytest.ini** adds both `src/` and `tests/` to `sys.path` (`pythonpath = src tests`) and sets `asyncio_mode = auto`. Integration tests use `httpx.AsyncClient` with `ASGITransport` and an `autouse` fixture that clears the in-memory repos between tests.

## Code Standards

- **Python 3.12+**, `from __future__ import annotations` in every file
- Type hints on all signatures; `pydantic.BaseModel` for all schemas; `pydantic_settings` for config
- `Protocol` (preferred) or `ABC` for all service interfaces in `domain/interfaces/`
- Async endpoints by default; `lifespan` context manager for startup/shutdown
- Separate request and response schemas — never expose domain models from API endpoints
- One router per domain resource, registered in `api/main.py` under `/api/v1/...`
- Google-style docstrings on all public functions, classes, and modules
- Branch naming: `feat/`, `fix/`, `chore/`, `refactor/`; Conventional Commits format

## CI

Two GitHub Actions workflows:
- **`tests.yml`** — runs `pytest --cov=src --cov-fail-under=80` on every PR; posts a coverage comment
- **`claude-review.yml`** — Claude PR review (currently disabled with `if: false`)

The review model is `claude-haiku-4-5-20251001` by default; override via the `CLAUDE_MODEL` repository variable. Required secret: `MY_GITHUB_CLAUDE_API_KEY`.
