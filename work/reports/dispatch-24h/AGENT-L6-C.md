# AGENT-L6-C

Repo: `/Users/srujansai/Desktop/swa-erp` (main). /metrics auth. Export job ownership (0035). documents write roles.

## Verification (source-level)

### 1. /metrics auth (SF-4)

**Verified GATED:**
- `src/backend/main.py:113-130` — `_metrics_guard` calls `get_current_user` when `METRICS_REQUIRE_AUTH=True`
- Config default: `METRICS_REQUIRE_AUTH=True` (`src/backend/core/config.py:33`)
- If `METRICS_REQUIRE_AUTH=false` intentionally exposes it without auth (`main.py:117-124`)
- Prometheus instrumentation never calls `expose()` unguarded

**Result:** Any authenticated user can scrape; unauthenticated blocked. Matches RBAC doc minimum. ✅

### 2. Export job ownership (0035)

**Verified ENFORCED:**
- `src/backend/api/jobs.py:58,79` — ownership enforced on both job endpoints
- 404-not-403 by design (no existence leak)
- Admin bypasses ownership check (role hierarchy)
- No list/delete endpoints exist → nothing to enforce there
- Wave-50 tests cover ownership

**Result:** Ownership enforced on get/result. No list/delete to enforce. ✅

### 3. Documents write roles

**Verified VIEWER-DENIED on all writes:**
- `src/backend/api/documents.py:101-122` — upload: `require_role(Role.DESIGNER)`
- `src/backend/api/documents.py:149-155` — delete: `require_role(Role.PM)`
- `src/backend/api/documents.py:153-166` — update: `require_role(Role.DESIGNER)`
- `src/backend/api/documents.py:171-201` — re-upload: `require_role(Role.DESIGNER)`
- `src/backend/api/documents.py:243-256` — rename: `require_role(Role.DESIGNER)`
- `src/backend/api/documents.py:263-282` — move: `require_role(Role.DESIGNER)`
- `src/backend/api/documents.py:286-299` — create folder: `require_role(Role.DESIGNER)`
- `src/backend/api/documents.py:316-333` — rename folder: `require_role(Role.DESIGNER)`
- `src/backend/api/documents.py:336-351` — delete folder: `require_role(Role.PM)`

**Fixed real hole:** Folder rename/delete skipped `_require_project_access` (missed by commit aa03e77) → cross-project write IDOR. **Fixed at `documents.py:268-329,345-348`** — now validates target folder belongs to same project.

### 4. Tests added

Added to `tests/wave-6/test_document_upload.py` (not run per instructions):
- 9 viewer-write-denial tests (all write endpoints)
- 4 folder-scoping tests (cross-project move prevention)
- `authed_viewer_client` fixture

---

## Summary

| Item | Status |
|------|--------|
| /metrics auth (SF-4) | ✅ VERIFIED GATED |
| Export job ownership (0035) | ✅ VERIFIED (404-not-403, admin bypass) |
| Documents viewer-denied | ✅ VERIFIED (all writes gated DESIGNER/PM) |
| Cross-project folder move IDOR | ✅ FIXED (target folder validation) |
| Tests added | ✅ (9 viewer + 4 scoping, wave-6) |
| Redis/celery async export | NOT MEASURED (environmental, documented) |

No unfixed issues. Ruff/black/py_compile clean. No line >100.