"""Unit tests: ClientService use cases with an in-memory fake repository."""

from __future__ import annotations

import pytest

from app.application.client_services import (
    ClientService,
    CreateClientCommand,
    UpdateClientCommand,
)
from app.domain.client import Client
from app.domain.errors import ConflictError, NotFoundError, ValidationError


class FakeClientRepo:
    def __init__(self) -> None:
        self._items: dict[int, Client] = {}
        self._next_id = 1

    async def add(self, client: Client) -> Client:
        client.id = self._next_id
        self._next_id += 1
        self._items[client.id] = client
        return client

    async def get(self, client_id: int) -> Client | None:
        return self._items.get(client_id)

    async def list(self, *, page=1, per_page=20, search=None):
        items = list(self._items.values())
        if search:
            needle = search.lower()
            items = [c for c in items if needle in c.name.lower() or needle in c.email]
        total = len(items)
        start = (page - 1) * per_page
        return items[start : start + per_page], total

    async def save(self, client: Client) -> Client:
        self._items[client.id] = client
        return client

    async def delete(self, client_id: int) -> bool:
        return self._items.pop(client_id, None) is not None

    async def email_exists(self, email: str) -> bool:
        return any(c.email == email.lower() for c in self._items.values())


@pytest.fixture
def service() -> ClientService:
    return ClientService(FakeClientRepo())


async def test_create_returns_persisted_client(service: ClientService):
    client = await service.create(CreateClientCommand(name="Ada", email="ada@example.com"))
    assert client.id is not None
    fetched = await service.get(client.id)
    assert fetched.email == "ada@example.com"


async def test_create_duplicate_email_conflicts(service: ClientService):
    await service.create(CreateClientCommand(name="Ada", email="ada@example.com"))
    with pytest.raises(ConflictError):
        await service.create(CreateClientCommand(name="Other", email="ada@example.com"))


async def test_create_invalid_data_raises_validation(service: ClientService):
    with pytest.raises(ValidationError):
        await service.create(CreateClientCommand(name="", email="bad"))


async def test_get_missing_client_raises_not_found(service: ClientService):
    with pytest.raises(NotFoundError):
        await service.get(999)


async def test_list_paginates_and_searches(service: ClientService):
    for i in range(5):
        await service.create(CreateClientCommand(name=f"Client {i}", email=f"c{i}@x.dev"))
    page1, total = await service.list(page=1, per_page=2)
    assert total == 5 and len(page1) == 2
    found, total_found = await service.list(search="client 3")
    assert total_found == 1 and found[0].email == "c3@x.dev"


async def test_update_modifies_client(service: ClientService):
    client = await service.create(CreateClientCommand(name="Ada", email="ada@example.com"))
    updated = await service.update(client.id, UpdateClientCommand(phone="+1-555", is_active=False))
    assert updated.phone == "+1-555"
    assert updated.is_active is False


async def test_delete_removes_client(service: ClientService):
    client = await service.create(CreateClientCommand(name="Ada", email="ada@example.com"))
    await service.delete(client.id)
    with pytest.raises(NotFoundError):
        await service.get(client.id)


async def test_delete_missing_raises(service: ClientService):
    with pytest.raises(NotFoundError):
        await service.delete(42)
