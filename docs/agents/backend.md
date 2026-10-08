# Backend agent rules

Owns: `backend/` (FastAPI + hexagonal + PostgreSQL).

## Architecture

- Follow the dependency rule strictly:
  `domain` → `application` → `ports` ← `adapters/out`, `adapters/inbound` → `application`.
- `domain/`: entities (`Client`, `User`) and `errors.py`. No imports from FastAPI,
  SQLAlchemy, pydantic, or any framework. Validation raises `ValidationError(field=...)`.
- `application/`: use cases as plain classes with async methods taking dataclass commands.
  Raise domain errors (`NotFoundError`, `ConflictError`, `AuthenticationError`).
- `ports/`: `Protocol` classes. New capability = new port first, adapter second.
- `adapters/inbound/web/`: routers are thin — parse DTO → call service → map errors via
  `translate_domain_error`. No business logic in routers.
- `adapters/out/`: SQLAlchemy repositories, bcrypt hasher, JWT provider, seed script.

## TDD workflow

1. Red: write the failing test in `tests/unit` (domain/service) or `tests/integration` (API).
2. Green: minimal implementation.
3. Refactor: ruff + mypy clean.
4. Gate: `pytest --cov=app` ≥ 80%, `ruff check .`, `mypy app`.

## API rules

- All routes under `/api/v1/`. Ops endpoints (`/health`, `/ready`) stay unversioned.
- Errors return `{"detail": "..."}` with the right status code.
- List endpoints are paginated: `page`, `per_page`, `search` + `meta {total, pages}`.
- Every endpoint documents `summary` and response models — Swagger must stay accurate.

## Security

- Passwords: bcrypt only, never logged. Login failures return a generic 401.
- JWT: `JWT_SECRET` from `.env` via pydantic-settings; production boot fails on default.
- Rate limiting via slowapi (`RATE_LIMIT`), CORS restricted to `CORS_ORIGINS`.
- Admin-only operations (e.g., delete) use the `require_admin` dependency.

## Database

- Migrations via Alembic: `alembic revision --autogenerate -m "..."`, commit the file.
- Repositories `flush`; commit happens once per request in `get_session`.
- Seed script (`app.adapters.out.db.seed`) must stay idempotent.
