"""bcrypt password hasher adapter."""

from __future__ import annotations

import bcrypt


class BcryptPasswordHasher:
    def hash(self, plain: str) -> str:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode(), hashed.encode())
        except ValueError:
            return False
