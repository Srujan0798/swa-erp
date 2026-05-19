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

| Module | Responsibility | Files |
|---|---|---|
| `api/auth.py` | Login, refresh, password reset | router + service |
| `api/users.py` | CRUD users, assign roles | router + service |
| `api/clients.py` | CRUD clients, contacts | router + service |
| `api/projects.py` | CRUD projects, lifecycle transitions | router + service |
| `api/boq.py` | Upload BOQ (JSON/Excel), version, approve | router + service + parser |
| `api/quotes.py` | Generate/version/send quote | router + service |
| `api/tasks.py` | CRUD tasks, assignments, deps | router + service |
| `api/vendors.py` | CRUD vendors, vendor RFQs | router + service |
| `api/inventory.py` | Materials catalog, pricing | router + service |
| `api/documents.py` | Upload, version, link to project | router + service |
| `api/compliance.py` | Checklists, standards (NBC/ECBC/IGBC/IS), audit trail | router + service |
| `api/timesheets.py` | Log hours, billable/non-billable | router + service |
| `api/invoices.py` | Generate, PDF, mark paid | router + service |
| `api/reports.py` | Dashboards, exports | router + service |

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

- **JWT** (HS256 in dev, RS256 in prod) with 1-hour access + 30-day refresh
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
| Two PMs edit same project | Lost update | Optimistic locking via `version` column + `If-Match` header |
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

- **Logs:** structlog → stdout → Docker → fluentd (later)
- **Metrics:** Prometheus client → /metrics → Grafana (later)
- **Errors:** Sentry SDK integrated, env-gated
- **Audit:** `audit_log` table — every mutation, who, when, what before/after
