# Security Perimeter Guide

> **For:** the on-site operator / reviewer with **no security background**. This explains what the
> system protects, how it does it, and the specific hardening we did in **Wave-37** (real fixes,
> not aspirations). It also lists the **known gaps** we have *not* closed yet, honestly.

---

## 1. The trust boundary in one picture

```
Browser (user's machine)
   │  sends a token with every request
   ▼
Frontend (localhost:3100)  ── just displays data, no secrets here
   │  calls the API
   ▼
Backend (localhost:8100)  ←  THE PERIMETER
   │  • checks the token (JWT)
   │  • checks the user's role (RBAC)
   │  • reads/writes the database (PostgreSQL)
   │  • stores uploaded files under uploads/ (or MinIO)
   ▼
PostgreSQL · Redis · (MinIO)  ←  behind the perimeter, not public
```

**Rule of thumb:** if a request reaches the backend without a valid token, or with a role that
isn't allowed, it is rejected. The backend is the only thing that touches the database.

---

## 2. Authentication — how users prove who they are

**Mechanism:** **JWT (JSON Web Token), algorithm HS256 (symmetric HMAC).**

- When a user logs in, the backend signs a token with the server's **`SECRET_KEY`** and returns it.
- The browser stores that token in **`localStorage`** (the browser's local scratch space) and sends
  it on every request in the `Authorization` header.
- The token is **stateless** — the server doesn't keep a session table; it just verifies the
  signature. That's why rotating `SECRET_KEY` (see Incident Playbook §4) logs everyone out at once.
- Two tokens: a short-lived **access token** (`JWT_ACCESS_TTL_MIN = 60` minutes) and a longer-lived
  **refresh token** (`JWT_REFRESH_TTL_DAYS = 30` days).

> Source of truth: `src/backend/core/config.py:24-25`, `src/backend/core/security.py:26-55`.

---

## 3. Authorization — what each role can do (RBAC)

Roles are checked on the server for every protected action. The roles, in `src/backend/core/roles.py`:

| Role | Can do |
|---|---|
| **admin** | Everything, including settings and user management |
| **pm** (project manager) | Projects, clients, finance reads/exports, time approval |
| **designer** | Project execution: tasks, time entries, documents |
| **viewer** | Read-only dashboards, lists, details |

**Key point:** authorization is enforced by the **database role**, not by trusting the token's
`role` claim. The JWT algorithm allow-list is pinned (`algorithms=[HS256]`), so an attacker cannot
trick the server with a different signing algorithm (the classic "alg confusion" attack).
> Source: `src/backend/core/security.py:55` (pinned algorithm); `src/backend/core/deps.py`
> (role read from DB, not token).

---

## 4. What Wave-37 actually fixed (real, shipped hardening)

These are **not** plans — they are in the code (commit `82bf291`, "wave-37 critical hardening").

### 4.1 Path traversal in file storage (Critical — fixed)
**Before:** an upload filename like `../../evil` could be used to read or write files *outside* the
upload directory.
**After:** `LocalStorage` now resolves every key and refuses anything that escapes the upload root:
- Absolute paths are rejected outright (`save()` raises `ValueError`).
- Relative keys are joined under root, then **asserted to still be under root** via
  `candidate.relative_to(root)`; a `..` escape raises `ValueError("storage key escapes upload root")`.
- Uploaded filenames are reduced to their basename (`Path(name).name`) so a malicious name can't
  carry directory parts.
> Source: `src/backend/core/storage.py:42-82` (`_ensure_under_root`, `_path`, `save`).

### 4.2 Insecure secret-key denylist (Critical — fixed)
**Before:** the production validator only blocked a tiny set of weak secrets, so a placeholder like
`REPLACE_ME_IN_ENV_FILE` would start the app in **production** mode with a known, attackable key.
**After:** `INSECURE_SECRET_KEYS` now includes the real placeholders seen in deploy templates
(`REPLACE_ME_IN_ENV_FILE`, `dev-secret-change-me`) plus the old ones. In any `APP_ENV` other than
`dev`, using one of these **refuses to start** the app.
> Source: `src/backend/core/config.py:4-11`, `:38-46` (`_validate_production_secrets`).

### 4.3 Hourly-rate setting is explicit, not invented math (fixed)
**Before:** billing/P&L estimates could silently bake in a hardcoded rate.
**After:** the company default billing rate is a single configurable setting
`DEFAULT_HOURLY_RATE_INR` (default `"5000.00"`), overridable per invoice. No magic numbers in the
finance code.
> Source: `src/backend/core/config.py:37-40`; used in `project_pnl_service.py`, `invoice_service.py`.

### 4.4 Metrics endpoint must not be public (High — guidance)
`/metrics` (Prometheus) is **excluded from auth** by design and must **never** be exposed on a
public port. Bind it to localhost or the scrape network only. The dev compose maps it inside the
Docker network; do not publish port 8000 to the internet.
> Source: `src/backend/core/metrics.py:99-105` (excludes `/metrics` from instrumentation but does
> not add auth — that is the operator's job at the network level).

---

## 5. Known gaps we have NOT closed (honest list)

From the same Wave-37 review (`work/reports/wave-37/_findings-security.md`):

1. **JWT refresh tokens are not rotated on use.** A stolen refresh token is reusable for up to 30
   days; logout only revokes the *refresh row*, not the presented token. *Mitigation today:* rotate
   `SECRET_KEY` to invalidate all tokens (Incident Playbook §4).
2. **IDOR in time tracking.** Any logged-in user could *read* others' time entries/hours. Write
   paths are owner-checked; reads were not, at review time.
3. **Financial RBAC inconsistency.** Some cost/P&L *read* endpoints were auth-only (any logged-in
   user) rather than `PM+`, unlike the export endpoints.
4. **Document writes** used `get_current_user` only, so a `viewer` could mutate project files;
   delete already required `PM`.
5. **Async job results** (Celery) are pollable by any `PM+` via job id with no owner binding.

These are recorded honestly so the next wave can close them. They do **not** affect the four fixes
in §4, which are complete.

---

## 6. Operator checklist (what you control)

- [ ] **Never** ship `SECRET_KEY` as `dev-secret-change-me` / `REPLACE_ME_IN_ENV_FILE` to the
      client's server — the app will refuse to start (good), so generate a real one:
      `openssl rand -hex 32`.
- [ ] **Never** expose port 8000 (the API/metrics) to the public internet; keep it on the VPN /
      internal network.
- [ ] Uploaded files live under `uploads/` — treat that directory as sensitive data, back it up
      (see Incident Playbook §5).
- [ ] Tokens live in the user's browser `localStorage` — that's normal for this app, but it means
      a shared/public computer should be logged out after use.
