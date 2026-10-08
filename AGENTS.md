# AGENTS.md — Rules for AI agents working on this project

These rules apply to every agent (human or AI). Role-specific rules live in
`docs/agents/<role>.md` and take precedence for that role.

## Project overview

Small SPA for viewing/managing client data:

- **Backend**: FastAPI, hexagonal architecture, PostgreSQL, JWT auth, Swagger UI at `/docs`
- **Frontend**: Nuxt 4 (SPA, `ssr: false`), served by nginx, proxies `/api` to the backend
- **Everything runs in Docker** via `docker compose up --build`

## Non-negotiable principles

1. **KISS** — smallest solution that satisfies the requirement. No speculative abstractions.
2. **Hexagonal (ports & adapters)** — dependency rule: `domain` ← `application` ← `adapters`.
   - `app/domain`: pure entities/rules, zero framework imports.
   - `app/application`: use cases, depends only on domain + ports (`Protocol`).
   - `app/ports`: interfaces implemented by outbound adapters.
   - `app/adapters/inbound`: FastAPI routers/DTOs. `app/adapters/out`: DB, auth.
   - Never import a framework in `domain` or `application`. Never import `adapters` from `domain`.
   - Note: the inbound folder is `inbound/` because `in` is a Python keyword.
3. **TDD** — write/adjust the failing test first, then the minimum code to pass, then refactor.
   - Backend gate: `pytest` green, coverage ≥ 80% (`fail_under` in `pyproject.toml`).
   - Frontend gate: `npm test` green; logic in composables should be covered.
4. **Secrets in `.env` only** — `.env` is gitignored. Ship `.env.example` with placeholders.
   - Never hardcode keys, tokens, passwords, connection strings, or JWT secrets.
   - CI uses GitHub Secrets. Production must fail at boot with a default `JWT_SECRET`.
   - `detect-secrets` pre-commit hook must pass.
5. **Swagger is the API contract** — every endpoint needs: `summary`, sensible tags,
   request/response models, and error responses (401/403/404/409/422). Breaking changes
   require a version bump in the path (`/api/v1/...`) or an issue labeled `breaking`.

## GitFlow

- `main` — production. Protected. Only `release/*` and `hotfix/*` merge here.
- `develop` — integration. All work branches off from here.
- `feature/<issue-number>-<slug>` → PR into `develop`.
- `release/x.y.z` → PR into `main` (and back-merge to `develop`).
- `hotfix/<slug>` → PR into `main` **and** `develop`.
- Never commit directly to `main` or `develop`. Use `--no-ff` merges (GitHub PRs do this).

## CI/CD (GitHub Actions)

- `ci.yml` — runs on PRs and pushes to `main`/`develop`: ruff, mypy, pytest+coverage,
  eslint, vitest, docker build, integration tests against real PostgreSQL.
- `cd-staging.yml` — push to `develop`, manual dispatch, or an issue labeled `deploy`:
  build/push images to GHCR, deploy over SSH, run smoke test.
- `issue-driven.yml` — labels on issues trigger jobs:
  `qa-run`, `security-scan`, `sre-check`.
- All gates must be green before merging a PR.

## Definition of done (every issue)

- [ ] Tests written first and passing; coverage not decreased.
- [ ] `ruff check`, `mypy`, `eslint` clean.
- [ ] `docker compose up --build` works from a clean checkout (with `.env` created from example).
- [ ] API changes reflected in Swagger and `.env.example` if new config is needed.
- [ ] No secrets in the diff.
- [ ] PR follows GitFlow and references the issue.

## Commands

```bash
cp .env.example .env          # once
make dev                      # docker compose up --build
make test                     # backend pytest + coverage
make lint                     # ruff + eslint
make smoke                    # end-to-end smoke test
```
