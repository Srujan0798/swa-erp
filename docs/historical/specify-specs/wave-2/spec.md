# Wave 2 — Clients + Projects (Core)

## Goal
Ship CRM-lite + project tracking. A PM can create clients, create projects linked to clients, assign team members, and move projects through the lifecycle (Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed).

## User stories

### US-2.1 — As a PM, I can create a client
**Given** I am logged in as PM or admin
**When** I fill the client form (name, code, address, GST, contacts) and save
**Then** the client appears in the clients list.

### US-2.2 — As a PM, I can create a project
**Given** I have created a client
**When** I select the client, fill project basics (name, code, location, estimated value), assign PM/designer/auditor, and save
**Then** the project is created with status "Lead" and appears on the dashboard.

### US-2.3 — As a PM, I can transition a project's status
**Given** a project exists in status "Lead"
**When** I click "Move to Quote"
**Then** the project status changes to "Quote", an audit log entry is created, and a placeholder task template is noted (real tasks in wave-4).

### US-2.4 — As any user, I see project stats on the dashboard
**Given** I am on /dashboard
**Then** I see cards: total active projects, projects by status, recent projects, recent clients.

### US-2.5 — As a PM, I can search and paginate clients/projects
**Given** there are 50+ clients or projects
**When** I type in the search box
**Then** results filter by name/code/email and paginate.

## In scope (wave-2 only)

- Client model + contacts (1 client has many contacts)
- Project model linked to client + users (PM, designer, auditor)
- Project lifecycle: 8 statuses, transition rules, audit logging
- Dashboard: stats cards + recent lists
- Clients list/detail pages with search/pagination
- Projects list/detail pages with search/pagination + status filter
- Soft-delete for clients and projects
- DB indexes: clients(name, code), projects(client_id, status, pm_id), contacts(client_id)

## Out of scope (later waves)
- BOQ/Quote workflow — wave-3
- Task management — wave-4
- Document upload on projects — wave-6
- Time tracking per project — wave-7
- Financials / invoicing — wave-7
- Vendor assignment on projects — wave-5
- Compliance checklists — wave-6
- Advanced filters (date range, value range) — wave-8

## Success criteria
- [ ] `pytest tests/wave-2/` passes 100%
- [ ] `make lint` clean
- [ ] PM can create client → create project → assign team → transition status end-to-end
- [ ] Dashboard shows real project stats (not placeholders)
- [ ] Search + pagination works for both clients and projects
- [ ] CI green on push

## Performance budgets
- Client list: < 100ms for 500 clients
- Project list: < 150ms for 500 projects
- Dashboard stats: < 200ms
- DB queries per list request: ≤ 3 (including count)

## Data model

```sql
-- clients
id            UUID PK
name          TEXT NOT NULL
code          TEXT UNIQUE NOT NULL
address       TEXT
city          TEXT
state         TEXT
pincode       TEXT
country       TEXT NOT NULL DEFAULT 'India'
gst_number    TEXT
primary_email TEXT NOT NULL
primary_phone TEXT
notes         TEXT
is_active     BOOLEAN NOT NULL DEFAULT TRUE
created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
deleted_at    TIMESTAMPTZ NULL

-- contacts (belongs to client)
id            UUID PK
client_id     UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE
name          TEXT NOT NULL
email         TEXT NOT NULL
phone         TEXT
designation   TEXT
is_primary    BOOLEAN NOT NULL DEFAULT FALSE
created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()

-- projects
id              UUID PK
client_id       UUID NOT NULL REFERENCES clients(id)
name            TEXT NOT NULL
code            TEXT UNIQUE NOT NULL
description     TEXT
status          TEXT NOT NULL CHECK (status IN ('Lead','Quote','Awarded','Design','Vendor','Execution','Validation','Closed')) DEFAULT 'Lead'
pm_id           UUID NULL REFERENCES users(id)
designer_id     UUID NULL REFERENCES users(id)
auditor_id      UUID NULL REFERENCES users(id)
location        TEXT
estimated_value DECIMAL(18,2)
actual_value    DECIMAL(18,2)
start_date      DATE
target_end_date DATE
actual_end_date DATE
is_active       BOOLEAN NOT NULL DEFAULT TRUE
created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
deleted_at      TIMESTAMPTZ NULL
```

## API surface (wave-2)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/clients` | bearer + pm/admin | List clients (paginated, search q) |
| POST | `/api/clients` | bearer + pm/admin | Create client |
| GET | `/api/clients/{id}` | bearer | Read client + contacts |
| PATCH | `/api/clients/{id}` | bearer + pm/admin | Update client |
| DELETE | `/api/clients/{id}` | bearer + admin | Soft-delete client |
| POST | `/api/clients/{id}/contacts` | bearer + pm/admin | Add contact |
| PATCH | `/api/clients/{id}/contacts/{contact_id}` | bearer + pm/admin | Update contact |
| DELETE | `/api/clients/{id}/contacts/{contact_id}` | bearer + pm/admin | Remove contact |
| GET | `/api/projects` | bearer + pm/admin | List projects (paginated, search q, status filter) |
| POST | `/api/projects` | bearer + pm/admin | Create project |
| GET | `/api/projects/{id}` | bearer | Read project |
| PATCH | `/api/projects/{id}` | bearer + pm/admin | Update project |
| DELETE | `/api/projects/{id}` | bearer + admin | Soft-delete project |
| POST | `/api/projects/{id}/transition` | bearer + pm/admin | Transition status |
| GET | `/api/projects/stats` | bearer | Dashboard stats |
