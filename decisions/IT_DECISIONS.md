# IT Decision Log — 8 Factual Answers Required

**For:** Vikrant / IT Team  
**From:** Viraj (forward this + `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md`)  
**Deadline:** Before production deploy  
**Format:** One sentence per answer. If unknown, say "Ask [name]."

---

## 🔴 8 Required Answers (One Per Line)

| # | Question | Your Answer |
|---|----------|-------------|
| 1 | **Docker** — Already installed? If yes, free "Docker Engine" or paid "Docker Desktop"? If none, free Engine is fine. | |
| 2 | **WSL2 / Linux containers** — Is WSL2 available/enabled on the Windows Server? (Needed for Linux containers.) | |
| 3 | **Free ports** — 5 ports needed (DB:5432, Redis:6379, MinIO:9000, API:8100, UI:3100). What's already running/reserved? | |
| 4 | **HTTPS / Certificates** — Internal CA available, or use self-signed for start? | |
| 5 | **Backups** — Existing backup process on server? Daily DB + weekly file backup needed. Join existing or build new? | |
| 6 | **Internal web address** — What will staff type/click? (e.g., `erp.swa.local` or IP) Must lock before deploy. | |
| 7 | **Database location** — PostgreSQL + Redis inside Docker (simpler) or Windows services? Your preference for maintenance. | |
| 8 | **Deploy process** — How to push updates: direct remote access, commands to run, or existing pipeline? | |

---

## What Happens Next

1. **You answer** → We fill placeholders in `docker-compose.prod.yml` + `.env.production.example`
2. **We deploy** → `docker compose -f docker-compose.prod.yml up -d`
3. **Smoke test** → Login → walk core chain → verify GST invoice
4. **Rollback plan** → `docker compose down` (keeps data) → redeploy previous tag

---

## What We've Already Built (No IT Work Needed)

| Component | Status |
|-----------|--------|
| PostgreSQL schema | ✅ 38 tables, Alembic head 0042 |
| Redis + Celery | ✅ Background jobs (PDF, reports) |
| MinIO file storage | ✅ Local uploads/ + MinIO opt-in |
| JWT auth + RBAC | ✅ 5 roles (admin/pm/designer/auditor/viewer) |
| Rate limiting | ✅ 5 login/min/IP |
| Backup scripts | ✅ `make backup-db` / `backup-files` / `restore-db` |
| Alembic migrations | ✅ Single head 0042, auto-run on container start |

---

## What We Need From You (Only)

| Item | You Provide | We Configure |
|------|-------------|--------------|
| Docker/WSL2/ports | ✅ | `docker-compose.prod.yml` ports |
| HTTPS cert | ✅ | `nginx`/`traefik` config in compose |
| Backup process | ✅ | `make backup-db` cron or your tool |
| Internal URL | ✅ | `SERVER_NAME` in `.env.production` |
| DB location | ✅ | Compose `postgres` service or external |
| Deploy method | ✅ | Document in runbook |

---

## Quick Reference

**Files to review:**
- `docker-compose.prod.yml` — production compose (has `PENDING IT ANSWER` placeholders)
- `.env.production.example` — environment template (has `PENDING IT ANSWER` placeholders)
- `deliverables/handover/ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` — full architecture (forward to IT)
- `docs/DEPLOYMENT_CHECKLIST.md` — step-by-step deploy steps

**Ports we need (defaults, changeable):**
| Service | Default Port |
|---------|--------------|
| PostgreSQL | 5432 |
| Redis | 6379 |
| MinIO API | 9000 |
| Backend API | 8100 |
| Frontend UI | 3100 |

---

## Contact

**Srujan** — Developer | Happy to do 15-min call to walk through this.

---

*Updated: 2026-09-21 | Product v1.0.1 | All code gates pass*