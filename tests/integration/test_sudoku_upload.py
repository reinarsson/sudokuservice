from __future__ import annotations

import base64
import csv
import io
import json

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from api.main import create_app
from fixtures import EXPECTED_SOLUTION, test_board
from web.callbacks.sudoku import _parse_upload

SOLVE_URL = "/api/v1/sudoku/solve"


def _json_upload(board: list[list[int]]) -> tuple[str, str]:
    contents = "data:application/json;base64," + base64.b64encode(
        json.dumps(board).encode()
    ).decode()
    return contents, "puzzle.json"


def _csv_upload(board: list[list[int]]) -> tuple[str, str]:
    buf = io.StringIO()
    csv.writer(buf).writerows(board)
    contents = "data:text/csv;base64," + base64.b64encode(
        buf.getvalue().encode()
    ).decode()
    return contents, "puzzle.csv"


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_upload_json_and_solve(client: AsyncClient) -> None:
    contents, filename = _json_upload(test_board)
    board = _parse_upload(contents, filename)
    assert board == test_board

    response = await client.post(SOLVE_URL, json={"board": board})
    assert response.status_code == 200
    assert response.json()["solution"] == EXPECTED_SOLUTION


@pytest.mark.asyncio
async def test_upload_csv_and_solve(client: AsyncClient) -> None:
    contents, filename = _csv_upload(test_board)
    board = _parse_upload(contents, filename)
    assert board == test_board

    response = await client.post(SOLVE_URL, json={"board": board})
    assert response.status_code == 200
    assert response.json()["solution"] == EXPECTED_SOLUTION
