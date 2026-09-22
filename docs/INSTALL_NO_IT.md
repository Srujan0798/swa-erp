# Install on company server — no IT department

**When to use:** Viraj (or whoever handles the Windows Server / VPN) has ~1–2 hours
and wants the ERP up. There is no separate IT team.

**When not to use:** You still don't have machine access — then keep waiting; nothing to force.

Safe defaults used here (change only if Viraj prefers otherwise):

| Choice | Default |
|--------|---------|
| Containers | Docker Engine (free) + WSL2 on Windows Server (NOT Docker Desktop) |
| Stack | All in Docker Compose (Postgres, Redis, backend, frontend, worker) |
| Storage | Local `uploads/` directory default; set `STORAGE_BACKEND=minio` + `MINIO_*` env vars to enable MinIO |
| HTTPS | Self-signed **or** plain HTTP **only on VPN** for first week (document risk) |
| Hostname | Whatever he gives (IP is fine for v1) |
| Backups | Our `make backup-db` / `backup-files` until company backup exists |

---

## 0. Prerequisites (on the server)

1. Windows Server with VPN access for staff (already the plan).
2. Install **Docker Engine (free)** — NOT Docker Desktop. Enable **WSL2** / Linux containers:
   - `wsl --install` (if not already enabled)
   - In Docker Engine settings: *Use the WSL 2 based engine* (checked by default on Windows Server 2022+)
3. Git (or copy the repo zip) + enough disk for images + DB + uploads (~20 GB free is comfortable).
4. Open/free ports (defaults): `3100` (UI), `8100` (API). DB/Redis stay internal to compose unless he wants them exposed.

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
# Generate secrets (run inside WSL2 Ubuntu or PowerShell with python)
python3 -c "import secrets; print(secrets.token_hex(32))"   # → SECRET_KEY
# set POSTGRES_PASSWORD to something strong and unique

SECRET_KEY=...paste...
POSTGRES_PASSWORD=...strong...
# Staff browser origin — use real host/IP when known:
CORS_ORIGINS=http://SERVER_IP:3100
# or http://erp.swa.local:3100
```

If hostname is still unknown, use the server LAN IP for the first install and update
`CORS_ORIGINS` when a proper name exists.

Strip or ignore remaining `PENDING IT ANSWER` comments once you've filled real values
for secrets + CORS + ports you actually use.

**Secrets handling (Windows Server + Docker Engine):** Keep secrets in `.env.production`
(never commit). For production hardening later, migrate to Docker secrets:
```bash
# Example: store secret in Docker secret, then reference in compose
printf "real-secret-key" | docker secret create swa_secret_key -
# In compose: SECRET_KEY_FILE=/run/secrets/swa_secret_key
```
But for first install, `.env.production` is fine.

---

## 3. Start the stack

Run from a WSL2 Ubuntu shell (or PowerShell with `wsl` prefix):

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs migrate   # must Exit 0
curl -f http://localhost:8100/healthz                    # {"status":"ok"}
```

Open in a browser (on VPN): `http://<server-LAN-IP>:3100` (or the hostname you set).

**Healthcheck details:** The backend container runs `curl -f http://localhost:8000/healthz` internally
(container port 8000). From the host, the mapped port is 8100, hence `curl localhost:8100/healthz`.

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

Schedule daily (Windows Task Scheduler / cron inside WSL2) until a company-wide backup exists.

---

## 6. Excel migration (separate sitting)

Only after the app is up and Viraj names who owns the data:

```bash
# Always dry-run first
python3 scripts/import_excel.py clients path/to/Clients.xlsx
# ... review report ...
python3 scripts/import_excel.py clients path/to/Clients.xlsx --commit

# Incomplete multi-sheet sets may need stub FKs (SWA-SYS-UNLINKED hold client,
# orphan projects). Opt in with --allow-stubs or IMPORT_ALLOW_STUBS=1:
python3 scripts/import_excel.py document_references path/to/DRN.xlsx --commit --allow-stubs
```

Supported types: see `deliverables/SUBMISSION.md` §7.

---

## 7. Updates later

```bash
cd swa-erp
git pull   # or drop new release
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

Run from a WSL2 Ubuntu shell (or PowerShell with `wsl` prefix). Never `down -v` in production (wipes volumes).

---

## If something fails

| Symptom | Check |
|---------|--------|
| migrate non-zero | `logs migrate`; fix DB URL/password; re-run migrate |
| UI loads, API fails | CORS_ORIGINS must match the browser URL exactly |
| Can't pull images | Network / Docker Hub from that server |
| Port in use | Change host ports in compose; update CORS if UI port changes |
| WSL2 not enabled | `wsl --install` in PowerShell admin; reboot; verify `wsl -l -v` shows Ubuntu |
| Docker Engine not using WSL2 | Docker Desktop not installed; in Docker Engine settings enable "Use the WSL 2 based engine" |
| Secrets not loading | `.env.production` must be in repo root; no spaces around `=` in file |

Longer checklist: `docs/DEPLOYMENT_CHECKLIST.md`. Ops day-to-day: `docs/runbook.md`.
