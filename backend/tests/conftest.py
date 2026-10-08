"""Shared test fixtures — in-memory SQLite, app factory, auth helpers."""

from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET", "test-secret-do-not-use-in-prod")
os.environ.setdefault("RATE_LIMIT", "1000/minute")

import httpx
import pytest
import pytest_asyncio

from app.adapters.out.auth.pwd import BcryptPasswordHasher
from app.adapters.out.db.models import Base, UserRow
from app.adapters.out.db.session import dispose_engine, get_engine, get_session_factory
from app.config import get_settings
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def database():
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await dispose_engine()
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def api() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def admin_token(api: httpx.AsyncClient) -> str:
    factory = get_session_factory()
    async with factory() as session:
        session.add(
            UserRow(
                email="admin@test.dev",
                password_hash=BcryptPasswordHasher().hash("admin-pass-123"),
                full_name="Admin",
                role="admin",
            )
        )
        await session.commit()
    response = await api.post(
        "/api/v1/auth/login", json={"email": "admin@test.dev", "password": "admin-pass-123"}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}
