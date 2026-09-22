# SWA Consultancy ERP — Architecture Overview for Viraj to Forward to IT

**Prepared for:** Viraj (to forward to IT team)
**Date:** 2026-09-22
**Version:** 1.0.1

---

## One-Page Summary (for IT's quick review)

**What:** Internal ERP replacing ~20 Excel files on OneDrive with one web app.

**Architecture:** 6 containers (Docker) — Browser (React) → FastAPI (Python) → PostgreSQL + Redis + MinIO + Celery

**Deployment Target:** Windows Server on-prem (VPN access, 100+ users, 128 GB RAM)

**Data:** PostgreSQL (records) + MinIO (files) — no external APIs, no internet exposure

**Deploy:** `docker compose -f docker-compose.prod.yml up -d` (after filling 8 IT answers)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        VPN / Company Network                     │
├─────────────────────────────────────────────────────────────────┤
│  Browser (Staff) → HTTPS → React Frontend (Port 3100)           │
│                                      ↓                           │
│                          FastAPI Backend (Port 8100)             │
│                    ┌─────────┬──────────┬──────────┐            │
│                    │         │          │          │            │
│              PostgreSQL   Redis      MinIO     Celery            │
│              (Port 5432) (Port 6379) (Port 9000) (Background)   │
│                    │         │          │          │            │
│                    └─────────┴──────────┴──────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

**All pieces run as Docker containers on Windows Server (WSL2 backend).**

---

## Component Details

| Component | Technology | Purpose | Port | Data |
|-----------|------------|---------|------|------|
| **Frontend** | React 18 + Vite + Tailwind | Staff UI | 3100 | Static files |
| **Backend** | FastAPI (Python 3.11) | Business logic, REST API | 8100 | — |
| **Database** | PostgreSQL 16 | All records (Clients, Projects, Tokens, Docs, Time, Invoices) | 5432 | Persistent volume |
| **Cache/Queue** | Redis 7 | Celery broker, rate limiting, sessions | 6379 | Ephemeral |
| **File Storage** | MinIO (S3-compatible) | Uploaded files (PDFs, drawings) | 9000 | Persistent volume |
| **Background Jobs** | Celery + Redis | PDF generation, reports, email | — | — |

---

## Security Model

- **No internet exposure** — runs entirely inside company network, accessed via VPN
- **Authentication:** JWT (HS256 dev / RS256 prod target) + bcrypt password hashing
- **RBAC Roles:** Admin | PM | Designer | Auditor | Viewer (mirrors Excel sheet permissions)
- **Rate Limiting:** 5 login attempts/min/IP (configurable)
- **File Uploads:** Stored in MinIO, not database (keeps DB lean)

---

## Data Model (Core Chain)

```
Inquiry → Client → Service Agreement → Token → Document Reference → Time Log → Invoice
     ↓           ↓              ↓           ↓              ↓           ↓         ↓
  SWA-INQ     SWA-CLT         SWA-SA      SWA-TKN        SWA-DBR     Time      Invoice
  (reset/yr)  (reset/yr)      (reset/yr)  (reset/yr)     (shared DBR/KDR)       (GST)
```

**ID Format:** `SWA-{year}-{TYPE}-{seq:03d}` (counters reset every calendar year)

---

## Infrastructure Requirements (What IT Needs to Provide)

| Item | Requirement | Notes |
|------|-------------|-------|
| **OS** | Windows Server (on-prem) | 99% confirmed — final confirmation pending |
| **RAM** | 128 GB | Extendable |
| **Docker** | Docker Engine (free) or Docker Desktop | WSL2 backend required |
| **WSL2** | Must be enabled on Windows Server | Required for Linux containers |
| **Ports** | 5 free ports (DB 5432, Redis 6379, MinIO 9000, API 8100, UI 3100) | Verify available |
| **HTTPS** | Internal CA cert or self-signed | Staff access via VPN |
| **Backups** | Daily DB dump + weekly file backup | Join existing process if exists |
| **Internal URL** | e.g., `erp.swa.local` or IP | Lock in before deploy |

---

## Deployment Process

1. **IT provides 8 answers** (see `deliverables/SEND_IT.md`)
2. **Fill placeholders** in `docker-compose.prod.yml` + `.env.production.example`
3. **Run:** `docker compose -f docker-compose.prod.yml up -d`
4. **Post-deploy smoke test:** Login → walk core chain → verify GST invoice

**Rollback:** `docker compose down` (preserves volumes) → redeploy previous image tag

---

## Key Facts for IT Decision-Making

| Question | Answer |
|----------|--------|
| **Internet access needed?** | No — fully internal, VPN only |
| **External APIs?** | None — all internal |
| **Data sensitivity** | Client records, financials, compliance docs — internal only |
| **Load profile** | 100+ concurrent users, p95 ≈ 29–130 ms (dev machine tested) |
| **Backup strategy** | Daily DB dump + weekly MinIO backup — join existing process |
| **Updates** | Image-tagged Docker images; `docker compose pull && up -d` |
| **Rollback** | `docker compose down` (keeps volumes) → redeploy previous tag |
| **DB migration** | Runs automatically on container start (`alembic upgrade head`) |

---

## What We Need from IT (8 Questions)

See `deliverables/SEND_IT.md` for the full list. Summary:

1. **Docker** — Installed? Free Engine or paid Desktop?
2. **WSL2** — Available/enabled on Windows Server?
3. **Free ports** — 5 ports needed (DB, Redis, MinIO, API, UI)?
4. **HTTPS** — Internal CA or self-signed cert?
5. **Backups** — Existing process to join?
6. **Internal URL** — What will staff type (e.g., `erp.swa.local`)?
7. **DB location** — Inside Docker or Windows services?
8. **Deploy process** — Remote access, commands, or existing pipeline?

---

## Current Status

| Item | Status |
|------|--------|
| Application code | ✅ Complete (v1.0.1) |
| Backend tests | 654 passed |
| Frontend tests | 600 passed |
| Code quality (ruff/black/mypy) | Clean |
| Smoke chain | Full chain verified end-to-end |
| Alembic migrations | Single head 0042 |
| Docker compose (dev) | Working |
| Docker compose (prod) | Ready — needs IT answers |
| Windows Server deploy | **Blocked on IT answers** |

---

## What We Need from Viraj/IT to Go Live

1. **IT answers** to the 8 questions above
2. **Migration owner** named (who runs the real Excel → ERP import at go-live)
3. **Internal URL** confirmed (e.g., `erp.swa.local`)
4. **HTTPS cert** decision (internal CA or self-signed)

---

## Contact

**Srujan** — Developer
- Questions about architecture, deployment, or data model
- Happy to do a 15-min call with IT to walk through this

---

*This document is designed to be forwarded directly to IT. All technical decisions are already made — only the 8 factual answers are needed from IT to configure the deployment correctly on the first try.*