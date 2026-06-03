from __future__ import annotations

import sudokulib


class SudokuServiceImpl:
    """Concrete implementation delegating to sudokulib."""

    def solve(self, board: list[list[int]]) -> list[list[int]]:
        """Validate and solve a 9x9 sudoku puzzle."""
        return sudokulib.solve(board)
