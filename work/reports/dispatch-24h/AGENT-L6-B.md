# AGENT-L6-B

Repo: `/Users/srujansai/Desktop/swa-erp` (main). JWT logout / token_version vs version column. Refresh rotation. Fix or NOT MEASURED.

## Verification (source-level, Python 3.11.5)

### 1. JWT logout invalidates existing access tokens

**Verified WORKING:**
- `v` claim embedded at sign: `src/backend/core/security.py:24-44` (both mint sites pass `token_version`)
- Enforced at read: `src/backend/core/deps.py:36-39` (get_current_user compares `payload.v` vs `user.token_version`)
- Bumped on logout: `src/backend/services/auth_service.py:105` (`user.token_version += 1; db.commit()`)
- Every route decodes via `get_current_user` — no unenforced path

**Result:** Logout invalidates all outstanding access tokens for that user. ✅

### 2. users.token_version vs version column

**Verified:**
- Model: `src/backend/models/user.py:26` — `token_version: Mapped[int]` (renamed from `version` in migration 0036)
- Dev DB: uses `token_version` column, no `version` column
- Migration 0036 applied cleanly (idempotent: renames `version`→`token_version` or adds if missing)
- **No migration created** — column already correct.

**Flag:** Dev DB is at revision 0037 but no 0037 file exists in the repo (pre-existing, NOT MEASURED).

### 3. Refresh rotation

**Verified WORKING:**
- Single-use: old token revoked via `revoke_single` (auth_service.py:84)
- Type-checked, DB-hash-validated, all tokens revoked on logout (auth_service.py:108)
- `find_valid` uses `with_for_update()` row lock (added in L6-FIX) — prevents race

**Result:** Refresh rotation works correctly. ✅

### 4. Added tests

Added 2 tests to `tests/wave-1/test_auth.py` (not run per instructions):
- `test_logout_invalidates_access_token_via_token_version`
- `test_refresh_rotation_revokes_old_token`

Ruff/black/py_compile/mypy all clean; only that test file modified, left unstaged.

---

## Summary

| Check | Status |
|-------|--------|
| Logout invalidation via token_version | ✅ VERIFIED WORKING |
| token_version column vs version | ✅ VERIFIED (no migration needed) |
| Refresh rotation (single-use, revoke on logout) | ✅ VERIFIED WORKING |
| Reuse race (row lock) | ✅ FIXED (with_for_update) |
| Tests added | ✅ (unstaged, wave-1) |

**No fix needed.** All JWT/refresh mechanics verified working.