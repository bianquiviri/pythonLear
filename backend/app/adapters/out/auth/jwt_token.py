"""JWT token provider adapter."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from app.config import get_settings
from app.domain.errors import AuthenticationError


class JwtTokenProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self._secret = settings.jwt_secret.get_secret_value()
        self._algorithm = settings.jwt_algorithm
        self._expires = timedelta(minutes=settings.jwt_expires_min)

    def encode(self, subject: str, role: str) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": subject,
            "role": role,
            "iat": now,
            "exp": now + self._expires,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode(self, token: str) -> dict[str, object]:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationError("Token expired") from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationError("Invalid token") from exc
        return payload
