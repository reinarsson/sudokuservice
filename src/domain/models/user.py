from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class User(BaseModel):
    """Domain model representing an authenticated user."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    hashed_password: str
