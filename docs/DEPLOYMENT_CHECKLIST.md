# SWA ERP — Deployment Checklist (Production)

Follow this top-to-bottom on deployment day. It assumes the production-shaped
config files exist (`docker-compose.prod.yml`, `.env.production.example`) and
that `docs/IT_BRIEF.md`'s 8 answers have landed (any still-open item is marked
`PENDING IT ANSWER` in those files and must be resolved first).

**Storage:** local `uploads/` directory is the default; set `STORAGE_BACKEND=minio`
and the `MINIO_*` env vars to enable MinIO. Local uploads/ works out of the box —
do not force MinIO on laptop demo.

**Platform:** Windows Server + Docker Engine (free, NOT Docker Desktop) + WSL2 + Docker Compose.
All commands run inside a WSL2 Ubuntu shell (or PowerShell with `wsl` prefix).

---

## 1. Pre-deployment

- [ ] **Confirm a fresh backup of the current system exists** (the old Excel
      files / existing DB, whichever is live today) before touching anything.
- [ ] **Create `.env.production`** from `.env.production.example` and fill in
      every value. In particular:
  - [ ] `SECRET_KEY` generated via
        `python3 -c "import secrets; print(secrets.token_hex(32))"`
  - [ ] `POSTGRES_PASSWORD` set to a strong, unique value.
  - [ ] `CORS_ORIGINS` set to the real internal hostname (Q6) — e.g. `["http://<server-LAN-IP>:3100"]`.
  - [ ] `.env.production` is gitignored (never commit it) — verified 2026-09-21.
  - [ ] Secret rotation = global logout by design: changing `SECRET_KEY`
        invalidates all access tokens at once (no per-session revocation list
        for access tokens; refresh-token families are revoked in DB).
- [ ] **No `PENDING IT ANSWER` comments remain unresolved** in
      `docker-compose.prod.yml` or `.env.production`. Each maps to a numbered
      question in `docs/IT_BRIEF.md`:
  - [ ] Q1 Docker Engine (free) vs Docker Desktop — confirm free Engine is used
  - [ ] Q2 WSL2 / Linux containers enabled on Windows Server
  - [ ] Q3 free ports substituted (UI 3100, API 8100; DB/Redis internal only)
  - [ ] Q4 TLS termination decided (cert source — self-signed or internal CA for VPN)
  - [ ] Q6 internal web address locked (e.g. `http://<server-LAN-IP>:3100`)
  - [ ] Q7 postgres/redis in-compose vs native Windows — confirm in-compose
- [ ] **Confirm target server has Docker Engine (free) running** and WSL2 enabled
      for Linux containers (`wsl -l -v` shows Ubuntu).
- [ ] **Pull / transfer the built images** (or confirm the host can build from
      the repo — `Dockerfile`, `Dockerfile.frontend` are unchanged from dev).

---

## 2. Deployment steps

Run from a WSL2 Ubuntu shell (or PowerShell with `wsl` prefix):

```bash
# From the repo root on the target server.

# 1. Bring up the stack (builds images, starts postgres/redis/backend/frontend,
#    runs migrate automatically).
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# 2. Confirm the migrate service exited 0 (it must, or the DB schema is wrong).
docker compose -f docker-compose.prod.yml ps        # migrate should show Exit 0
docker compose -f docker-compose.prod.yml logs migrate

# 3. Verify health (host port 8100 maps to container port 8000).
curl -f http://localhost:8100/healthz                # expect {"status":"ok"}
docker compose -f docker-compose.prod.yml ps         # all long-running svc = healthy/Up
```

If `migrate` failed, **stop and debug before continuing** — a partial schema
will break every endpoint. Re-run migrate with
`docker compose -f docker-compose.prod.yml run --rm migrate` after fixing.

---

## 3. Post-deployment smoke test

Log in as **each role once** (admin, pm, designer, auditor, viewer) and confirm
the core chain works. Reuse the verified live-API smoke list from
`work/reports/wave-12/01-independent-verification.report.md` (these endpoints are
known-good end to end):

