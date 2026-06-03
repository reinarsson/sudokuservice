# sudokusolver

A service that solves Sudoku puzzles and provides a JWT-based authentication API with a Dash web frontend.

## Services

| Service | Default port | Description |
|---------|-------------|-------------|
| FastAPI | `8000` | REST API |
| Dash | `8050` | Web frontend |

## Running locally

**Install dependencies**
```bash
pip install -r requirements.txt
```

**Start the API**
```bash
PYTHONPATH=src uvicorn api.main:app --reload
```

**Start the web frontend**
```bash
PYTHONPATH=src python src/web/app.py
```

Interactive API docs are available at **http://localhost:8000/docs**.

## API endpoints

All endpoints are under `/api/v1/auth`.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/auth/register` | Create a new user account |
| `POST` | `/api/v1/auth/login` | Authenticate and receive tokens |
| `POST` | `/api/v1/auth/refresh` | Rotate tokens using a refresh token |
| `POST` | `/api/v1/auth/logout` | Revoke a refresh token |

### Token flow

- **Login** returns an `access_token` (30 min) and a `refresh_token` (7 days)
- **Refresh** issues a new token pair and revokes the old refresh token
- **Logout** revokes the refresh token; using it afterwards returns `400`

### Configuration

All settings are loaded from environment variables with the `AUTH_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_JWT_SECRET_KEY` | `change-me-in-production` | JWT signing secret — **always override in production** |
| `AUTH_JWT_ALGORITHM` | `HS256` | Signing algorithm |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `AUTH_REFRESH_TOKEN_EXPIRE_MINUTES` | `10080` | Refresh token lifetime (7 days) |
| `AUTH_API_HOST` | `127.0.0.1` | API bind address |
| `AUTH_API_PORT` | `8000` | API port |
| `AUTH_DASH_PORT` | `8050` | Dash port |

> **Note:** Users and tokens are stored in memory and are lost on restart. To persist data, implement the `UserRepository` and `TokenRepository` interfaces in `src/domain/interfaces/` with a database-backed adapter.

## Web frontend

The Dash app (`http://localhost:8050`) provides login and register pages. It communicates with the FastAPI service via HTTP.

Routes:
- `/` — login page
- `/register` — registration page

## Sudoku solver

The `SudokuSolver` class in `src/sudoku_solver.py` solves a 9×9 board using linear programming (PuLP/CBC). Pass a 9×9 list of integers where `0` represents an empty cell:

```python
from sudoku_solver import SudokuSolver

board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    # ...
]
solution = SudokuSolver(board).solve()
```

## Tests

```bash
pytest                                  # all tests
pytest tests/unit/                      # unit tests only
pytest tests/integration/               # integration tests only
pytest --cov=src --cov-fail-under=80    # with coverage gate
```

## Docker

**Build**
```bash
docker build -t sudokusolver .
```

**Run**
```bash
docker run --rm sudokusolver
```

**Test**
```bash
docker run --rm sudokusolver python -m pytest tests/
```

## GitHub Actions

Two workflows run on every pull request:

- **Tests and Coverage** (`tests.yml`) — runs the test suite with an 80% coverage gate and posts a report as a PR comment
- **Claude PR Review** (`claude-review.yml`) — currently disabled; re-enable by removing `if: false` from the job

The review workflow requires one repository secret:

| Secret | Description |
|--------|-------------|
| `MY_GITHUB_CLAUDE_API_KEY` | Anthropic API key for Claude PR review |

Add it under **Settings → Secrets and variables → Actions → New repository secret**.

The review model defaults to `claude-haiku-4-5-20251001`. Override via the `CLAUDE_MODEL` repository variable under **Settings → Secrets and variables → Actions → Variables**.
