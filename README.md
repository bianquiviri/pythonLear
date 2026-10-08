# Clients SPA

Small SPA for viewing and managing client data.

- **Backend**: FastAPI + hexagonal architecture + PostgreSQL + JWT auth — Swagger at `/docs`
- **Frontend**: Nuxt 4 SPA (nginx, proxies `/api` to the backend)
- **Quality**: TDD, coverage ≥ 80%, ruff/mypy/eslint, pre-commit, GitHub Actions CI/CD
- **Everything in Docker**: `docker compose up --build`

[![CI](https://github.com/bianquiviri/pythonLear/actions/workflows/ci.yml/badge.svg)](https://github.com/bianquiviri/pythonLear/actions/workflows/ci.yml)
![coverage](docs/coverage-badge.svg)

## Quick start

```bash
cp .env.example .env      # then edit the secrets (JWT_SECRET, passwords)
make dev                  # docker compose up --build
```

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:3000        |
| API + Swagger | http://localhost:8000/docs |
| OpenAPI   | http://localhost:8000/openapi.json |
| Health    | http://localhost:8000/health |

Seeded admin credentials come from `.env` (`SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`),
plus 5 sample clients.

## Development

```bash
make test     # backend: pytest + coverage (fail under 80%)
make lint     # ruff + eslint
make smoke    # end-to-end smoke test against the running stack
```

Frontend only: `cd frontend && npm install && npm run dev` (proxies `/api` to `localhost:8000`).

## Architecture

```
backend/app/
├── domain/          # pure entities & rules (no frameworks)
├── application/     # use cases (depend only on domain + ports)
├── ports/           # Protocol interfaces
└── adapters/
    ├── inbound/     # FastAPI routers + DTOs (web)
    └── out/         # PostgreSQL, bcrypt, JWT, seed
```

Dependency rule: `domain ← application ← adapters`.

## GitFlow

`feature/<issue>-<slug>` → `develop` → `release/x.y.z` → `main`.
See [AGENTS.md](AGENTS.md) and `docs/agents/` for role-specific rules
(backend, frontend, SRE, security, QA).

## Secrets

Real values live only in `.env` (gitignored). `.env.example` documents every variable.
CI uses GitHub Secrets. `detect-secrets` pre-commit hook prevents accidental leaks.

## GitHub automation

| Trigger | Result |
|---|---|
| PR to `develop`/`main` | `ci.yml`: lint, tests, coverage, docker build, postgres integration |
| Push to `develop` | `cd-staging.yml`: build/push GHCR + SSH deploy + smoke test |
| Issue label `deploy` | Manual staging deploy |
| Issue label `qa-run` | Full test suite runs and reports |
| Issue label `security-scan` | pip-audit + npm audit + Trivy |
| Issue label `sre-check` | Image build + health endpoint verification |
