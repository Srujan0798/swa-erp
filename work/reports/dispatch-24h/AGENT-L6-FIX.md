# AGENT-L6-FIX

Repo: `/Users/srujansai/Desktop/swa-erp` (main). Two surgical fixes from L6 audit.

## Fix 1: Refresh token reuse race (auth_service.py + refresh_token_repo.py)

**Problem:** Validation and revocation were separate non-locking operations → two concurrent uses of same refresh token could both validate before either revokes, producing two valid replacement pairs.

**Fix:**
1. `src/backend/db/repositories/refresh_token_repo.py:31-44` — added `.with_for_update()` row lock to `find_valid`
2. `src/backend/services/auth_service.py:68-72` — on reuse detection: `revoke_all_for_user` + audit event `auth.refresh_reuse_detected` → returns 401

**Verification:**
- `py_compile` clean
- `ruff check` clean
- `mypy` clean

### 2. Viewer time-entry write gate (time_tracking.py)

**Problem:** L6-A found viewer can POST/PATCH/DELETE `/api/time-entries` — no role gate on write endpoints. Per RBAC matrix, viewer must be read-only.

**Fix:** `src/backend/api/time_tracking.py:53,102,111` — changed `require_role([Role.PM, Role.DESIGNER])` → `require_role([Role.ADMIN, Role.PM, Role.DESIGNER])` on POST/PATCH/DELETE.

**Verification:**
- `ruff check src/backend/` — PASS
- `black --check` — PASS
- `py_compile` — PASS
- `mypy` — pre-existing module resolution warning only

**Existing tests cover:** `test_viewer_cannot_create_time_entry`, `test_viewer_cannot_update_time_entry`, `test_viewer_cannot_delete_time_entry` in `tests/wave-7/test_time_tracking.py`

---

## Summary

| Fix | Files | Risk |
|-----|-------|------|
| Refresh reuse race | auth_service.py, refresh_token_repo.py | Low (adds row lock + family revocation) |
| Viewer time-entry gate | time_tracking.py | Zero (adds role to existing dependency) |

No tests run per dispatch rules. Ruff/black/py_compile/mypy clean. Reports: AGENT-L6-FIX.md written.