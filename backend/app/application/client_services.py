"""Client use cases — framework-free application layer."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.client import Client
from app.domain.errors import ConflictError, NotFoundError
from app.ports import ClientRepository


@dataclass(frozen=True)
class CreateClientCommand:
    name: str
    email: str
    phone: str | None = None
    address: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class UpdateClientCommand:
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class ClientService:
    def __init__(self, repository: ClientRepository) -> None:
        self._repository = repository

    async def create(self, cmd: CreateClientCommand) -> Client:
        if await self._repository.email_exists(cmd.email):
            raise ConflictError(f"a client with email {cmd.email} already exists")
        client = Client(
            name=cmd.name,
            email=cmd.email,
            phone=cmd.phone,
            address=cmd.address,
            notes=cmd.notes,
        )
        return await self._repository.add(client)

    async def get(self, client_id: int) -> Client:
        client = await self._repository.get(client_id)
        if client is None:
            raise NotFoundError("Client", client_id)
        return client

    async def list(
        self, *, page: int = 1, per_page: int = 20, search: str | None = None
    ) -> tuple[list[Client], int]:
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        return await self._repository.list(page=page, per_page=per_page, search=search)

    async def update(self, client_id: int, cmd: UpdateClientCommand) -> Client:
        client = await self.get(client_id)
        client.update(
            name=cmd.name,
            phone=cmd.phone,
            address=cmd.address,
            notes=cmd.notes,
            is_active=cmd.is_active,
        )
        return await self._repository.save(client)

    async def delete(self, client_id: int) -> None:
        deleted = await self._repository.delete(client_id)
        if not deleted:
            raise NotFoundError("Client", client_id)
