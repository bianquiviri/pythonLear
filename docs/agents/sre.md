# SRE agent rules

Owns: Docker, CI/CD, observability, environments.

## Docker

- One service per container: `db` (postgres:16-alpine), `backend` (uvicorn),
  `frontend` (nginx serving the built SPA).
- Every service has a `healthcheck`; `depends_on` uses `condition: service_healthy`.
- Multi-stage builds; images pinned to minor versions; `.dockerignore` excludes
  `.venv`, `node_modules`, `.env`, tests.
- No secrets in `docker-compose.yml` — everything via `env_file: .env` or `${VAR}`.

## CI/CD

- `ci.yml` must stay under ~10 minutes; use pip/npm caches and gha Docker layer cache.
- Images are published to GHCR only from `cd-staging.yml` (never from PRs).
- Staging deploy: SSH with a deploy key stored as `STAGING_SSH_KEY` GitHub secret.
  Failures must surface the smoke test output.
- Rollback = redeploy the previous image tag (`ghcr.io/<repo>/<svc>:<sha>`).

## Observability

- `/health` = liveness (no dependencies), `/ready` = readiness (DB ping).
- Structured-ish log line per request: method, path, status, ms — keep it greppable.
- Docker healthchecks must match those endpoints.
- When adding a service: add healthcheck + wire `depends_on` + update `docs/sre.md` if needed.

## Environments

- `ENVIRONMENT=development|test|production` controls fail-fast secret checks.
- Production must never boot with default `JWT_SECRET` or `SEED_ADMIN_PASSWORD`.
- Database volume `pgdata` is the only stateful volume; document backup expectations
  in the issue before changing volume names.
