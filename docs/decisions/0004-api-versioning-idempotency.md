# Decision: API Versioning & Idempotency Keys

## Status
Accepted — **implemented 2026-09-21** (shipped shape differs from the original proposal; see below)

## Shipped Implementation (as built)

### API Versioning (header strategy, not URL prefix)
- `X-API-Version: 1` on every `/api/*` response (`core/middleware.py`).
- OpenAPI `version` = package version from `pyproject.toml` (pinned by
  `tests/security/test_api_versioning.py`).
- Policy: additive-only within a major. The first **breaking** change ships as
  `/api/v2` URLs; v1 then gets a 6-month sunset via `Deprecation` + `Sunset`
  headers. Rationale: URL-prefixing 115 routes now buys nothing for a
  single-tenant internal tool with one SPA consumer and no external callers.
- `docs/ARCHITECTURE.md` §7 records the strategy.

### Idempotency Keys (Postgres-backed, not Redis)
- `Idempotency-Key` header accepted on: invoice create, invoice
  generate-from-time, invoice status change (`api/invoices.py`).
- Table `idempotency_keys` (migration `0042`): (key, user_id) → exact first
  response; TTL 24h enforced lazily on lookup; user_id cascades.
- Same key + same body → replayed stored response + `Idempotent-Replayed: true`.
- Same key + different body → `422` (dev-tooling contract tests chose 422 over
  the originally proposed 409; 422 also matches the rest of this API's
  validation-error family).
- Redis was rejected as the store: this app's Redis is a cache/queue, and
  idempotency must survive a Redis flush. Postgres rows are tiny (one per
  money-POST) and lazily expire.
- Contract pinned by `tests/wave-52/test_idempotency_keys.py`.

## Deferred Scope (deliberate)
- Idempotency on quotes/RFQs/tasks/exports — these are cheap to re-issue or
  already guarded (exports own their job rows). Add when retrying clients exist.
- `/api/v2` URL prefix + sunset headers — first breaking change only.

## Original Proposal (superseded where different)
URL-prefix `/api/v1` + Redis storage + mandatory keys with 400/409 responses.
Kept below for history:

## Current State
- All routes mounted at `/api/...` (no version prefix)
- No idempotency key support
- OpenAPI docs at `/docs` (internal tool)

## Target State

### API Versioning
```
Current:  /api/projects, /api/tasks, /api/exports, ...
Target:   /api/v1/projects, /api/v1/tasks, /api/v1/exports, ...
```

**Implementation approach:**
1. Create `src/backend/api/v1/__init__.py` that re-exports all routers with `/api/v1` prefix
2. Update `main.py` to include v1 router
3. Add deprecation headers on unversioned routes (6-month sunset)
4. Update frontend `lib/api.ts` base URL to `/api/v1`

**Versioning policy:**
- v1 = current contract
- Breaking changes → v2
- Additive changes (new optional fields, new endpoints) → same version
- Deprecation: 6 months notice via `Deprecation` header + `Sunset` header

### Idempotency Keys
**Scope:** All mutating endpoints involving money or external side effects:
- `POST /api/v1/quotes` (create quote)
- `POST /api/v1/rfqs` (create RFQ)
- `POST /api/v1/invoices` (create invoice)
- `POST /api/v1/projects/{id}/transition` (lifecycle transition)
- `POST /api/v1/exports/*` (async exports)
- `POST /api/v1/tasks` (create task)

**Header:** `Idempotency-Key: <uuid>` (client-generated, recommended v4 UUID)

**Behavior:**
- Server stores key + response for 24 hours (Redis with TTL)
- Duplicate key → return cached response (same status, same body)
- Missing key on idempotent endpoints → `400 Bad Request`
- Key mismatch (different request body) → `409 Conflict`

**Storage:**
```
Redis key: idempotency:{key}
Value: JSON {status_code, headers, body, created_at}
TTL: 86400 seconds (24h)
```

**Implementation:**
1. Middleware or dependency `require_idempotency_key` for tagged routes
2. Redis lookup on request
3. On first request: execute handler, store response, return
4. On duplicate: return stored response

## Migration Plan
| Phase | Action | Timeline |
|-------|--------|----------|
| 1 | Add `/api/v1` prefix router, keep `/api` working | Sprint 1 |
| 2 | Add idempotency middleware + Redis storage | Sprint 1 |
| 3 | Tag money-mutating endpoints with idempotency requirement | Sprint 2 |
| 4 | Update frontend to send versioned URLs + idempotency keys | Sprint 2 |
| 5 | Deprecate unversioned routes (headers) | Sprint 3 |
| 6 | Remove unversioned routes | Sprint 4 |

## Risks
- Frontend/backend deploy coupling during transition
- Idempotency key storage adds Redis dependency for writes
- Client retry logic must generate stable keys per user action

## Decision
Defer implementation until first breaking change or external API consumer. Document now to avoid accidental contract drift.

## Related
- `docs/ARCHITECTURE.md` (Section 5: API Surface)
- `src/backend/core/middleware.py` (future idempotency middleware location)