# Architecture — SWA ERP

## High-level system

```
                    ┌──────────────────────────────────────────┐
                    │  Browser (React SPA, Vite, TS, Tailwind) │
                    └─────────────────┬────────────────────────┘
                                      │ HTTPS · JSON · JWT
                    ┌─────────────────▼────────────────────────┐
                    │  FastAPI (Python 3.11, uvicorn/gunicorn) │
                    │  ├── api/           routers per domain    │
                    │  ├── services/      business logic        │
                    │  ├── schemas/       Pydantic v2 models    │
                    │  ├── models/        SQLAlchemy 2 ORM      │
                    │  └── core/          config, security, deps│
                    └────┬──────────────┬──────────────┬────────┘
                         │              │              │
              ┌──────────▼──┐ ┌─────────▼────┐ ┌───────▼────────┐
              │ PostgreSQL  │ │ Redis        │ │ Local FS / S3  │
              │ (primary)   │ │ (Celery +    │ │ (uploads, docs,│
              │             │ │  cache)      │ │  BOQs, expo)   │
              └─────────────┘ └──────┬───────┘ └────────────────┘
                                     │
                              ┌──────▼──────┐
                              │ Celery      │
                              │ (workers)   │
                              └─────────────┘
```

## Modules (backend)

**Updated 2026-07-21** — the version of this table before today listed the wave-1-8 module plan
only (some with names that never matched the real files, e.g. `api/inventory.py` /
`api/timesheets.py`-only) and predated waves 9-21 entirely. This is the real, current
`src/backend/api/` listing, verified by `ls`, not the original plan.

| Module | Responsibility | Wave |
|---|---|---|
| `api/auth.py` | Login, refresh | 1 |
| `api/users.py` | CRUD users, assign roles | 1 |
| `api/health.py` | `/healthz` | 1 |
| `api/clients.py` | CRUD clients, contacts | 2 |
| `api/projects.py` | CRUD projects | 2 |
| `api/lifecycle.py` | Project lifecycle transitions | 2 |
| `api/boqs.py` | Upload BOQ (JSON/Excel), version | 3 |
| `api/quotes.py` | Generate/version/send quote | 3 |
| `api/tasks.py` | CRUD tasks, assignments, deps | 4 |
| `api/vendors.py` | CRUD vendors | 5 |
| `api/materials.py` | Materials catalog, pricing | 5 |
| `api/rfqs.py` | RFQ-to-vendor workflow | 5 |
| `api/documents.py` | Generic file upload, version, link to project | 6 |
| `api/compliance.py` | Checklists, standards (NBC/ECBC/IGBC/IS) | 6 |
| `api/time_tracking.py` | Log hours, billable/non-billable | 7 |
| `api/invoices.py` | Generate, PDF, mark paid | 7 |
| `api/project_pnl.py` | Project profit & loss | 7 |
| `api/reports.py` | Dashboards | 8 |
| `api/exports.py` | Data exports | 8 |
| `api/inquiries.py` | Lead capture, convert-to-client-and-project | **9** |
| `api/agreements.py` | Service agreements (annual, per-client) | **9** |
| `api/tokens.py` | Units of work under an agreement | **9** |
| `api/document_references.py` | DRN — numbered documents (DBR/KDR/etc.) | **9** |
| `api/sustainability_metrics.py` | Post-project green-standard metrics | **10** |
| `api/notifications.py` | In-app notifications (mounted in wave-17) | 17 |

Modules 9-10 are the actual client-requested MVP core chain
(Inquiry→Client→Agreement→Token→DocumentReference), distinct from the wave 1-8 generic CRM — see
`docs/decisions/0002-core-id-chain-gap.md` for why that distinction matters.

Each module follows the same pattern:
- `api/<domain>.py` — FastAPI router, depends on services
- `services/<domain>_service.py` — business logic, depends on repositories
- `db/repositories/<domain>_repo.py` — SQLAlchemy queries
- `models/<domain>.py` — SQLAlchemy declarative models
- `schemas/<domain>.py` — Pydantic request/response

## Data flow — typical request

```
1. Browser sends POST /api/projects with Bearer token
2. FastAPI dispatches to api/projects.py router
3. Dependency `get_current_user` decodes JWT, fetches user from DB
4. Dependency `require_role("pm")` checks user has PM role
5. Pydantic validates request body against ProjectCreate schema
6. Router calls services.project_service.create_project(payload, user)
7. Service applies business rules (e.g., default status = "Lead")
8. Service calls repo.create_project(...) which uses SQLAlchemy session
9. DB INSERT, returns row
10. Service maps row to ProjectRead schema
11. Router returns ProjectRead serialized to JSON
12. Browser updates React Query cache
```

## State flow — project lifecycle

