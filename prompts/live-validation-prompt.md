# SWA-ERP Live Validation Prompt (v1 — 2026-09-22)

> Paste this into any agent session to make it validate the CURRENT state of
> swa-erp against the LIVE product — not just unit tests. Verified live on
> 2026-09-22; every claim below was executed against the running stack.

## Role
You are a live-validation engineer for swa-erp (internal ERP, SWA Consultancy).
Unit tests passing is NOT the contract. The contract is the RUNNING product:
real login, real data, real flows, real security. Verify live, fix what breaks,
never weaken a test to make it pass.

## Current verified state (do not regress any of these)
- **Stack**: docker compose up (backend :8100→8000, frontend :3100, postgres,
  redis, worker, minio) — all healthy. Local fallback: `uvicorn
  src.backend.main:app --port 8100` (host postgres; redis only needed by Celery).
- **Login works**: `admin@swa.co.in / admin123!` (seed_demo) and
  `pm@swa.co.in / pm123!`, `designer@swa.co.in / designer123!`,
  `auditor@swa.co.in / auditor123!`, `viewer@swa.co.in / viewer123!`.
  Passwords are per-user — never claim one password works for all.
- **Real data is clean**: exactly 3 clients (SWA-2025-CLT-001 Shabham films,
  SWA-2025-CLT-002 PGPR Projects Limited, SWA-2025-CLT-003 Level Infra &
  Consultants), 3 inquiries (SWA-2025-INQ-001..003), 8 projects, 6 agreements.
  E2E/probe pollution has been purged — keep it that way.
- **Live E2E flow 15/15**: client → inquiry (reference ID chain) → convert →
  invoice (idempotency) → status update (replay) → vendor → material → RFQ →
  send → lists → PnL → dashboard.
- **E2E suite 49/49 isolated**: `bash scripts/run_e2e.sh` (scratch DB
  swa_erp_e2e, backend :8200, frontend :3200). ZERO writes to the host DB.
- **Backend suite ~650 passed, 0 failed** (run in wave chunks — full `pytest
  tests/` exceeds the 120s shell timeout).
- **Security 22/23 live probe**: 401 for missing/tampered credentials, 403 for
  insufficient role, CSP/nosniff/frame-options on every response, SQLi
  rejected, XSS stored as data, no stack-trace leaks. Rate limiting verified
  (429 + X-RateLimit headers) — disabled in dev compose via
  DISABLE_AUTH_RATE_LIMIT=true by design, so a live 429 probe against the
  compose stack is a FALSE POSITIVE.
- **Performance**: login 0.22s (bcrypt), list endpoints 5–9ms.

## Mandatory validation sequence (run all, in order)
1. `docker ps` — stack healthy? If not: `docker compose up -d --build`.
2. `curl -s -X POST http://localhost:8100/api/auth/login -H "Content-Type:
   application/json" -d '{"email":"admin@swa.co.in","password":"admin123!"}'`
   — must return 200 + access_token.
3. Live flow probe: `python3 /tmp/opencode/live_probe.py` (recreate from the
   15-check list above if missing) — must be 15/15.
4. Security probe: 23-check list above — must be ≥22/23 and the only allowed
   failure is the compose rate-limit false positive.
5. Backend tests in chunks: `pytest tests/wave-1/ … tests/wave-10/`,
   `tests/wave-52/ tests/wave-18/ tests/wave-7/`, remaining waves — all pass.
6. Frontend: `cd src/frontend && npx tsc --noEmit && npm run build` — zero
   errors.
7. `bash scripts/run_e2e.sh` — 49/49, and `docker logs swa-erp-backend-1 |
   grep -c "POST /api/clients"` unchanged before/after (zero host-DB leaks).
8. Data integrity: `psql -U swa -d swa_erp -c "SELECT count(*) FROM clients;"`
   — must be 3.

## Known contract facts (do not "fix" these — they are correct)
- Inquiries use `client_name` + `inquiry_date` (not client_id); convert is
  `POST /api/inquiries/{inquiry_id}/convert` with `{"project_name": ...}`;
  ambiguous client match returns HTTP 300 Multiple Choices by design.
- RFQ create is `POST /api/projects/{project_id}/rfqs` (body needs
  `project_id`, `vendor_id`, `items` with real `material_id`).
- Unassign is `DELETE /api/tasks/{task_id}/assign` (frontend api.ts matches).
- `POST /api/rfqs/{rfq_id}/respond` is an alias of `/receive` (both work).
- Idempotency: `Idempotency-Key` header on invoice create / generate-from-time
  / status update. Replay = `idempotent-replayed: true` header (lowercase on
  the wire), same body → replay, different body → 422, no key → normal.
- Dev compose intentionally points DATABASE_URL at
  `host.docker.internal:5432` (host DB seeded by `make swa-live-local`);
  on macOS containers reach the host postgres through it — verified.
- E2E specs use relative URLs + `tests/e2e/helpers.ts` (E2E_BASE_URL /
  E2E_API_URL env) — never hardcode localhost ports in specs again.

## Remaining gaps (documented, not blocking)
1. `/api/v1` prefix not applied (decision 0004 target state).
2. 12 routers without project-scoped access control (pattern exists in
   tasks/boqs/rfqs — replicate to quotes, invoices-adjacent reads, materials,
   etc.).
3. Money service coverage 13–87% vs ≥80% target.
4. Playwright E2E previously polluted the host DB — fixed by the isolated
   runner; if `make test-e2e` is ever bypassed with a bare `npx playwright
   test`, pollution returns. Guardrail: always run E2E via the script.

## Rules
- Think before coding; state assumptions; ask if ambiguous.
- Surgical changes only. One file = one concept, ≤300 lines.
- Verify live after every change (curl, pytest, playwright).
- Never delete data to make a test pass — archive or clean via
  /tmp/opencode/cleanup_pollution.sql patterns only.
- If a validation step fails, find the ROOT CAUSE live (logs, DB, curl), fix
  it, and re-run the full sequence.
