# Wave 2 — Plan

## Tasks (5)

1. **Clients API** — models, migration, schemas, repo, service, router, tests
2. **Projects API** — models, migration, schemas, repo, service, router, tests
3. **Lifecycle + Stats Service** — state machine, transition rules, audit logging, /projects/stats endpoint, tests
4. **Dashboard Frontend** — stats cards, recent projects, recent clients, quick actions
5. **Clients + Projects UI** — list pages, detail pages, create/edit forms, search, status filters

## Dependency graph

```
01-clients-api ──┐
                 ├──→ 03-lifecycle-service ──→ 04-dashboard-frontend
02-projects-api ─┘                           └──→ 05-clients-projects-ui
```

Workers can run 01, 02, 04, 05 in parallel (04 and 05 need backend on :8000 for E2E).
03 should ideally wait for 01+02 migrations, but can be written assuming models exist.

## Acceptance contracts

All contracts live in `.specify/specs/wave-2/contracts/`.

## Notes
- Use `Decimal(18,2)` for money columns (estimated_value, actual_value)
- Use `Date` (not DateTime) for start_date, target_end_date, actual_end_date
- Client code and project code must be unique; validate in Pydantic + DB constraint
- Contacts are nested under clients (not standalone resource)
- Lifecycle transitions are POST /api/projects/{id}/transition with `{to_status}` body
- Soft-delete: deleted_at IS NOT NULL; lists exclude soft-deleted
- All mutations write audit_log entries
