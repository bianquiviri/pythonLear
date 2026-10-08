# QA agent rules

Owns: test strategy, quality gates, release verification.

## Test strategy (TDD)

- **Unit** (`backend/tests/unit`): domain rules and use cases with fakes for ports.
  Fast, no network, no DB.
- **Integration** (`backend/tests/integration`): real FastAPI app + database through
  HTTP (`httpx.ASGITransport`). Covers auth, CRUD, pagination, error codes, Swagger.
- **Frontend** (`frontend/tests`): vitest for pure logic (composables, error mapping).
- **E2E smoke** (`.github/scripts/smoke.sh`): health, ready, Swagger, login, list, UI served.

## Rules

- Write the test first (red), then the code (green), then refactor.
- Every bug fix needs a regression test that fails without the fix.
- Assert on status codes and payloads, not just "no exception".
- Use `data-testid` attributes in the frontend for stable selectors.

## Gates (must be green to merge)

| Gate | Command |
|---|---|
| Backend lint | `ruff check . && ruff format --check .` (backend/) |
| Types | `mypy app` (backend/) |
| Tests + coverage | `pytest --cov=app` — ≥ 80% enforced by `fail_under` |
| Frontend lint | `npm run lint` |
| Frontend tests | `npm test` |
| Build | `docker compose build` |
| Smoke | `make smoke` with the stack up |

## Coverage & reporting

- Coverage badge: `pytest --cov --cov-report=json && python ../scripts/make_badge.py
  coverage.json ../docs/coverage-badge.svg`.
- Coverage that drops below 80% is a failed build, not a warning.
- Label an issue `qa-run` to trigger the full suite from GitHub.

## Release verification (GitFlow `release/*`)

1. All CI jobs green on the release branch.
2. `docker compose up --build` from a clean checkout + `.env` from `.env.example`.
3. `make smoke` passes (seeded admin login + client list).
4. Swagger `/docs` matches the implemented API.
