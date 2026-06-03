from __future__ import annotations

import bcrypt


class PasswordHasher:
    """Adapter for password hashing using bcrypt."""

    def hash(self, password: str) -> str:
        """Hash a plaintext password."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a plaintext password against its hash."""
        return bcrypt.checkpw(password.encode(), hashed.encode())
