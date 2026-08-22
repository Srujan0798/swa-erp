## Evidence

Command: static code review by feature-dev:code-reviewer agent (2026-08-23).
Verification: file:line citations in table below; no suite re-run claimed in this scratch file.

```
static analysis only — intermediate wave-37 scratch
```

# Wave-37 — Backend security findings

**Scope:** Read-only review of `src/backend/` (auth/RBAC, IDOR, secrets, SQLi, storage traversal, JWT, mass assignment, `/metrics`, CORS).  
**Method:** Static inspection of routers, deps, storage, config, compose templates. No exploit PoCs.  
**Bar:** Only findings with confidence ≥ 80. Cleared checks listed at the bottom.

| id | area | severity | evidence (file:line) | triage suggestion |
|----|------|----------|----------------------|-------------------|
| SEC-01 | Path traversal (storage) | Critical | [`src/backend/core/storage.py:42-52`](../../../src/backend/core/storage.py) — `LocalStorage._path` returns absolute paths unchanged; `save` does `self.root / key` with no `resolve()` + root containment check. Upload keys embed raw filenames: [`document_service.py:77-79`](../../../src/backend/services/document_service.py), [`boq_service.py:56-58`](../../../src/backend/services/boq_service.py). A filename like `../../evil` can write/read outside `uploads/`. | Reject `..` / absolute keys; `resolve()` then assert path is under `root`. Sanitize upload basenames (`Path(name).name` only). Add unit tests for traversal keys. |
| SEC-02 | `/metrics` exposure | High | [`src/backend/main.py:102-103`](../../../src/backend/main.py) — `_instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)` with no auth. Compose maps host `8100:8000` ([`docker-compose.prod.yml:84`](../../../docker-compose.prod.yml)). Endpoint can leak path/volume patterns and `failed_logins_total`. | Bind metrics to localhost / scrape network only, or require basic auth / network policy. Do not expose `/metrics` on the public app port. |
| SEC-03 | Secrets / prod defaults | Critical | [`docker-compose.prod.yml:61,74,76`](../../../docker-compose.prod.yml) — `SECRET_KEY: ${SECRET_KEY:-REPLACE_ME_IN_ENV_FILE}` and `POSTGRES_PASSWORD:-changeme_change_before_prod`. Validator only blocks `{"change-me","replace-with-openssl-rand-hex-32",""}` ([`config.py:4-5,33-39`](../../../src/backend/core/config.py)), so `REPLACE_ME_IN_ENV_FILE` and weak DB password start under `APP_ENV=production`. | Expand insecure-key denylist (or require min entropy). Fail compose if `SECRET_KEY` / `POSTGRES_PASSWORD` unset. Never ship usable prod defaults. |
| SEC-04 | IDOR — time tracking | High | [`src/backend/api/time_tracking.py:45-64`](../../../src/backend/api/time_tracking.py) list entries (optional `user_id` filter, no self-scope); [`67-81`](../../../src/backend/api/time_tracking.py) get any entry; [`103-128`](../../../src/backend/api/time_tracking.py) list/get any timesheet. Ownership enforced only on update/delete/submit ([`time_service.py:119-120,145-146,214-215`](../../../src/backend/services/time_service.py)). Any authenticated user can read others’ hours/descriptions. | Default list/get to `current_user.id`; allow cross-user reads only for `ADMIN` (or PM). Mirror the existing owner checks on write. |
| SEC-05 | RBAC — financial reads | High | VIEWER-reachable financial data while writes/exports need PM: revenue/executive [`reports.py:45-69`](../../../src/backend/api/reports.py); cost list/breakdown [`project_pnl.py:46-55,70-76`](../../../src/backend/api/project_pnl.py) (`get_current_user` vs PnL summary `require_role(Role.PM)` at `:30`); invoice list/get [`invoices.py:84-112`](../../../src/backend/api/invoices.py). Wave-22 claimed PnL *reads* → PM; list/breakdown still auth-only. | Align read gates with exports (`Role.PM`+) unless product explicitly wants VIEWER company-wide finance visibility. At minimum raise costs list/breakdown to match `/pnl`. |
| SEC-06 | JWT session invalidation | High | Logout only `revoke_all_for_user` on refresh rows ([`auth_service.py:84-92`](../../../src/backend/services/auth_service.py)); access JWTs remain valid until `JWT_ACCESS_TTL_MIN` (60). Refresh path does not rotate/revoke the presented refresh token ([`57-81`](../../../src/backend/services/auth_service.py)) — stolen refresh reusable for up to `JWT_REFRESH_TTL_DAYS` (30). | Rotate refresh on each use (revoke old jti/hash). Shorten access TTL and/or maintain an access denylist / version claim checked in `get_current_user`. |
| SEC-07 | IDOR — async jobs | Medium | [`src/backend/api/jobs.py:13-64`](../../../src/backend/api/jobs.py) — any `Role.PM+` can poll/download any Celery `job_id`; no owner/project binding. Result keys read via storage (`get_storage().read(result_key)`). UUIDs resist guessing but insider lateral access is unconstrained. | Store `created_by` (and project) with job metadata; authorize before status/result. Prefer signed, short-lived result URLs. |
| SEC-08 | RBAC — document writes | Medium | Document upload/update/rename/move/re-upload use `get_current_user` only ([`documents.py:52-58,128-136,149-155,216-240`](../../../src/backend/api/documents.py)). VIEWER can mutate project files; delete requires PM. | Require `Role.PM` (or designer/PM matrix) for mutating document endpoints; keep reads at VIEWER if desired. |

