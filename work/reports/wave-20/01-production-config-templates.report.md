# Report — wave-20 / 01 — Production config templates

## Result
**DONE**

## What I did
- Created `docker-compose.prod.yml` (88 lines) — production-shaped compose, separate from dev.
- Created `.env.production.example` (45 lines) — mirrors `.env.example` variable names.
- Created `docs/DEPLOYMENT_CHECKLIST.md` (107 lines) — day-of deployment runbook.

## Acceptance checks
- [x] `docker-compose -f docker-compose.prod.yml config` validates without error — `exit=0`, zero stderr (removed the obsolete `version` key so there are no warnings either).
- [x] Every `PENDING IT ANSWER` comment references a specific numbered question from `docs/IT_BRIEF.md` — present: Q1, Q2, Q3, Q4, Q6, Q7 (Q5 backups and Q8 update-process are process questions, covered in the checklist's pre-deploy/rollback sections rather than as config placeholders).
- [x] `docs/DEPLOYMENT_CHECKLIST.md` is concrete enough to follow without extra context — ordered sections: pre-deployment, deploy, post-deploy smoke (reuses wave-12's verified live-API list), rollback.
- [x] Dev `docker-compose.yml` / `.env.example` are byte-for-byte unchanged — `git status` shows no modifications to them (or to `Dockerfile` / `Dockerfile.frontend`).
- [x] No app code touched, so `pytest` is unaffected by design.

## Decisions I made
- Kept the same service shape (postgres, redis, migrate, backend, frontend) and variable names as dev, swapping in: named prod volumes (`swa_erp_prod_pgdata`, `swa_erp_prod_redisdata`), `restart: unless-stopped` on long-running services, removed `adminer` (DB admin UI must not be exposed in prod), and a backend `/healthz` healthcheck.
- `SECRET_KEY` defaults to `REPLACE_ME_IN_ENV_FILE` and `POSTGRES_PASSWORD` to a clear placeholder so `config` validates today, with comments that both MUST be set via `.env.production`.
- TLS (Q4) handled at the nginx/frontend layer only — no app code change needed; documented the exact nginx.conf edit once the cert source is known. Did not add a separate reverse-proxy service (out of scope until Q4 answered).
- Used `env_file: .env.production` invocation in the checklist (`--env-file .env.production`) so the template validates even without the file present.

## Tests run
- `docker-compose -f docker-compose.prod.yml config` → exit 0 (valid, no warnings)
- `git status --short docker-compose.yml .env.example Dockerfile Dockerfile.frontend` → empty (dev configs untouched)

## Issues / blockers
None. All uncertain values are explicit placeholders per the task's "never guess" constraint.

## Recommended next task
Wave-21 (handover documentation) — depends only on already-built/verified material, not on IT answers.

## Time / tokens / model
~35 min / minimal tokens / opus.
