from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from api.v1.auth_router import router as auth_router
from api.v1.sudoku_router import router as sudoku_router
from core.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown hooks."""
    yield


def create_app() -> FastAPI:
    """Factory function to build the FastAPI application."""
    app = FastAPI(title="Auth Service", version="1.0.0", lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(sudoku_router)
    return app


app = create_app()