```
Lead ──→ Quote ──→ Awarded ──→ Design ──→ Vendor ──→ Execution ──→ Validation ──→ Closed
  │       │          │           │          │           │             │
  │       │          │           │          │           │             └─ archive after 1yr
  │       │          │           │          │           └─ compliance signoff required
  │       │          │           │          └─ vendor PO issued
  │       │          │           └─ design docs uploaded
  │       │          └─ client approval recorded
  │       └─ BOQ uploaded, quote sent
  └─ entry point (from contact form / manual entry / Project 1 BOQ upload)
```

Transitions enforced in `services/project_service.transition()`. Each transition triggers:
- Audit log entry
- Notification to assignees
- Optional automated next-step task creation

## User flow — happy path (PM creates project)

```
1. PM logs in → /login → /dashboard
2. PM clicks "New Project" → /projects/new
3. PM selects client (or creates) → fills project basics → SAVE
4. Project lands in "Lead" status on /dashboard
5. PM clicks "Upload BOQ" → drops .json or .xlsx → parsed and shown
6. PM clicks "Generate Quote" → /quotes/new → reviews → SEND
7. Status auto-transitions to "Quote"
8. Client signs (recorded manually in MVP) → PM clicks "Mark Awarded"
9. Status → "Awarded" → auto-creates first design tasks from template
```

## Auth & RBAC

- **JWT**: HS256 only, currently — verified by grep, no RS256 code exists anywhere despite the
  original plan calling for it in prod. Not yet a blocker (HS256 with a strong, properly-set
  `SECRET_KEY` is adequate for a single-backend-instance deployment like this one), but if
  multiple backend instances or third-party token verification is ever needed, RS256 would need
  to actually be built, not just documented as a plan. 1-hour access + 30-day refresh TTLs.
- **bcrypt** for password hashing (cost 12)
- **Roles** (versioned in `core/roles.py`):
  - `admin` — everything
  - `pm` — full CRUD on owned/assigned projects, read all
  - `designer` — read assigned projects, edit tasks + documents
  - `auditor` — read assigned projects, edit compliance + audit findings
  - `viewer` — read-only across permitted scope
- **Permissions** check via FastAPI dependency `require_role(...)` or `require_permission(...)`
- **Audit log** for every mutation; immutable append-only `audit_log` table

## Integrations (MVP)

| Integration | When | How |
|---|---|---|
| Email (transactional) | Quote sent, invoice issued, password reset | Resend or SMTP, queued via Celery |
| PDF generation | Quotes, invoices, BOQ export | WeasyPrint (HTML→PDF) |
| Excel import/export | BOQ upload, reports export | openpyxl |
| File storage | Documents, BOQs, signed PDFs | Local FS in dev, MinIO in prod, S3 ready |
| Background jobs | Email send, PDF gen, periodic reports | Celery + Redis broker |

## Failure points + mitigations

| Failure | Impact | Mitigation |
|---|---|---|
| DB connection lost | API 503 | Connection pool + retry; health check |
| Celery worker crashes | Background tasks stuck | Supervisord; task retry with backoff |
| BOQ upload malformed | Bad data in DB | Schema validation; reject with clear error; never partial-insert |
| User session expired | UX confusion | Auto-refresh token; 401 → redirect to login with toast |
| File upload too large | Storage cost | 50MB cap per file; chunked upload for larger; clear error |
| Two PMs edit same project | Lost update | **Not actually implemented for Project** — `version`-column optimistic locking exists on `BOQ`, `Document`, `ComplianceItem`, `Quote`, and `User` (verified by grep), but `Project` itself has no `version` column. This is a real, unfixed gap if two PMs edit the same project concurrently. |
| Currency rounding | Invoice mismatch | All money as `Decimal(18,2)`; no float anywhere |
| Time zone bugs | Wrong dates in reports | Store UTC, display Asia/Kolkata; never naive datetimes |
| Migration applied wrong | Data corruption | Test migrations on staging copy; never edit applied migrations |

## Validation points

| Layer | What it validates |
|---|---|
| Frontend form | Required fields, basic format (email regex, etc.) |
| API request | Pydantic schemas — types, ranges, enum membership |
| Service | Business rules — lifecycle transitions, permissions |
| DB | Constraints — NOT NULL, FK, UNIQUE, CHECK |
| Background | Long-running validations (large BOQ files) |

## Observability

**Updated 2026-07-21** — verified against actual code, not the original plan:
- **Logs:** structlog IS actually wired (`src/backend/core/middleware.py`) → stdout → Docker.
  fluentd forwarding is still just a "later" plan, not built.
- **Metrics:** Prometheus/`/metrics` — **not implemented**. Grep found zero matches; this row
  was aspirational in the original plan and never built.
- **Errors:** Sentry — **not implemented**. `SENTRY_DSN` exists as a blank optional env var in
  `.env.example` but no `sentry_sdk` import exists anywhere in the codebase. Also aspirational.
- **Audit:** `audit_log` table — this one is real and working, every mutation logged with
  who/when/before/after, verified across many wave reports.
