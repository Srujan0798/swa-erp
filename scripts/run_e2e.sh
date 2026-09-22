#!/usr/bin/env bash
# Isolated E2E runner: E2E tests NEVER touch the seeded real DB.
#
# Creates a scratch postgres DB (swa_erp_e2e), migrates + seeds it, boots an
# isolated backend (:8200) and frontend (:3200) pointed at the scratch DB,
# runs Playwright, then tears everything down.
#
# Why: the dev stack (:3100 -> :8100) reads the host DB seeded by
# `make swa-live-local`. Running Playwright against it pollutes real data
# (E2E Client* rows). This script isolates the blast radius to scratch.
set -euo pipefail

cd "$(dirname "$0")/.."

SCRATCH_DB="${SCRATCH_DB:-swa_erp_e2e}"
BACKEND_PORT="${E2E_BACKEND_PORT:-8200}"
FRONTEND_PORT="${E2E_FRONTEND_PORT:-3200}"
SCRATCH_URL="postgresql://swa:swa@localhost:5432/${SCRATCH_DB}"

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
  [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "=== 1/6 fresh scratch DB: ${SCRATCH_DB} ==="
psql -U swa -d postgres -c "DROP DATABASE IF EXISTS ${SCRATCH_DB};" >/dev/null
psql -U swa -d postgres -c "CREATE DATABASE ${SCRATCH_DB};" >/dev/null

echo "=== 2/6 migrate scratch ==="
DATABASE_URL="$SCRATCH_URL" alembic -c src/backend/alembic.ini upgrade heads

echo "=== 3/6 seed scratch users ==="
DATABASE_URL="$SCRATCH_URL" python3 scripts/seed_dev.py

echo "=== 4/6 boot isolated backend :${BACKEND_PORT} ==="
DISABLE_AUTH_RATE_LIMIT=true DATABASE_URL="$SCRATCH_URL" \
  uvicorn src.backend.main:app --host 0.0.0.0 --port "$BACKEND_PORT" \
  > /tmp/opencode/e2e-backend.log 2>&1 &
BACKEND_PID=$!
for _ in $(seq 1 30); do
  curl -sf -m 2 "http://localhost:${BACKEND_PORT}/healthz" >/dev/null && break
  sleep 1
done
curl -sf -m 2 "http://localhost:${BACKEND_PORT}/healthz" >/dev/null || {
  echo "backend failed to start; see /tmp/opencode/e2e-backend.log"; exit 1; }

echo "=== 5/6 boot isolated frontend :${FRONTEND_PORT} ==="
BACKEND_URL="http://localhost:${BACKEND_PORT}" \
  npm --prefix src/frontend run dev -- --port "$FRONTEND_PORT" \
  > /tmp/opencode/e2e-frontend.log 2>&1 &
FRONTEND_PID=$!
for _ in $(seq 1 30); do
  curl -sf -m 2 "http://localhost:${FRONTEND_PORT}/" >/dev/null && break
  sleep 1
done
curl -sf -m 2 "http://localhost:${FRONTEND_PORT}/" >/dev/null || {
  echo "frontend failed to start; see /tmp/opencode/e2e-frontend.log"; exit 1; }

echo "=== 6/6 playwright ==="
E2E_BASE_URL="http://localhost:${FRONTEND_PORT}" \
  E2E_API_URL="http://localhost:${BACKEND_PORT}" \
  E2E_WEB_CMD="true" \
  npx playwright test tests/e2e/

echo "E2E complete — scratch DB ${SCRATCH_DB} left in place for inspection (drop with: psql -U swa -d postgres -c 'DROP DATABASE ${SCRATCH_DB};')"