## Cleared / not reported (honest negatives)

| check | result |
|-------|--------|
| **SQL injection** | No dynamic string-built SQL in app paths. `reference_id_service` uses bound params (`text(...)` + `:entity_type`). Alembic `sa.text("now()")` is migration-only. **No finding.** |
| **CORS** | `allow_origins=settings.CORS_ORIGINS` with default `["http://localhost:3100"]`, credentials on ([`main.py:65-70`](../../../src/backend/main.py)). Not `*`. Misconfig risk is ops, not a code vuln. **No finding at defaults.** |
| **Mass assignment** | Public update schemas are narrow (`UserUpdate`, `DocumentUpdate`, `TimeEntryCreate` has no `user_id`; create forces session user). **No high-confidence mass-assignment bug.** |
| **Missing auth on core mutators** | Post–wave-22, sensitive mutators (exports, invoice status, task transitions, RFQ workflow, materials reads) generally use `get_current_user` / `require_role`. Unauthenticated surface is intentionally `/healthz`, `/readyz`, `/api/auth/login`, `/api/auth/refresh`, plus `/metrics` (SEC-02). |
| **Hardcoded live secrets in source** | No production API keys/tokens in Python. Insecure *defaults* exist (SEC-03); MinIO `minioadmin` is expected for local only. |
| **JWT alg confusion** | `jwt.decode(..., algorithms=[settings.JWT_ALGORITHM])` pins the allow-list. Authz uses DB `user.role`, not the JWT `role` claim ([`deps.py:27-37`](../../../src/backend/core/deps.py)). |
| **Notification IDOR** | List/mark-read scoped by `current_user.id` ([`notifications.py:24-55`](../../../src/backend/api/notifications.py)). **OK.** |

## Notes / likely false positives (excluded)

- **Content-Disposition quote injection** via document/BOQ filenames — theoretically possible; modern ASGI stacks limit classic response-splitting. Confidence &lt; 80; still sanitize filenames when fixing SEC-01/SEC-08.
- **`/readyz` error strings** — mild info disclosure; acceptable for probes.
- **OpenAPI `/docs`** — expected for internal ERP; gate only if the API is internet-facing.
- **Rate-limit XFF fallback** — only used when `request.client` is missing; low practical impact behind a normal reverse proxy.

## Suggested fix order

1. SEC-01 (storage containment) + SEC-03 (prod secret defaults)  
2. SEC-02 (metrics network/auth)  
3. SEC-04 + SEC-05 (IDOR / financial RBAC)  
4. SEC-06 (token rotation / logout semantics)  
5. SEC-07 + SEC-08  

**Reviewer:** security-focused static pass for wave-37. No code changes made outside this report file.
