# SWA Consultancy ERP — Full Project & Deployment Brief for IT

**Prepared by:** Srujan
**For:** Vikrant

---

## Part 1 — Why this project exists (business context)

SWA Consultancy currently runs its entire operations — client onboarding, project tracking,
document numbering, time logging — through about 20 separate Excel files stored on OneDrive.
Everyone edits these live, there's no single source of truth, and the founder (Viraj) has said
directly: *"I need clear documentation, a way of a website or workflow, how to proceed further."*

That's what this ERP is: a website that replaces those Excel sheets with one system, while
keeping the exact same business logic staff already use day to day. It's not adding new
processes — it's digitizing the existing ones.

### The core business flow (the heart of the whole system)

```
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
```

Every one of those records (Inquiry, Client, Agreement, Token, Document) gets a unique ID that
follows one consistent format the company already uses in their Excel sheets:

`SWA-{year}-{3-letter type code}-{number}`

Examples: `SWA-2025-INQ-001` (an inquiry), `SWA-2025-CLT-001` (a client),
`SWA-2025-SA-011` (a service agreement), `SWA-2025-TKN-001` (a token)

### What's deliberately not included

HR records, employee satisfaction surveys, finance/founder-only sheets, client complaints and
satisfaction tracking, and marketing metrics (Instagram/LinkedIn/website stats) are all
explicitly excluded from this system for now — those stay as separate, independent processes.

---

## Part 2 — What's already built vs. what's in progress

**Already built and working:** client/project management, quotations, task management, vendor
and materials tracking, document uploads, compliance checklists (building code standards), time
tracking, invoicing, and basic reporting/dashboards.

**Currently being finished:** the specific Inquiry → Client → Agreement → Token → Document
Reference chain described above (this is the part that most directly maps to how staff currently
work in the Excel sheets), plus a tool to import the existing 20 Excel files into the new system
as a one-time migration once it's ready.

None of this changes what's needed from IT — it's context so you understand what kind of traffic
and data the server will actually be handling: this is a records/workflow system, not something
computationally heavy. Think "digital filing cabinet with a workflow on top," not "data
processing pipeline."

---

## Part 3 — How the application is built (technical architecture)

> **Corrected 2026-08-10** — this section now describes the ACTUAL build. As of wave-31:
> Items 4 and 5 below (MinIO, Redis+Celery) are implemented. File storage uses MinIO with a
> local `uploads/` fallback (configurable via `STORAGE_BACKEND`), and a Celery worker runs
> background jobs (PDF/report generation) with `make worker`. Redis + Celery still require a
> Redis server on the deployment host.

In plain terms, the system has these separate pieces, each running as its own "container" (a
self-contained, isolated unit — using a tool called Docker so each piece can be started, stopped,
or replaced independently without affecting the others):

1. **The application itself (backend)** — written in Python, handles all the business logic
   (creating records, checking permissions, generating IDs, etc.) and exposes it to the browser
   over standard web requests.
2. **The website (frontend)** — what staff actually see and click on in their browser. Built with
   React (a standard, widely-used web framework), served as static files.
3. **The database** — PostgreSQL, an industry-standard relational database. This is where every
   Client, Project, Token, Document Reference, etc. actually lives permanently.
4. **File storage** — MinIO, a self-hosted alternative to Amazon S3, used to store uploaded files
   (PDFs, Word docs, drawings). Keeps large files out of the database, which is standard practice.
5. **Background job runner** — Redis + Celery, used for anything that shouldn't make a staff
   member wait on screen: generating a PDF, sending an email, running a report.
6. **Login/security** — staff log in with a username/password (JWT-based session tokens), and
   different staff roles (admin, project manager, designer, auditor, viewer) see different things
   based on permissions — mirroring the "some sheets are open to everyone, some are founder-only"
   access rules already used in the Excel system today.

None of this requires internet-facing exposure — it's meant to run entirely inside the company's
own network, reached by staff over VPN, exactly like the current file-server setup you already
manage. There are no external paid APIs or third-party services involved.

**Already confirmed with Viraj on infrastructure:**
- Windows Server, on-prem (99% confirmed)
- 128 GB RAM, extendable
- Expected load: 100+ concurrent users over VPN/RDP
- Docker used for containerization
- Daily database backup + weekly file backup intended

This is not asking IT to help choose any of the above — it's already decided and matches what's
already running (a Windows file server with VPN access). What's needed is specific factual
information about how the server is set up, to configure the deployment correctly on the first
try instead of guessing and causing problems later.

---

## Part 4 — What's needed from IT (8 specific, answerable questions)

Please answer these directly — a sentence or two each is enough. If you don't know one, just say
so and who to ask instead.

1. **Docker license** — Docker (the tool that runs each piece of the app in its own container)
   has a free version and a paid version. The paid version ("Docker Desktop") is only legally
   required for larger companies. Does the server already have Docker installed? If so, is it the
   free "Docker Engine" or paid "Docker Desktop"? If nothing's installed, no problem — it'll just
   need installing (free version is fine).
2. **Windows vs Linux containers** — the application is built the standard way almost all web
   apps are built ("Linux-style" containers), even though it'll run on a Windows Server. This
   usually needs a Windows feature called WSL2 turned on. Can you confirm WSL2 is available or
   can be enabled on this server? (Happy to send a single command to check if unsure.)
3. **Free ports** — each piece of the app "listens" on a numbered port. About 5 port numbers are
   needed that are free and not already used by something else on that server: one for the
   database, one for the background job tool (Redis), one or two for file storage, and one for
   the app itself. What's already running/reserved on that machine?
4. **Secure connection (HTTPS)** — since staff will log in with passwords over VPN, the
   connection needs to be encrypted. Does the company already have an internal way of issuing
   secure certificates (an internal certificate authority), or should a basic self-signed one be
   set up to start with?
5. **Backups** — is there already a backup process running on this server (for files or other
   data)? The database and uploaded documents need to be backed up daily. If backup tooling
   already exists, better to connect into that than build something separate that might clash.
6. **Internal web address** — what address will staff actually type or click to reach the app
   once it's live (e.g. something like `erp.swa.local`, or a plain IP address)? This needs to be
   locked in before final setup — changing it later means reconfiguring things.
7. **Where the database runs** — the database and Redis can either run inside the same Docker
   setup as the rest of the app (simpler to manage day-to-day), or be installed directly on
   Windows as standalone services if that fits how the team normally manages servers. Either
   works technically — which is preferred to maintain long-term?
8. **How updates get deployed** — when a new version is ready to push live, what's the best way
   to get it onto the server? Options: direct remote access to update it directly, sending the
   update with a couple of commands to run, or some other process already used for similar
   software.

---

That's everything. Happy to do this over a quick call if that's faster than typing it all out —
whatever works best. Thanks for taking the time to help get this set up right.
