# Wave-48 Task 01 — Production hardening: rate limiting, audit trail, frontend resilience, accessibility

**This is proactive, not close-out.** Found by a live audit of the real system, not by re-reading reports. The archetype (`internal-tool`, ADAPTOID-LITE.md §14) names exactly these as the priorities to emphasize: **domain model + lifecycle; RBAC; audit log; vertical slices** — this wave closes the audit-log and RBAC-adjacent gaps that priority calls out.

## Verified findings (orchestrator measured these — do not re-derive)

| # | Finding | Evidence |
|---|---|---|
| 1 | **Rate limiting covers only `/auth/login`.** All 26 other routers are unprotected — including file upload (Excel import), PDF/report generation, and BOQ parsing, which are the expensive endpoints most worth throttling. | `grep -rn "rate_limit\|Limiter" src/backend/api/*.py` → 0 hits; only `src/backend/core/rate_limit.py` + `main.py` wire it, both auth-only |
| 2 | **Audit trail covers 1 of 30 services.** `AuditLog` model exists (`src/backend/models/audit_log.py`) but only `time_service.py` writes to it. `invoice_service.py` and `src/backend/api/users.py` — the money and RBAC-sensitive paths — write nothing. | grep across `services/*.py` and `api/users.py` |
| 3 | **No React error boundary anywhere.** One unhandled render error white-screens the entire app for a user mid-task, with no recovery path. | `grep -rl "ErrorBoundary" src/frontend/src` → 0 results |
| 4 | **Accessibility is thin.** Only 18 of 98 non-test `.tsx` files reference `aria-*` or `role=`. This is a daily-use internal tool — a real accessibility gap, not a cosmetic one. | file count |

## Files you own
- `src/backend/core/rate_limit.py` (extend, don't rewrite)
- `src/backend/api/{import_.py or wherever Excel upload lives, export*.py, reports.py}` — check the actual filenames first
- `src/backend/services/invoice_service.py`, `src/backend/api/users.py`
- `src/frontend/src/components/ErrorBoundary.tsx` (new)
- `src/frontend/src/App.tsx` (wrap root route tree only)
- Accessibility: only the highest-traffic components — do not attempt all 98 files in one wave

## The work

### 1. Extend rate limiting to expensive endpoints
Reuse the existing `IPRateLimiter` pattern from `core/rate_limit.py`. Apply to: Excel/BOQ import upload, PDF export, report generation. Pick sane limits (e.g. 10/min/IP for uploads, 20/min for exports) and make them configurable via settings, matching the existing `AUTH_RATE_LIMIT_PER_MIN` convention. Do NOT rate-limit read-heavy list/dashboard endpoints — that would hurt normal use.

### 2. Extend audit logging to money + RBAC paths
Add `AuditLog` writes to: invoice create/update/delete/status-change in `invoice_service.py`, and role/permission changes in `users.py`. Follow the exact pattern `time_service.py` already uses — do not invent a new schema.

### 3. Frontend error boundary
One `ErrorBoundary` component wrapping the app's route tree. On catch: log via the existing Sentry wiring (`core/errors.py` pattern, if a frontend equivalent exists — check first) and render a recoverable fallback UI (not a blank screen), with a "reload" action.

### 4. Accessibility on the highest-traffic surfaces
Target the core-chain pages first: Inquiries, Clients, Agreements, Tokens, Document References, Tasks. Add `aria-label`/`role` where genuinely missing on interactive elements (buttons, form inputs, modals). Do not do a mechanical sweep of every file — prioritize what real users touch daily.

## Acceptance criteria
- [ ] New endpoints return `429` after exceeding their limit — prove it with a real curl loop, paste output
- [ ] `AuditLog` rows are created on invoice mutation and role change — prove with a real DB query after triggering each
- [ ] Deliberately throw inside a child component; confirm the ErrorBoundary catches it and renders the fallback (not a blank page); revert the deliberate throw
- [ ] `npx eslint . --ext ts,tsx --max-warnings 0` still clean after accessibility changes
- [ ] Full backend + frontend suites still green (paste both)

## Deliver
`work/reports/wave-48/01-production-hardening.report.md`. Commit before writing it.

## Constraints
- Time budget: 150 min · commit per numbered item
- Do not touch `src/backend/core/rate_limit.py`'s auth-login behavior — extend only
- Every claim needs a command + output next to it. This project has a documented pattern of unverified reports.