| # | Endpoint | Expect |
|---|----------|--------|
| 1 | `GET /healthz` | 200 `{"status":"ok"}` |
| 2 | `POST /api/auth/login` | 200, JWT issued |
| 3 | `GET /api/auth/me` | 200 |
| 4 | `GET /api/clients` | 200 |
| 5 | `POST /api/clients` | 201 |
| 6 | `POST /api/inquiries` | 201, `reference_id=SWA-YYYY-INQ-001` |
| 7 | `POST /api/inquiries/{id}/convert` | 200, client+project created |
| 8 | `GET /api/projects` | 200 |
| 9 | `POST /api/service-agreements` | 201, `reference_id=SWA-YYYY-SA-001` |
| 10 | `POST /api/tokens` | 201, `reference_id=SWA-YYYY-TKN-001` |
| 11 | `POST /api/document-references` | 201, `reference_id=SWA-YYYY-DRAWING-001` |
| 12 | `GET /api/projects/{id}/sustainability/metrics` | 200 |
| 13 | `POST /api/projects/{id}/sustainability/metrics` | 201 |
| 14 | `POST /api/projects/{id}/tasks` | 201 |
| 15 | `GET /api/projects/{id}/tasks` | 200 |
| 16 | `GET /api/projects/{id}/documents` | 200 |
| 17 | `GET /api/reports/project-health` | 200 |
| 18 | `GET /api/dashboard/executive` | 200 |

Frontend: open the internal URL (Q6, e.g. `http://<server-LAN-IP>:3100`) in a browser, log in as admin, confirm the
dashboard renders and the inquiry→client→project→agreement→token→document chain
is clickable end to end.

---

## 4. Rollback procedure

The stack is image-tagged; to revert to the previous known-good version (run from WSL2):

```bash
# 1. Stop the current stack (keeps the prod volumes — DB data is preserved).
docker compose -f docker-compose.prod.yml down

# 2. Checkout / pull the previous release tag or commit.
git checkout <previous-release-tag>

# 3. Redeploy from the previous images.
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

## 5. Backup & restore (Meeting 2 cadence)

- [ ] **Daily database backup** configured and tested (Windows Task Scheduler on prod host).
      Suggested task: Action → `wsl.exe -d Ubuntu -- bash -c "cd /mnt/c/path/to/swa-erp && make backup-db"`
      Trigger: Daily at 02:00.
- [ ] **Weekly file backup** configured (Windows Task Scheduler on prod host):
      Suggested task: Action → `wsl.exe -d Ubuntu -- bash -c "cd /mnt/c/path/to/swa-erp && make backup-files"`
      Trigger: Weekly on Sunday at 03:00.
- [ ] **Restore dry-run verified** before go-live:
  - `make restore-db file=<path.sql.gz>` — prints commands, exits 0 (no changes)
  - `make restore-files file=<path.tar.gz>` — prints command, exits 0 (no changes)
- [x] **Actual restore tested** in a staging environment at least once:
  - `make restore-db file=<path.sql.gz> FORCE=--force` (destructive — needs confirmation)
  - `make restore-files file=<path.tar.gz> FORCE=--force` (overwrites uploads/)
  - **Proof 2026-09-21:** `swa_erp_backup_20260919_021036.sql.gz` restored into
    scratch DB `swa_restore_proof` via the script's exact pipeline
    (`gunzip -c … | psql --set ON_ERROR_STOP=on --single-transaction`):
    39 tables, 8 users, 2 projects, 5 clients, `alembic_version` present.
    Scratch DB dropped afterwards. RPO ≈ 24h (daily), restore time < 1 min
    for current data size.
- [ ] **Retention policies active**:
  - DB backups: 30-day retention (handled by `backup_db.sh`)
  - File backups: 90-day retention (handled by `backup_files.sh`)

Restoration safety:
- Dry-run mode is the default — the target scripts print commands without executing them.
- Actual restore requires the `--force` flag AND an interactive "yes" confirmation.
- `restore-db` drops the public schema before restore (destructive).
