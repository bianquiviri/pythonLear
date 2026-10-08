#!/usr/bin/env bash
# Smoke test: verifies the whole stack is alive.
# Usage: bash .github/scripts/smoke.sh [BASE_URL]
set -euo pipefail

BASE="${1:-http://localhost}"
BACKEND="${BACKEND_URL:-${BASE}}"
FRONTEND="${FRONTEND_URL:-http://localhost:3000}"

echo "==> Backend health"
curl -fsS "${BACKEND}/health" | grep -q '"status":"ok"'

echo "==> Backend readiness"
curl -fsS "${BACKEND}/ready" | grep -q '"status":"ready"'

echo "==> OpenAPI / Swagger"
curl -fsS "${BACKEND}/openapi.json" | grep -q '"Clients SPA API"'
curl -fsS -o /dev/null -w "%{http_code}\n" "${BACKEND}/docs" | grep -q 200

echo "==> Login with seeded admin"
TOKEN=$(curl -fsS -X POST "${BACKEND}/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"${SEED_ADMIN_EMAIL:-admin@example.com}\",\"password\":\"${SEED_ADMIN_PASSWORD:-change-me-admin}\"}" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')

echo "==> List clients"
COUNT=$(curl -fsS "${BACKEND}/api/v1/clients" -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["meta"]["total"])')
echo "    clients in DB: ${COUNT}"
test "${COUNT}" -gt 0

echo "==> Frontend served"
curl -fsS "${FRONTEND}/" | grep -qi "<!doctype html"

echo "SMOKE OK"
