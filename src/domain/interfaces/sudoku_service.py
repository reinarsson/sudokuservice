from __future__ import annotations

from typing import Protocol


class SudokuService(Protocol):
    """Port defining the sudoku solving use case."""

    def solve(self, board: list[list[int]]) -> list[list[int]]:
        """Solve a 9x9 sudoku puzzle and return the completed grid."""
        ...
