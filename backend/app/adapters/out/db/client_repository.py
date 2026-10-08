"""ClientRepository adapter over SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import func, or_, select

from app.adapters.out.db.models import ClientRow
from app.domain.client import Client


def _to_domain(row: ClientRow) -> Client:
    return Client(
        id=row.id,
        name=row.name,
        email=row.email,
        phone=row.phone,
        address=row.address,
        notes=row.notes,
        is_active=row.is_active,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_row(client: Client, row: ClientRow | None = None) -> ClientRow:
    target = row or ClientRow()
    target.name = client.name
    target.email = client.email
    target.phone = client.phone
    target.address = client.address
    target.notes = client.notes
    target.is_active = client.is_active
    return target


class SqlClientRepository:
    def __init__(self, session) -> None:
        self._session = session

    async def add(self, client: Client) -> Client:
        row = _to_row(client)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return _to_domain(row)

    async def get(self, client_id: int) -> Client | None:
        row = await self._session.get(ClientRow, client_id)
        return _to_domain(row) if row else None

    async def list(
        self, *, page: int = 1, per_page: int = 20, search: str | None = None
    ) -> tuple[list[Client], int]:
        query = select(ClientRow)
        count_query = select(func.count()).select_from(ClientRow)
        if search:
            pattern = f"%{search.strip()}%"
            condition = or_(
                ClientRow.name.ilike(pattern),
                ClientRow.email.ilike(pattern),
                ClientRow.phone.ilike(pattern),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)
        total = (await self._session.execute(count_query)).scalar_one()
        rows = (
            (
                await self._session.execute(
                    query.order_by(ClientRow.name).offset((page - 1) * per_page).limit(per_page)
                )
            )
            .scalars()
            .all()
        )
        return [_to_domain(row) for row in rows], int(total)

    async def save(self, client: Client) -> Client:
        row = await self._session.get(ClientRow, client.id)
        if row is None:
            raise ValueError(f"client {client.id} not found")
        _to_row(client, row)
        await self._session.flush()
        return _to_domain(row)

    async def delete(self, client_id: int) -> bool:
        row = await self._session.get(ClientRow, client_id)
        if row is None:
            return False
        await self._session.delete(row)
        return True

    async def email_exists(self, email: str) -> bool:
        count = await self._session.scalar(
            select(func.count()).select_from(ClientRow).where(ClientRow.email == email.lower())
        )
        return bool(count)
