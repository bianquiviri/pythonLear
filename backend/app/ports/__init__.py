"""Ports (interfaces) — implemented by adapters, used by application services."""

from __future__ import annotations

from typing import Protocol

from app.domain.client import Client
from app.domain.user import User


class ClientRepository(Protocol):
    async def add(self, client: Client) -> Client: ...

    async def get(self, client_id: int) -> Client | None: ...

    async def list(
        self, *, page: int = 1, per_page: int = 20, search: str | None = None
    ) -> tuple[list[Client], int]: ...

    async def save(self, client: Client) -> Client: ...

    async def delete(self, client_id: int) -> bool: ...

    async def email_exists(self, email: str) -> bool: ...


class UserRepository(Protocol):
    async def add(self, user: User) -> User: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def get(self, user_id: int) -> User | None: ...


class PasswordHasher(Protocol):
    def hash(self, plain: str) -> str: ...

    def verify(self, plain: str, hashed: str) -> bool: ...


class TokenProvider(Protocol):
    def encode(self, subject: str, role: str) -> str: ...

    def decode(self, token: str) -> dict[str, object]: ...
