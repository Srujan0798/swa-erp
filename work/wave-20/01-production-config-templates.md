# Task 01 — Production config templates (ready for instant swap once IT answers land)

## What to do
Build the production-shaped config files now, with every IT-dependent value clearly marked as a
placeholder — so the moment `docs/IT_BRIEF.md`'s 8 answers come back, updating these is a find-
and-replace, not a from-scratch build. This is explicitly about *not* blocking on IT's answers,
per `docs/decisions/0003-it-server-call-brief.md`'s own framing.

## Files to create
- CREATE: `docker-compose.prod.yml` — production-shaped compose file, separate from the existing
  dev `docker-compose.yml` (don't modify the dev one)
- CREATE: `.env.production.example` — mirrors `.env.example` but with prod-appropriate defaults
  and explicit `# PENDING IT ANSWER:` comments on anything still unknown
- CREATE: `docs/DEPLOYMENT_CHECKLIST.md` — the actual step-by-step "day of deployment" runbook

## Files you must NOT touch
- `docker-compose.yml`, `Dockerfile`, `Dockerfile.frontend`, `.env.example` — the existing dev
  configs are working and verified (wave-14), don't risk them; this task only adds new,
  separate prod-targeted files
- Any Alembic migration

## The core problem (inline)

### `docker-compose.prod.yml`
Base it on the current (working, wave-14-fixed) `docker-compose.yml` — same service shape
(postgres, redis, migrate, backend, frontend), but with these prod-appropriate changes, each
one marked inline with a comment explaining what's still pending:
```yaml
# PENDING IT ANSWER (docs/IT_BRIEF.md Q1): confirm Docker Engine vs Docker Desktop availability
# PENDING IT ANSWER (Q2): confirm Linux containers via WSL2 are available on the target server
# PENDING IT ANSWER (Q3): replace these port mappings with IT-confirmed free ports
# PENDING IT ANSWER (Q4): TLS termination - self-signed placeholder below, replace once confirmed
# PENDING IT ANSWER (Q6): replace localhost/placeholder hostname with the real internal address
# PENDING IT ANSWER (Q7): confirm whether postgres/redis stay in this compose file or move to
#                          native Windows services - if native, remove those two services here
```
Concretely:
- Use named volumes with clear prod-appropriate naming (`swa_erp_prod_pgdata`, etc.), not the
  dev volume names
- Set `restart: unless-stopped` on long-running services (postgres, redis, backend, frontend) —
  dev compose likely doesn't have this, prod should
- Remove any dev-only conveniences (e.g. adminer, if it's in the dev compose — check first;
  don't expose a DB admin UI in a prod compose file by default)
- Reference `.env.production.example`'s variable names consistently

### `.env.production.example`
Mirror `.env.example`'s structure exactly (same variable names, so nothing needs renaming in
app code), but:
- `APP_ENV=production`
- `DEBUG=false`
- `SECRET_KEY=` left blank with a comment: `# REQUIRED - generate via: python3 -c "import secrets; print(secrets.token_hex(32))" - app will refuse to start without this if wave-18's SECRET_KEY validation has landed`
- `CORS_ORIGINS=` with `# PENDING IT ANSWER (Q6): the real internal hostname staff will use`
- Any TLS-related variable with `# PENDING IT ANSWER (Q4)`

### `docs/DEPLOYMENT_CHECKLIST.md`
A literal ordered checklist someone follows top to bottom on deployment day. Sections:
1. Pre-deployment (confirm backups exist, confirm `.env.production` is filled in completely,
   confirm no `PENDING IT ANSWER` comments remain unresolved)
2. Deployment steps (`docker-compose -f docker-compose.prod.yml up -d --build`, verify migrate
   service exits 0, verify healthz)
3. Post-deployment smoke test (login as each role once, hit a handful of core endpoints — reuse
   the smoke-test list from `work/reports/wave-12/01-independent-verification.report.md`'s "Live
   API smoke" section as a starting point)
4. Rollback procedure (how to revert to the previous image/tag if something's wrong)

## Acceptance criteria
- [ ] `docker-compose -f docker-compose.prod.yml config` — validates without error (syntax-valid
  compose file, even though some placeholder values won't work until IT answers land)
- [ ] Every `PENDING IT ANSWER` comment references the specific numbered question from
  `docs/IT_BRIEF.md` it depends on
- [ ] `docs/DEPLOYMENT_CHECKLIST.md` is concrete enough to follow without additional context
- [ ] The existing dev `docker-compose.yml` / `.env.example` are byte-for-byte unchanged
- [ ] `python3 -m pytest tests/ -q` — unaffected (this task shouldn't touch app code at all)

## How to deliver
1. Build all three files
2. Validate the compose file syntax
3. Write report to `work/reports/wave-20/01-production-config-templates.report.md`
4. Stop

## Constraints
- Time budget: 75 min
- Do not guess at IT's answers — every uncertain value gets a clear placeholder + comment, never
  a silent assumption
- Allowed tools: file edit, docker-compose, docker
