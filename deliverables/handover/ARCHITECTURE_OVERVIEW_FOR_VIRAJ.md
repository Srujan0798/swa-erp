# SWA ERP — Architecture Overview (forwardable)

*For Viraj to forward to IT / keep on file. Plain language, no business
background — you already know that. Just what the system is made of and how it
runs. Full technical brief for IT is the separate `docs/IT_BRIEF.md`.*

---

## What it is
A website that replaces ~20 Excel files with one system, running **entirely
inside the company network** (staff reach it over VPN, like today's file
server). No external paid services, no public internet exposure.

## The 6 pieces (each runs in its own Docker container)
1. **Backend (the app logic)** — Python. Creates records, checks permissions,
   generates the `SWA-YYYY-XXX-001` IDs. Talks to the browser over standard web
   requests.
2. **Frontend (the website)** — what staff click. React, served as static files.
3. **Database** — PostgreSQL. Where every Client, Project, Token, Document, etc.
   permanently lives.
4. **File storage** — currently a local folder on the server disk. Holds
   uploaded PDFs/drawings so big files stay out of the database. (MinIO — a
   more scalable S3-style storage option — was planned but not built yet; the
   current local-folder approach works fine for now and can be upgraded later
   without disrupting anything.)
5. **Background jobs** — currently handled directly, in real time, when a
   staff member clicks the action (e.g. generating a PDF happens immediately,
   not queued). Redis + Celery are installed and ready for this but not yet
   wired up — fine at current scale, worth revisiting once volume grows.
6. **Login/security** — username + password (JWT). Five roles (admin, PM,
   designer, auditor, viewer) see different things, matching today's sheet
   access rules.

## Confirmed infrastructure (per Viraj)
- Windows Server, on-prem
- 128 GB RAM (extendable)
- Expected load: 100+ concurrent users over VPN/RDP — *IT's claim about the server. Wave-35
  load tests verified **10/50/100 concurrent users, p95 ≈ 29–51 ms, no server errors** on a dev
  machine (see `docs/PERFORMANCE.md`); the client's server itself has not been load-tested.*
- Docker for containerization
- Daily DB backup + weekly file backup intended

## What IT needs to confirm (the 8 questions in `docs/IT_BRIEF.md`)
Docker (Engine vs Desktop), WSL2 for Linux containers, free ports, HTTPS/cert
source, existing backup tooling, the internal web address, where DB/Redis run,
and how updates get deployed.

## Status
Core system built and verified end to end (inquiry → client → project →
agreement → token → document → time → sustainability). A tool exists to import
the existing Excel files in one go. Production config templates are ready and
just need the 8 IT answers plugged in.
