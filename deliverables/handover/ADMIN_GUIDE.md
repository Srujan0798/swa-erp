# SWA ERP — Administrator Guide

For the person who keeps the live system running day to day. Everything here
documents what is already built and verified (waves 1–16 shipped); nothing is
aspirational.

---

## 1. Users and roles

The system has **five roles**. They mirror the access rules already used in the
old Excel sheets (see `resources/MEETINGS_MASTER.md` §4 for the full matrix):

| Role | What they can do |
|------|------------------|
| **Admin** | Everything — plus user management and viewing finance. |
| **PM** (Project Manager) | Create inquiries, convert to client+project, service agreements, tokens, log/own time. |
| **Designer** | Work inside projects, create document references, log own time. |
| **Auditor** | Compliance / certification (Reforge/DPR) review. Read + certify. |
| **Viewer** | Read-only navigation. |

**To create or manage a user:** an Admin creates the account (via the admin
user-management area, or the Users API) and assigns exactly one of the five
roles above. Roles are enforced server-side (RBAC), so a Viewer cannot edit
anything even if they try.

> Finance and HR data are intentionally **admin-only / dropped from MVP** per
> Meeting 1 — do not expect those sheets in this system.

---

## 2. Running the Excel → ERP import tool (safely)

The one-time migration of the existing ~20 Excel files is done with
`scripts/import_excel.py` (built in wave-13). **Always dry-run first.**

```bash
# 1. DRY RUN — no writes, just a report of what WOULD happen
make import-data file=<path.xlsx> type=<clients|inquiries|agreements|tokens|document_references|projects|time_logs|sustainability>

# 2. Only after you've read the dry-run summary and it looks right:
make import-data file=<path.xlsx> type=<...> commit=1
```

- It upserts on natural keys (client code, reference IDs), so re-running does
  not create duplicates.
- The dry-run prints a JSON summary: `{sheet_type, total_rows, created, updated,
  skipped, errors, ok}`. If `errors` is non-empty, fix the source row and re-run;
  valid rows still import.
- Full usage is in `work/reports/wave-13/01-excel-import-tooling.report.md`.
- **Before importing into a live Postgres, run migrations first**
  (`make migrate-up` / `alembic upgrade head`) or FK resolution will error.

> The migration owner (who freezes the live OneDrive sheets and runs this) is
> still an open organizational decision — see `resources/MEETINGS_MASTER.md` §7.

---

## 3. Backup and restore

> **Corrected 2026-08-07.** The dedicated backup/restore scripts shipped and are
> tested — this is no longer pending. See `docs/runbook_backup_restore.md` for the
> full how-to. In short:
>
> - **Database backup:** `make backup-db` (runs `scripts/backup_db.sh` → a
>   timestamped `.sql.gz`, pruned after 30 days). Restore: `make restore-db file=<path>`.
> - **File backup:** `make backup-files` (runs `scripts/backup_files.sh` → a tar of
>   the `uploads/` directory, pruned after 90 days).
> - **Scheduling:** add the two cron lines in `docs/runbook_backup_restore.md` §"How to
>   schedule backups" to get the intended daily DB + weekly file backup on the on-prem
>   server. Retention (30/90 days) is a default, not a confirmed client requirement —
>   adjust if the client specifies otherwise.
> - These are verified by `tests/wave-19/test_backup_scripts.py` (full
>   backup → restore round-trip) and `tests/wave-27/test_backup_script_safety.py`.

---

## 4. Checking system health

- **App health:** `GET /healthz` must return `200 {"status":"ok"}`.
  On the server: `curl -f http://localhost:8000/healthz` (or the IT-confirmed
  port — see deployment checklist).
- **Containers:** `docker compose -f docker-compose.prod.yml ps` — postgres,
  redis, backend, frontend should all show healthy/Up. The `migrate` service
  should show Exit 0.
- **Frontend:** open the internal URL and confirm the dashboard renders after
  login.

---

## 5. Troubleshooting — most likely real issues

**Login fails even with correct credentials**
- Almost always a **dual-Postgres confusion** (wave-14 report): the host's
  local Postgres and the Docker Postgres can both bind port 5432. If users were
  seeded into the wrong one, the app (pointing at the Docker DB) sees no users.
  Fix: seed/verify users inside the Docker Postgres, not the host's.

**Endpoints 500 with "column … does not exist"**
- **Migration drift** (wave-12 / wave-16 reports). A model has columns the
  migration never created. Fix: run `make migrate-up` (or `alembic upgrade head`)
  on the target DB. If a brand-new model was added without a migration, that's a
  code issue to file back to the dev team.

**`migrate` service exits non-zero on deploy**
- The schema is wrong/incomplete. Read `docker compose ... logs migrate`. Do not
  bring the stack up past this until it exits 0.

**App won't start / "SECRET_KEY not set"**
- `SECRET_KEY` is empty in `.env.production`. Generate one
  (`python3 -c "import secrets; print(secrets.token_hex(32))"`) and restart.

**TLS / "not secure" warning**
- TLS termination is at the frontend nginx layer and depends on IT_BRIEF Q4
  (cert source). Until that's set, the site serves plain HTTP — see
  `docker-compose.prod.yml` Q4 note and `docs/DEPLOYMENT_CHECKLIST.md`.

---

## Related documents
- `docs/DEPLOYMENT_CHECKLIST.md` — day-of deployment runbook
- `work/reports/wave-13/01-excel-import-tooling.report.md` — import tool details
- `resources/MEETINGS_MASTER.md` §4 — access-control matrix rationale
- `work/reports/wave-14/...` and `work/reports/wave-12/...`, `work/reports/wave-16/...`
  for the dual-Postgres and migration-drift background
