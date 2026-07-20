# ADR-0003 — IT/Server Call Brief (Windows Server Deployment)

**Date:** 2026-07-20 (v2 — expanded into a full standalone brief so the IT person has complete
project + architecture context, not just a bare question list. The full text sent to IT lives at
the bottom of this file under "Full brief text (send as-is)".)
**Purpose:** Prep for the call with the client's IT/server admin. Meeting 2 already confirmed
the target infra — this call is to nail down the *specific* server-side details that only the
IT person can answer, not to re-derive the architecture from scratch.

## What's already decided (Meeting 2) — state this, don't ask about it
- OS: Windows Server, on-prem, 99% confirmed
- RAM: 128 GB, extendable
- Load target: 100+ concurrent users via VPN/RDP
- Database: PostgreSQL
- File storage: MinIO (S3-compatible), same server
- Containerization: Docker Desktop on Windows Server
- Background jobs: Celery + Redis
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

```
SWA CONSULTANCY ERP — FULL PROJECT & DEPLOYMENT BRIEF FOR IT
Prepared by Srujan | For: [IT Person's Name]

============================================================
PART 1 — WHY THIS PROJECT EXISTS (business context)
============================================================

SWA Consultancy currently runs its entire operations — client onboarding, project tracking,
document numbering, time logging — through about 20 separate Excel files stored on OneDrive.
Everyone edits these live, there's no single source of truth, and the founder (Viraj) has said
directly: "I need clear documentation, a way of a website or workflow, how to proceed further."

That's what this ERP is: a website that replaces those Excel sheets with one system, while
keeping the exact same business logic staff already use day to day. It's not adding new
processes — it's digitizing the existing ones.

THE CORE BUSINESS FLOW (this is the heart of the whole system):

  Inquiry comes in (a lead, e.g. from a referral or website)
      ↓
  Check: does this client already exist in our records?
      → No: create a new Client record
      → Yes: use the existing Client record
      ↓
  A Project gets created under that Client
      ↓
  If it's a recurring client, they may have a Service Agreement (an annual contract,
  not project-by-project — think of it like a retainer)
      ↓
  Work done under that agreement is tracked as "Tokens" — each Token is one unit of work
  requested (e.g. "calculate R-value," "submit thickness report")
      ↓
  When actual documents are produced (reports, drawings, design notes), each one gets a
  unique Document Reference Number so it can be tracked and referenced later
      ↓
  Staff log the hours they spent, tied back to the Project/Token/Document they worked on
      ↓
  After a project finishes, sustainability metrics may be recorded (energy savings, carbon
  savings, etc.) if the client shares that data

Every one of those "records" (Inquiry, Client, Agreement, Token, Document) gets a unique ID
that follows one consistent format the company already uses in their Excel sheets:
  SWA-{year}-{3-letter type code}-{number}
  Examples: SWA-2025-INQ-001 (an inquiry), SWA-2025-CLT-001 (a client),
            SWA-2025-SA-011 (a service agreement), SWA-2025-TKN-001 (a token)

WHAT'S DELIBERATELY NOT INCLUDED (so you know the scope is intentionally limited):
HR records, employee satisfaction surveys, finance/founder-only sheets, client complaints and
satisfaction tracking, and marketing metrics (Instagram/LinkedIn/website stats) are all
explicitly excluded from this system for now — those stay as separate, independent processes.

============================================================
PART 2 — WHAT'S ALREADY BUILT vs. WHAT'S IN PROGRESS
============================================================

Already built and working: client/project management, quotations, task management, vendor and
materials tracking, document uploads, compliance checklists (building code standards),
time tracking, invoicing, and basic reporting/dashboards.

Currently being finished: the specific Inquiry → Client → Agreement → Token → Document
Reference chain described above (this is the part that most directly maps to how staff
currently work in the Excel sheets), plus a tool to import the existing 20 Excel files into the
new system as a one-time migration once it's ready.

None of this changes what I need from you — I'm telling you so you understand what kind of
traffic and data the server will actually be handling: this is a records/workflow system, not
something computationally heavy. Think "digital filing cabinet with a workflow on top," not
"data processing pipeline."

============================================================
PART 3 — HOW THE APPLICATION IS BUILT (technical architecture)
============================================================

In plain terms, the system has these separate pieces, each running as its own "container"
(a self-contained, isolated unit — using a tool called Docker so each piece can be started,
stopped, or replaced independently without affecting the others):

1. THE APPLICATION ITSELF (backend) — written in Python, handles all the business logic
   (creating records, checking permissions, generating IDs, etc.) and exposes it to the
   browser over standard web requests.

2. THE WEBSITE (frontend) — what staff actually see and click on in their browser. Built with
   React (a standard, widely-used web framework), served as static files.

3. THE DATABASE — PostgreSQL, an industry-standard relational database. This is where every
   Client, Project, Token, Document Reference, etc. actually lives permanently.

4. FILE STORAGE — MinIO, a self-hosted alternative to Amazon S3, used to store uploaded files
   (PDFs, Word docs, drawings). Keeps large files out of the database, which is standard practice.

5. BACKGROUND JOB RUNNER — Redis + Celery, used for anything that shouldn't make a staff
   member wait on screen: generating a PDF, sending an email, running a report.

6. LOGIN/SECURITY — staff log in with a username/password (JWT-based session tokens), and
   different staff roles (admin, project manager, designer, auditor, viewer) see different
   things based on permissions — mirroring the "some sheets are open to everyone, some are
   founder-only" access rules already used in the Excel system today.

None of this requires internet-facing exposure — it's meant to run entirely inside the
company's own network, reached by staff over VPN, exactly like the current file-server setup
you already manage. There are no external paid APIs or third-party services involved.

Already confirmed with Viraj on infrastructure:
  - Windows Server, on-prem (99% confirmed)
  - 128 GB RAM, extendable
  - Expected load: 100+ concurrent users over VPN/RDP
  - Docker used for containerization
  - Daily database backup + weekly file backup intended

I'm not asking you to help choose any of this — it's already decided and matches what you're
already running (a Windows file server with VPN access). What I need is specific factual
information about how your server is set up, so I can configure the deployment correctly on
the first try instead of guessing and causing problems later.

============================================================
PART 4 — WHAT I NEED FROM YOU (8 specific, answerable questions)
============================================================

Please answer these directly — a sentence or two each is enough. If you don't know one, just
say so and who I should ask instead.

1. DOCKER LICENSE — Docker (the tool that runs each piece of the app in its own container)
   has a free version and a paid version. The paid version ("Docker Desktop") is only legally
   required for larger companies. Does the server already have Docker installed? If so, is it
   the free "Docker Engine" or paid "Docker Desktop"? If nothing's installed, no problem — I'll
   just need it installed (free version is fine).

2. WINDOWS vs LINUX CONTAINERS — My application is built the standard way almost all web
   apps are built ("Linux-style" containers), even though it'll run on a Windows Server. This
   usually needs a Windows feature called WSL2 turned on. Can you confirm WSL2 is available
   or can be enabled on this server? (I can send you a single command to check if you're unsure.)

3. FREE PORTS — Each piece of the app "listens" on a numbered port. I need about 5 port
   numbers that are free and not already used by something else on that server: one for the
   database, one for the background job tool (Redis), one or two for file storage, and one for
   the app itself. What's already running/reserved on that machine?

4. SECURE CONNECTION (HTTPS) — Since staff will log in with passwords over VPN, the
   connection needs to be encrypted. Does the company already have an internal way of issuing
   secure certificates (an internal certificate authority), or should I set up a basic
   self-signed one to start with?

5. BACKUPS — Is there already a backup process running on this server (for files or other
   data)? I want the database and uploaded documents backed up daily. If you already have
   backup tooling, I'd rather connect into that than build something separate that might clash.

6. INTERNAL WEB ADDRESS — What address will staff actually type or click to reach the app once
   it's live (e.g. something like erp.swa.local, or a plain IP address)? I need to lock this in
   before final setup — changing it later means reconfiguring things.

7. WHERE THE DATABASE RUNS — I can either run the database and Redis inside the same Docker
   setup as the rest of the app (simpler for me to manage day-to-day), or you can install them
   directly on Windows as standalone services if that fits how your team normally manages
   servers. Either works technically — which do you prefer to maintain long-term?

8. HOW UPDATES GET DEPLOYED — When I have a new version ready to push live, what's the best
   way to get it onto the server? Options: you give me direct remote access to update it
   myself, I send you the update and a couple of commands for you to run, or some other process
   you already use for similar software.

============================================================
That's everything. Happy to do this over a quick call if that's faster than typing it all
out — whatever works best for you. Thanks for taking the time to help get this set up right.
============================================================
```
