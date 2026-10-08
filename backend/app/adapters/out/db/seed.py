"""Seed the database with an admin user and sample clients (idempotent)."""

from __future__ import annotations

import asyncio

from sqlalchemy import func, select

from app.adapters.out.auth.pwd import BcryptPasswordHasher
from app.adapters.out.db.client_repository import SqlClientRepository
from app.adapters.out.db.models import ClientRow, UserRow
from app.adapters.out.db.session import dispose_engine, get_session_factory
from app.adapters.out.db.user_repository import SqlUserRepository
from app.application.client_services import ClientService, CreateClientCommand
from app.config import get_settings
from app.domain.user import ROLE_ADMIN, User

SAMPLE_CLIENTS = [
    ("Acme Corp", "contact@acme-corp.com", "+1-555-0100", "123 Main St, Springfield"),
    ("Globex", "hello@globex.io", "+1-555-0101", "1 Infinite Loop, Silicon Valley"),
    ("Initech", "info@initech-erp.com", "+1-555-0102", "500 Powel St, San Francisco"),
    ("Umbrella Ltd", "sales@umbrella-ltd.net", "+1-555-0103", "16 South Park St"),
    ("Wayne Enterprises", "bruce@wayne-enterprises.com", "+1-555-0104", "1007 Mountain Dr, Gotham"),
]


async def seed() -> None:
    settings = get_settings()
    factory = get_session_factory()
    async with factory() as session:
        admin_email = settings.seed_admin_email.lower()
        existing = await session.scalar(select(UserRow).where(UserRow.email == admin_email))
        if existing is None:
            user_repo = SqlUserRepository(session)
            await user_repo.add(
                User(
                    email=admin_email,
                    password_hash=BcryptPasswordHasher().hash(
                        settings.seed_admin_password.get_secret_value()
                    ),
                    full_name="Administrator",
                    role=ROLE_ADMIN,
                )
            )
            print(f"[seed] admin user created: {admin_email}")

        client_count = await session.scalar(select(func.count()).select_from(ClientRow))
        if not client_count:
            repo = SqlClientRepository(session)
            service = ClientService(repo)
            for name, email, phone, address in SAMPLE_CLIENTS:
                await service.create(
                    CreateClientCommand(name=name, email=email, phone=phone, address=address)
                )
            print(f"[seed] {len(SAMPLE_CLIENTS)} sample clients created")
        await session.commit()
    await dispose_engine()


if __name__ == "__main__":
    asyncio.run(seed())
