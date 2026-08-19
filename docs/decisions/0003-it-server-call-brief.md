# ADR-0003 — IT/Server Call Brief (Windows Server Deployment)

**Date:** 2026-07-20 (v2 — expanded into a full standalone brief so the IT person has complete
project + architecture context, not just a bare question list. The full text sent to IT is the
canonical copy in `docs/IT_BRIEF.md`.)
**Purpose:** Prep for the call with the client's IT/server admin. Meeting 2 already confirmed
the target infra — this call is to nail down the *specific* server-side details that only the
IT person can answer, not to re-derive the architecture from scratch.

## What's already decided (Meeting 2) — state this, don't ask about it
- OS: Windows Server, on-prem, 99% confirmed
- RAM: 128 GB, extendable
- Load target: 100+ concurrent users via VPN/RDP — **IT's claim (per Viraj) about the server.**
  Wave-35 load tests verified **10/50/100/150 concurrent users, p95 ≈ 29–130 ms, no server
  errors** on a dev machine (`docs/PERFORMANCE.md`); the client's Windows Server itself remains
  unload-tested.
- Database: PostgreSQL
- File storage: MinIO (S3-compatible), same server — **target decision; shipped in wave-31
  (2026-08-10) via `StorageBackend` (`STORAGE_BACKEND=minio`); `local` `uploads/` remains the
  default — see `HIERARCHY.md`**
- Containerization: Docker Desktop on Windows Server
- Background jobs: Celery + Redis — **target decision; shipped in wave-31 (2026-08-10) —
  `src/backend/workers/` Celery app + compose `worker` service, Redis as broker/backend**
- PDF generation: WeasyPrint (HTML→PDF)
- Excel import/export: openpyxl
- Backend: FastAPI (Python 3.11), internal REST only, no paid external APIs
- Auth: JWT — **correction 2026-07-21: HS256 only, RS256 was never actually implemented**
  despite being listed here and in the original architecture plan; verified by grep, no RS256
  code path exists anywhere. HS256 with a properly-set `SECRET_KEY` (see wave-18) is adequate
  for this single-backend-instance deployment; don't tell IT RS256 is happening unless it
  actually gets built first.

You are not asking IT to choose the stack. It's chosen. You're asking them to fit it onto their
box and tell you the constraints.

## The 8 things you actually need from this call

Ask these as direct, closed questions. Each one blocks a concrete deployment decision — don't
let the call drift into a general architecture discussion.

1. **Docker Desktop license status** — Docker Desktop requires a paid license for business use
   at >250 employees / >$10M revenue. Confirm whether SWA Consultancy is licensed, or whether
   you should target **Docker Engine + Docker Compose CLI** on Windows Server instead (no
   licensing issue, same Compose files work, just no GUI). This changes the install instructions
   you write, not the app.
2. **Windows Server version and container mode** — exact Windows Server edition/build, and
   whether containers will run in **Windows containers** or **Linux containers via WSL2**. Your
   Dockerfiles (`Dockerfile`, `Dockerfile.frontend`) are Linux-based — confirm WSL2 is
   available/enabled, otherwise you need a different base image strategy.
3. **Port and firewall allocation** — which ports are free/allowed for: backend (currently 8000
   in dev), frontend (currently 3000, but prod likely serves built static assets through
   nginx/IIS on 80/443), PostgreSQL (5432), Redis (6379), MinIO (9000/9001). Ask what's already
   in use on that box.
4. **TLS/certificate strategy** — internal CA cert, self-signed, or a real cert for the VPN-only
   internal hostname staff will hit. This determines whether you configure HTTPS termination in
   nginx or hand it off to something IT already runs.
5. **Backup ownership and schedule** — Meeting 2 flagged "daily DB dump, weekly file backup" as
   the intended strategy but never confirmed who runs it. Ask: does IT have existing backup
   tooling (e.g. Windows Server Backup, a scheduled task runner) you should hook a
   `pg_dump`/MinIO snapshot script into, or do you need to build and schedule it yourself via
   Celery beat?
6. **VPN access model for staff** — Meeting 2 mentions "shortcut in user folders," implying
   staff reach the app via an internal hostname over VPN, not a public URL. Confirm the exact
   hostname/DNS entry so you can hardcode the right `VITE_API_URL` / CORS origin for prod
   instead of guessing at build time.
7. **Redis/Postgres as Windows services vs. containers** — Meeting 2 says "Celery worker as
   Windows service" was still to be finalized. Confirm: does everything (Postgres, Redis,
   backend, frontend, Celery worker) run inside Docker Compose, or does IT want Postgres/Redis
   installed natively as Windows services with only the app containers in Docker? This changes
   your `docker-compose.yml` significantly — ask before writing prod compose config.
8. **Who has server access for deploys** — do you get direct RDP/VPN access to push updates, or
   does IT run a `docker compose pull && up -d` on your behalf on a schedule? Determines whether
   you need to hand over a runbook or a full deploy pipeline.

## What NOT to do on this call
- Don't ask "what architecture should we use" — you already have one (Meeting 2), and the client
  scolded this pattern already: don't hand back an open assignment and ask them to fill in the
  plan. Bring the plan, ask for the 8 specific confirmations above.
- Don't ask about anything already decided in the "already decided" list — re-litigating those
  wastes the IT person's time and reads as not having read your own meeting notes.
- Don't commit to a delivery date on this call — infra constraints (item 1, 2, 5 especially)
  could change the deployment shape; get the answers first, then estimate.

## After the call
Record the answers back into this file (append a "## Answers" section) and update
`docker-compose.yml` / `Dockerfile*` / `.env.example` to match whatever's confirmed — those are
currently written for local dev assumptions (Linux containers, ports 8000/3000) that may not
hold in the Windows Server target.

## Full brief text (send as-is)

The full send-as-is brief for IT (business context, what's built vs. in progress, technical
architecture, and the 8 questions) lives in [`deliverables/SEND_IT.md`](../../deliverables/SEND_IT.md) — that file is
the canonical, sendable copy (supersedes the earlier `docs/IT_BRIEF.md`, now archived to
`docs/historical/IT_BRIEF-superseded.md`). This ADR records only *why* each of the 8 questions is
being asked (see "The 8 things you actually need from this call" above); do not duplicate the
brief text here. It was previously embedded in this file in full and drifted once on the RS256
claim — keep a single source of truth and edit `deliverables/SEND_IT.md`, not this ADR.
