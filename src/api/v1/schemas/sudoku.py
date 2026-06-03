from __future__ import annotations

from pydantic import BaseModel, field_validator

GRID_SIZE = 9
MAX_VALUE = 9


class SudokuSolveRequest(BaseModel):
    """Request schema for solving a sudoku puzzle."""

    board: list[list[int]]

    @field_validator("board")
    @classmethod
    def validate_board_dimensions(cls, board: list[list[int]]) -> list[list[int]]:
        """Ensure the board is a 9x9 grid with valid cell values."""
        if len(board) != GRID_SIZE:
            raise ValueError(f"Board must have {GRID_SIZE} rows, got {len(board)}")
        for i, row in enumerate(board):
            if len(row) != GRID_SIZE:
                raise ValueError(f"Row {i} must have {GRID_SIZE} columns, got {len(row)}")
            for j, val in enumerate(row):
                if not (0 <= val <= MAX_VALUE):
                    raise ValueError(f"Cell ({i},{j}) must be 0-{MAX_VALUE}, got {val}")
        return board


class SudokuSolveResponse(BaseModel):
    """Response schema containing the solved sudoku grid."""

    board: list[list[int]]
    solution: list[list[int]]
