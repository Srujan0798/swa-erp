# SWA Consultancy ERP — Brief for the IT Team

**From:** Srujan
**For:** Vikrant / IT
**Date:** August 2026

---

## What this is

SWA runs its operations — client onboarding, project tracking, document numbering, time logging —
through about 20 Excel files on OneDrive. Everyone edits them live; there is no single source of
truth. This ERP is a website that replaces those sheets with one system, keeping the exact same
business logic staff already use. It runs entirely inside the company network, reached over VPN,
like the current file-server setup.

## How it is built (in plain terms)

Separate pieces, each running as its own container (a self-contained unit using Docker):

1. **The app (backend)** — Python, all business logic, exposed to the browser over web requests.
2. **The website (frontend)** — React, what staff see and click.
3. **The database** — PostgreSQL. Every Client, Project, Token, Document Reference lives here.
4. **File storage** — MinIO (self-hosted, S3-compatible) for uploaded files (PDFs, drawings).
5. **Background job runner** — Redis + Celery, for work that shouldn't make staff wait (PDF/report generation).
6. **Login/security** — username/password with role-based permissions (admin, PM, designer, auditor, viewer).

No external paid APIs, no third-party services, no internet exposure.

## Already confirmed with Viraj

- Windows Server, on-prem (99% confirmed)
- 128 GB RAM, extendable
- 100+ concurrent users over VPN — **IT's claim about the server; load-tested by us at
  10/50/100 users with no server errors.** Wave-35 measured **p95 ≈ 29–51 ms at 10–100
  concurrent users on a dev machine** (`docs/PERFORMANCE.md`). The client's Windows Server
  itself has **not** been load-tested; that is the remaining step before 100+ can be promised
  for production.
- Docker for containerization
- Daily DB backup + weekly file backup intended

## What we need from IT — 8 factual answers

A sentence or two each is enough. If you don't know one, say so and who to ask.

1. **Docker** — already installed on the server? If yes, free "Docker Engine" or paid "Docker
   Desktop"? If nothing installed, it just needs installing (free version is fine).
2. **WSL2 / Linux containers** — the app uses standard Linux-style containers on the Windows
   Server, which usually needs a Windows feature called WSL2. Can you confirm WSL2 is available
   or can be enabled? (Happy to send a single command to check.)
3. **Free ports** — about 5 port numbers need to be free (database, Redis, file storage ×1–2,
   the app itself). What's already running/reserved on that machine?
4. **HTTPS** — staff log in with passwords over VPN, so the connection must be encrypted. Does
   the company have an internal way of issuing certificates, or should a self-signed one be set
   up to start?
5. **Backups** — is there an existing backup process on the server? The database and uploaded
   documents need daily backup. Better to join the existing process than build a separate one
   that might clash.
6. **Internal web address** — what will staff type/click to reach the app (e.g. `erp.swa.local`
   or a plain IP)? Must be locked before final setup — changing later means reconfiguring.
7. **Where the database runs** — database and Redis inside the same Docker setup, or installed
   directly on Windows as services? Either works — which is easier for your team to maintain
   long-term?
8. **Deploying updates** — when a new version is ready, what's the best way to get it onto the
   server: direct remote access, a couple of commands to run, or an existing process you already use?

## Why these answers matter

Deployment is configured correctly the first time, instead of guessing and causing problems
later. Think "digital filing cabinet with a workflow on top," not a data-processing pipeline —
nothing computationally heavy.

That's everything. Happy to do this over a quick call if that's faster than typing it all out.
Thanks for taking the time to help get this set up right.
