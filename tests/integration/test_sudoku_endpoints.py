from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from api.main import create_app

SOLVE_URL = "/api/v1/sudoku/solve"

VALID_BOARD = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

EXPECTED_SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Provide an async HTTP client bound to the FastAPI app."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Solve endpoint ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_solve_valid_puzzle_returns_solution(client: AsyncClient) -> None:
    response = await client.post(SOLVE_URL, json={"board": VALID_BOARD})
    assert response.status_code == 200
    data = response.json()
    assert data["board"] == VALID_BOARD
    assert data["solution"] == EXPECTED_SOLUTION


@pytest.mark.asyncio
async def test_solve_returns_complete_grid(client: AsyncClient) -> None:
    response = await client.post(SOLVE_URL, json={"board": VALID_BOARD})
    solution = response.json()["solution"]
    assert len(solution) == 9
    for row in solution:
        assert len(row) == 9
        assert all(1 <= v <= 9 for v in row)


@pytest.mark.asyncio
async def test_solve_preserves_given_clues(client: AsyncClient) -> None:
    response = await client.post(SOLVE_URL, json={"board": VALID_BOARD})
    solution = response.json()["solution"]
    for r in range(9):
        for c in range(9):
            if VALID_BOARD[r][c] != 0:
                assert solution[r][c] == VALID_BOARD[r][c]


@pytest.mark.asyncio
async def test_solve_wrong_dimensions_returns_422(client: AsyncClient) -> None:
    bad_board = [[0] * 9 for _ in range(8)]
    response = await client.post(SOLVE_URL, json={"board": bad_board})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_solve_wrong_row_length_returns_422(client: AsyncClient) -> None:
    bad_board = [[0] * 9 for _ in range(9)]
    bad_board[4] = [0] * 8
    response = await client.post(SOLVE_URL, json={"board": bad_board})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_solve_invalid_cell_value_returns_422(client: AsyncClient) -> None:
    bad_board = [[0] * 9 for _ in range(9)]
    bad_board[0][0] = 10
    response = await client.post(SOLVE_URL, json={"board": bad_board})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_solve_missing_board_returns_422(client: AsyncClient) -> None:
    response = await client.post(SOLVE_URL, json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_solve_unsolvable_puzzle_returns_400(client: AsyncClient) -> None:
    unsolvable = [[0] * 9 for _ in range(9)]
    # Two 1s in the same row makes it unsolvable
    unsolvable[0][0] = 1
    unsolvable[0][1] = 1
    response = await client.post(SOLVE_URL, json={"board": unsolvable})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_solve_already_complete_board(client: AsyncClient) -> None:
    response = await client.post(SOLVE_URL, json={"board": EXPECTED_SOLUTION})
    assert response.status_code == 200
    data = response.json()
    assert data["solution"] == EXPECTED_SOLUTION
