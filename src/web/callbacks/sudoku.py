from __future__ import annotations

import base64
import csv
import io
import json

import dash_bootstrap_components as dbc
import httpx
from dash import Input, Output, State, callback, html, no_update

from core.config import Settings
from web.layouts.sudoku import render_grid

_settings = Settings()
_SOLVE_URL = f"http://{_settings.api_host}:{_settings.api_port}/api/v1/sudoku/solve"

GRID_SIZE = 9


def _parse_upload(contents: str, filename: str) -> list[list[int]]:
    """Decode an uploaded file and return a 9x9 integer grid."""
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    if filename.endswith(".json"):
        board = json.loads(decoded)
    elif filename.endswith(".csv"):
        reader = csv.reader(io.StringIO(decoded.decode("utf-8")))
        board = [[int(cell) for cell in row] for row in reader if row]
    else:
        raise ValueError("Unsupported file type. Please upload JSON or CSV.")

    if len(board) != GRID_SIZE or any(len(row) != GRID_SIZE for row in board):
        raise ValueError(f"Board must be a {GRID_SIZE}x{GRID_SIZE} grid.")

    return board


@callback(
    [
        Output("puzzle-store", "data"),
        Output("upload-error", "children"),
        Output("grids-container", "children", allow_duplicate=True),
    ],
    Input("sudoku-upload", "contents"),
    State("sudoku-upload", "filename"),
    prevent_initial_call=True,
)
def handle_upload(
    contents: str | None,
    filename: str | None,
) -> tuple[object, object, object]:
    """Parse the uploaded file and display the puzzle grid."""
    if contents is None or filename is None:
        return no_update, no_update, no_update

    try:
        board = _parse_upload(contents, filename)
    except (ValueError, json.JSONDecodeError, KeyError) as exc:
        error = html.Span(str(exc), style={"color": "red"})
        return no_update, error, no_update

    puzzle_card = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Uploaded Puzzle", className="text-center mb-3"),
                render_grid(board),
                dbc.Button(
                    "Solve",
                    id="solve-button",
                    color="primary",
                    className="w-100 mt-3",
                ),
                html.Div(id="solve-error", className="mt-2"),
            ]
        ),
        style={"maxWidth": "420px"},
    )

    return board, "", [puzzle_card, html.Div(id="solution-card")]


@callback(
    Output("solution-card", "children"),
    Input("solve-button", "n_clicks"),
    [State("puzzle-store", "data"), State("auth-store", "data")],
    prevent_initial_call=True,
)
def handle_solve(
    n_clicks: int | None,
    board: list[list[int]] | None,
    auth_data: dict[str, str] | None,
) -> object:
    """Send the puzzle to the solver API and display the solution."""
    if board is None:
        return no_update

    headers = {}
    if auth_data and "access_token" in auth_data:
        headers["Authorization"] = f"Bearer {auth_data['access_token']}"

    with httpx.Client() as client:
        response = client.post(_SOLVE_URL, json={"board": board}, headers=headers)

    if response.status_code != 200:
        detail = response.json().get("detail", "Solve failed.")
        return html.Span(detail, style={"color": "red"})

    data = response.json()
    solution = data["solution"]
    original = data["board"]

    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Solution", className="text-center mb-3"),
                render_grid(solution, original=original),
            ]
        ),
        style={"maxWidth": "420px"},
    )
