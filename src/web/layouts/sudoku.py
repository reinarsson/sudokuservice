from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

GRID_SIZE = 9
BOX_SIZE = 3


def sudoku_layout() -> html.Div:
    """Return the sudoku upload and solver page layout."""
    return html.Div(
        [
            html.H2("Sudoku Solver", className="text-center mb-4 mt-4"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.P("Upload a JSON or CSV file with a 9x9 sudoku grid (0 = empty cell):"),
                        dcc.Upload(
                            id="sudoku-upload",
                            children=dbc.Button(
                                "Upload Puzzle File",
                                color="secondary",
                                className="w-100",
                            ),
                            accept=".json,.csv",
                        ),
                        html.Div(id="upload-error", className="mt-2"),
                    ]
                ),
                className="mx-auto mb-4",
                style={"maxWidth": "600px"},
            ),
            dcc.Store(id="puzzle-store"),
            html.Div(id="grids-container", className="d-flex justify-content-center flex-wrap gap-4"),
        ]
    )


def render_grid(board: list[list[int]], original: list[list[int]] | None = None) -> html.Table:
    """Render a 9x9 sudoku grid as an HTML table with box borders.

    Args:
        board: The grid values to display.
        original: If provided, cells where original[r][c] == 0 are
            shown in blue (solved cells); given clues stay black.
    """
    rows = []
    for r in range(GRID_SIZE):
        cells = []
        for c in range(GRID_SIZE):
            val = board[r][c]
            display = str(val) if val != 0 else ""

            style: dict[str, str | int] = {
                "width": "40px",
                "height": "40px",
                "textAlign": "center",
                "verticalAlign": "middle",
                "fontSize": "18px",
                "fontWeight": "bold",
                "border": "1px solid #999",
            }

            # Bold borders for 3x3 box edges
            if r % BOX_SIZE == 0:
                style["borderTop"] = "3px solid #000"
            if c % BOX_SIZE == 0:
                style["borderLeft"] = "3px solid #000"
            if r == GRID_SIZE - 1:
                style["borderBottom"] = "3px solid #000"
            if c == GRID_SIZE - 1:
                style["borderRight"] = "3px solid #000"

            # Colour solved cells differently
            if original is not None and original[r][c] == 0 and val != 0:
                style["color"] = "#1a73e8"
            else:
                style["color"] = "#000"

            cells.append(html.Td(display, style=style))
        rows.append(html.Tr(cells))

    return html.Table(
        rows,
        style={"borderCollapse": "collapse", "margin": "0 auto"},
    )
