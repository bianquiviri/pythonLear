"""Integration tests: HTTP API against the real FastAPI app + database."""

from __future__ import annotations

import httpx
import pytest

NEW_CLIENT = {
    "name": "Test Client",
    "email": "client@test.dev",
    "phone": "+1-555-9999",
    "address": "42 Testing Ave",
}


async def test_health_is_public(api: httpx.AsyncClient):
    response = await api.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_ready_reports_database(api: httpx.AsyncClient):
    response = await api.get("/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "ok"


async def test_openapi_documentation_available(api: httpx.AsyncClient):
    response = await api.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/clients" in paths
    assert "/api/v1/auth/login" in paths


async def test_clients_require_authentication(api: httpx.AsyncClient):
    response = await api.get("/api/v1/clients")
    assert response.status_code == 401


async def test_login_with_wrong_password_returns_401(api: httpx.AsyncClient, admin_token: str):
    response = await api.post(
        "/api/v1/auth/login", json={"email": "admin@test.dev", "password": "nope"}
    )
    assert response.status_code == 401


async def test_me_returns_current_user(api: httpx.AsyncClient, auth_headers: dict):
    response = await api.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "admin@test.dev"
    assert body["role"] == "admin"


async def test_client_crud_flow(api: httpx.AsyncClient, auth_headers: dict):
    created = await api.post("/api/v1/clients", json=NEW_CLIENT, headers=auth_headers)
    assert created.status_code == 201, created.text
    client_id = created.json()["id"]

    fetched = await api.get(f"/api/v1/clients/{client_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["email"] == NEW_CLIENT["email"]

    updated = await api.put(
        f"/api/v1/clients/{client_id}",
        json={"phone": "+1-555-0000", "is_active": False},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["phone"] == "+1-555-0000"
    assert updated.json()["is_active"] is False

    listed = await api.get("/api/v1/clients?search=test", headers=auth_headers)
    assert listed.status_code == 200
    assert listed.json()["meta"]["total"] == 1

    deleted = await api.delete(f"/api/v1/clients/{client_id}", headers=auth_headers)
    assert deleted.status_code == 204

    missing = await api.get(f"/api/v1/clients/{client_id}", headers=auth_headers)
    assert missing.status_code == 404


async def test_duplicate_client_email_returns_409(api: httpx.AsyncClient, auth_headers: dict):
    first = await api.post("/api/v1/clients", json=NEW_CLIENT, headers=auth_headers)
    assert first.status_code == 201
    second = await api.post("/api/v1/clients", json=NEW_CLIENT, headers=auth_headers)
    assert second.status_code == 409


async def test_invalid_client_payload_returns_422(api: httpx.AsyncClient, auth_headers: dict):
    response = await api.post(
        "/api/v1/clients", json={"name": "", "email": "nope"}, headers=auth_headers
    )
    assert response.status_code == 422


async def test_delete_missing_client_returns_404(api: httpx.AsyncClient, auth_headers: dict):
    response = await api.delete("/api/v1/clients/9999", headers=auth_headers)
    assert response.status_code == 404


async def test_delete_requires_admin(api: httpx.AsyncClient, auth_headers: dict, api2=None):
    created = await api.post("/api/v1/clients", json=NEW_CLIENT, headers=auth_headers)
    client_id = created.json()["id"]
    bad_token = "not-a-valid-token"
    response = await api.delete(
        f"/api/v1/clients/{client_id}", headers={"Authorization": f"Bearer {bad_token}"}
    )
    assert response.status_code == 401


async def test_pagination_meta(api: httpx.AsyncClient, auth_headers: dict):
    for i in range(3):
        await api.post(
            "/api/v1/clients",
            json={"name": f"Bulk {i}", "email": f"bulk{i}@test.dev"},
            headers=auth_headers,
        )
    response = await api.get("/api/v1/clients?page=1&per_page=2", headers=auth_headers)
    body = response.json()
    assert len(body["items"]) == 2
    assert body["meta"] == {"page": 1, "per_page": 2, "total": 3, "pages": 2}


@pytest.mark.parametrize("path", ["/docs", "/redoc"])
async def test_swagger_and_redoc_available(api: httpx.AsyncClient, path: str):
    response = await api.get(path)
    assert response.status_code == 200
