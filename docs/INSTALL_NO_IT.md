# Install on company server — no IT department

**When to use:** Viraj (or whoever handles the Windows Server / VPN) has ~1–2 hours
and wants the ERP up. There is no separate IT team.

**When not to use:** You still don't have machine access — then keep waiting; nothing to force.

Safe defaults used here (change only if Viraj prefers otherwise):

| Choice | Default |
|--------|---------|
| Containers | Docker Engine (free) + WSL2 on Windows Server |
| Stack | All in Docker Compose (Postgres, Redis, backend, frontend, worker) |
| Storage | Local `uploads/` first; MinIO optional later |
| HTTPS | Self-signed **or** plain HTTP **only on VPN** for first week (document risk) |
| Hostname | Whatever he gives (IP is fine for v1) |
| Backups | Our `make backup-db` / `backup-files` until company backup exists |

---

## 0. Prerequisites (on the server)

1. Windows Server with VPN access for staff (already the plan).
2. Install **Docker Engine** (free) + enable **WSL2** / Linux containers if needed.
3. Git (or copy the repo zip) + enough disk for images + DB + uploads (~20 GB free is comfortable).
4. Open/free ports (defaults): `3000` (UI), `8000` (API). DB/Redis stay internal to compose unless he wants them exposed.

---

## 1. Get the code on the machine

```bash
git clone <repo-url> swa-erp
cd swa-erp
git checkout v1.0.1   # or main at the release you agreed
```

Or copy a release folder he already has.

---

## 2. Create production env

```bash
cp .env.production.example .env.production
```

Edit `.env.production` at minimum:

```bash
# Generate secrets
python3 -c "import secrets; print(secrets.token_hex(32))"   # → SECRET_KEY
# set POSTGRES_PASSWORD to something strong and unique

SECRET_KEY=...paste...
POSTGRES_PASSWORD=...strong...
# Staff browser origin — use real host/IP when known:
CORS_ORIGINS=http://SERVER_IP:3000
# or http://erp.swa.local:3000
```

If hostname is still unknown, use the server LAN IP for the first install and update
`CORS_ORIGINS` when a proper name exists.

Strip or ignore remaining `PENDING IT ANSWER` comments once you've filled real values
for secrets + CORS + ports you actually use.

---

## 3. Start the stack

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs migrate   # must Exit 0
curl -f http://localhost:8000/healthz                    # {"status":"ok"}
```

Open in a browser (on VPN): `http://SERVER_IP:3000` (or the host you set).

---

## 4. Smoke test (15 minutes)

1. Login as admin (seeded/default from deploy docs — rotate password immediately).
2. Create Inquiry → convert → Service Agreement → Token → Document Reference.
3. Confirm IDs look like `SWA-2026-INQ-001`, `SWA-2026-SA-001`, etc.
4. Login once as a non-admin role if accounts exist.

Full API table: `docs/DEPLOYMENT_CHECKLIST.md` §3.

---

## 5. Backups (same day)

```bash
make backup-db
make backup-files
```

Schedule daily (Task Scheduler / cron) until a company-wide backup exists.

---

## 6. Excel migration (separate sitting)

Only after the app is up and Viraj names who owns the data:

```bash
# Always dry-run first
python3 scripts/import_excel.py clients path/to/Clients.xlsx
# ... review report ...
python3 scripts/import_excel.py clients path/to/Clients.xlsx --commit
```

Supported types: see `deliverables/SUBMISSION.md` §7.

---

## 7. Updates later

```bash
cd swa-erp
git pull   # or drop new release
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

Never `down -v` in production (wipes volumes).

---

## If something fails

| Symptom | Check |
|---------|--------|
| migrate non-zero | `logs migrate`; fix DB URL/password; re-run migrate |
| UI loads, API fails | CORS_ORIGINS must match the browser URL exactly |
| Can't pull images | Network / Docker Hub from that server |
| Port in use | Change host ports in compose; update CORS if UI port changes |

Longer checklist: `docs/DEPLOYMENT_CHECKLIST.md`. Ops day-to-day: `docs/runbook.md`.
