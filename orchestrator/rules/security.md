# Security rules

**Corrected 2026-07-21** — a full-project audit found this file described several mechanisms as
already-implemented fact when they weren't, which could cause a future security review to check
the wrong thing entirely. Corrected below to state actual current implementation, with the
original intent kept as a target where it's genuinely still a good goal.

- Secrets via env only. `.env` is gitignored. `.env.example` lists keys without values.
  `SECRET_KEY` currently defaults to `"change-me"` with no production fail-safe — see
  `work/wave-18/01-security-hardening.md` item 1, this is the actual current gap.
- Passwords: bcrypt cost 12. Never plaintext. Never reversible. (Real, verified.)
- **JWT: HS256 only, in both dev and prod — RS256 was never implemented despite being claimed
  here previously.** 1h access, 30d refresh. **Refresh does NOT rotate** — `refresh_access_token()`
  (`src/backend/services/auth_service.py`) issues a new access token but the same refresh token
  stays valid indefinitely until its TTL expires; no rotation, no revocation of the old one.
- RBAC server-side. Frontend may hide UI but server is source of truth. **As of 2026-07-21 this
  is aspirational, not fully true** — a full audit found multiple endpoints with no role check
  at all (e.g. `materials.py` reads had NO auth check whatsoever, not even login) and several
  RBAC mismatches between the client's stated access matrix and actual role gates. See
  `work/wave-22/01-critical-rbac-and-auth-gaps.md` for the fix list — verify against
  `work/reports/wave-22/` before trusting that this rule actually holds.
- SQL: parameterized only. No string concatenation, no f-strings into SQL. (SQLAlchemy ORM used
  throughout; no raw SQL string-building found in the audit.)
- CORS: explicit allowlist (frontend origin). No `*`. (Real — reads `CORS_ORIGINS` from env.)
- File uploads: size cap (50MB), type check (mime + extension), filename sanitize. (Not
  independently re-verified in the 2026-07-21 audit — check before relying on this claim.)
- Audit log: every mutation logged with user, IP, before/after. (Real, verified across many
  wave reports — `audit_log` table, consistently used.)
- **No cookies are used at all, HTTPS-only or otherwise.** Auth is Bearer-token based; the
  frontend stores both access AND refresh tokens in `localStorage`
  (`src/frontend/src/lib/auth.ts`) — a materially more XSS-exposed threat model than the
  cookie-based one this rule previously described as already in place. If cookie-based storage
  is ever actually desired, it needs to be built, not just documented as if it already exists.
- Error responses: never expose stack traces in production. (Not independently re-verified —
  check `APP_ENV`/`DEBUG` handling before relying on this claim.)
- **Dependencies: `pip-audit` and `npm audit` run in CI but do NOT block on anything.**
  `.github/workflows/security.yml:17` has `pip-audit -r requirements.txt --strict || true` and
  `:29` has `npm audit --audit-level=high || true` — both `|| true` patterns mean the job
  always exits 0 regardless of findings, directly contradicting "block on high/critical." This
  needs a real fix (remove the `|| true`, or explicitly triage and pin acceptable-risk
  exceptions) before this rule's stated intent is actually true.
