from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends

from api.v1.schemas.sudoku import SudokuSolveRequest, SudokuSolveResponse
from core.dependencies import get_sudoku_service
from domain.interfaces.sudoku_service import SudokuService

router = APIRouter(prefix="/api/v1/sudoku", tags=["sudoku"])

SudokuServiceDep = Annotated[SudokuService, Depends(get_sudoku_service)]


@router.post("/solve", response_model=SudokuSolveResponse)
async def solve(body: SudokuSolveRequest, sudoku_service: SudokuServiceDep) -> SudokuSolveResponse:
    """Solve a sudoku puzzle and return the original board with its solution."""
    loop = asyncio.get_running_loop()
    solution = await loop.run_in_executor(None, sudoku_service.solve, body.board)
    return SudokuSolveResponse(board=body.board, solution=solution)
