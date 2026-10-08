# Security agent rules

Owns: secrets, auth, hardening, dependency audits.

## Secrets management

- **Only** `.env` (gitignored) holds real values; `.env.example` ships placeholders.
- Never print secrets in logs, errors, API responses, or Swagger examples.
- `detect-secrets` pre-commit hook: baseline at `.secrets.baseline` (update via
  `detect-secrets scan --baseline .secrets.baseline` when legitimate secrets-looking
  strings are added).
- GitHub Secrets for CI: `STAGING_SSH_KEY`, `SEED_ADMIN_*`. Least-privilege `GITHUB_TOKEN`
  permissions in workflows (declare `permissions:` explicitly).
- `JWT_SECRET` in production: fail fast at boot (`Settings.ensure_secure`).

## AuthN / AuthZ

- JWT (HS256) with expiry (`JWT_EXPIRES_MIN`); bcrypt password hashing with salt.
- Generic 401 for unknown user or wrong password (no user enumeration).
- Role check server-side: admin-only routes use `require_admin`; never trust the client.
- Token sent only via `Authorization: Bearer` header.

## API hardening

- CORS restricted to `CORS_ORIGINS`; only GET/POST/PUT/DELETE + needed headers.
- Rate limiting via slowapi on every route (`RATE_LIMIT`).
- nginx adds `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`.
- Input validated twice: pydantic schemas at the edge, domain `validate()` inside.

## Audits (issue label `security-scan`)

- `pip-audit` for backend deps, `npm audit` for frontend, Trivy fs scan for HIGH/CRITICAL.
- Fix or justify every finding in the issue; no `--force` blind upgrades.
- Review PRs touching: auth, headers, CORS, env/config, Dockerfiles, workflows.
