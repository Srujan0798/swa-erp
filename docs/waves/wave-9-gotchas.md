# Wave 9 — Gotchas

> **Source:** Harvested from `work/reports/wave-9/` — real gotchas only, nothing invented.

## Known pitfalls

### Reference-ID service signature
The shared reference-ID service `generate_reference_id(db: Session, entity_type: str) -> str` returns `SWA-{year}-{TYPE}-{seq:03d}`. Used with codes `SA`, `INQ`, `CLT`, `TKN` and document counter keys. Callers: `agreement_service.py:41`, `inquiry_service.py:53,135`, `token_service.py:42`, `document_reference_service.py:78`.

Do NOT use a db-less signature — ADR-0002:31 proposes one but the real implementation takes `db`.

### Alembic revisions are zero-padded
Always use `--rev-id=NNNN_*`. Revisions run `0001`…`0025`, one migration per concern.

### Backend service convention
One function per operation, takes `db: Session` + `actor_id: uuid.UUID`, returns ORM model or raises a typed exception.

### Backend repo convention
`<entity>_repo.py` exposing `list_*`, `get_by_id`, `create`, `update`, `soft_delete` via a `deleted_at` column.

### E2E suite is small
Exactly 3 spec files = 7 tests (login 4, dashboard 1, BOQ/quote 2). Located in `tests/e2e/`.

### App version never bumped
`pyproject.toml:7` and `package.json:4` still `0.2.0` though waves 4-21 shipped. Release-versioning discipline is missing.

### Waves 22-24 have briefs, no reports
Wave-25 was done inline with no brief (directory empty).
