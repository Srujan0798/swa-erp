# Security rules

- Secrets via env only. `.env` is gitignored. `.env.example` lists keys without values.
- Passwords: bcrypt cost 12. Never plaintext. Never reversible.
- JWT: HS256 in dev, RS256 in prod. 1h access, 30d refresh. Refresh rotates.
- RBAC server-side. Frontend may hide UI but server is source of truth.
- SQL: parameterized only. No string concatenation, no f-strings into SQL.
- CORS: explicit allowlist (frontend origin). No `*`.
- File uploads: size cap (50MB), type check (mime + extension), filename sanitize.
- Audit log: every mutation logged with user, IP, before/after.
- HTTPS-only cookies in prod with `Secure`, `HttpOnly`, `SameSite=Lax`.
- Error responses: never expose stack traces in production.
- Dependencies: `pip-audit` and `npm audit` in CI; block on high/critical.
