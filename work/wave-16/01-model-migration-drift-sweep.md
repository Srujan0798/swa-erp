# Task 01 — Sweep remaining models for migration drift (Material, Contact, ComplianceItem, etc.)

## What to do
Wave-12's independent verification found that `Task` and `Document` models had columns defined
in the SQLAlchemy model that were never added by their Alembic migrations — this caused live
500 errors (`column tasks.reporter_id does not exist`) that unit tests never caught because the
test suite uses `Base.metadata.create_all()` instead of running real migrations. Two migrations
were added to fix those two models (`0021_align_tasks_with_model.py`,
`0022_align_documents_with_model.py`). The wave-12 report explicitly flags this as a systemic
pattern likely affecting other models that weren't exercised in that session. Find and fix all
remaining instances.

**Depends on wave-14 (docker-compose auto-migrate) landing first**, so you have a reliable way
to stand up a fresh-migrated database to diff against.

## Files to investigate
- Every file in `src/backend/models/*.py`
- Every file in `src/backend/alembic/versions/*.py`

## Files you may create
- CREATE: new Alembic migration(s), one per model family that has drift (follow the naming
  pattern `00NN_align_<model>_with_model.py` used by 0021/0022), each with `down_revision`
  pointing at the current latest head for its branch (there are multiple heads — check
  `alembic -c src/backend/alembic.ini heads` and pick a sensible parent, don't guess)

## Files you must NOT touch
- `0021_align_tasks_with_model.py`, `0022_align_documents_with_model.py` — already correct,
  don't modify
- Model files themselves — the model is the source of truth here; migrations should be updated
  to match the models, not the other way around, UNLESS you find a model field that's clearly
  dead/unused code, in which case flag it in the report rather than silently deleting it

## The core problem (inline)
Systematic method (don't skip steps, this is exactly how the Task/Document bugs were found):
1. Bring up a stack with the docker-compose auto-migrate fix from wave-14 (fresh volumes, so
   migrations run from scratch): `docker-compose down -v && docker-compose up -d`
2. For each model file in `src/backend/models/`, extract the full column list (including type)
   from the SQLAlchemy class definition
3. Compare against the live table schema: `docker exec <postgres-container> psql -U swa -d
   swa_erp -c '\d <table_name>'` for each table
4. Any column present in the model but missing from the live table = drift → needs a migration
   to add it
5. Any type mismatch (e.g. model says `Integer`, DB has `String`) = drift → needs a migration to
   alter it
6. For each drifted model, write ONE new migration that brings the DB in line with the model —
   don't bundle unrelated models into one migration, keep them separable like 0021/0022 did

Known candidates to check first (named in the wave-12 report, not yet verified): `Material`,
`Contact`, `ComplianceItem`. But check every model — don't assume the list is exhaustive.

### Edge cases
- If a live table has a column the model DOESN'T have, that's the opposite kind of drift
  (probably a leftover from an old migration) — flag it in the report, don't auto-drop data
  columns without asking; this is a metadata/report item unless it's obviously safe (e.g. a
  duplicate index)

## Acceptance criteria
- [ ] `docker-compose down -v && docker-compose up -d` then compare every model's columns
  against every live table — zero drift remaining, documented in the report
- [ ] `python3 -m pytest tests/ -q` — full suite still passes (these bugs weren't caught by
  tests before, so passing tests alone doesn't prove the fix — the acceptance criterion is the
  live-schema diff, not just green tests)
- [ ] Hit at least one endpoint per newly-fixed model against the live docker stack (e.g. if
  `Material` had drift, `GET /api/materials` should return 200, not 500)
- [ ] `alembic -c src/backend/alembic.ini heads` — document the resulting head count; don't need
  to merge them in this task, just don't make the fan-out worse than necessary

## How to deliver
1. Run the systematic sweep above against every model
2. Write and apply migrations for every drifted model found
3. Verify against the live stack, not just unit tests
4. Write report to `work/reports/wave-16/01-model-migration-drift-sweep.report.md` — list every
   model checked, which had drift, which didn't, and the migration file for each fix
5. Stop

## Constraints
- Time budget: 90 min
- Migrations only add/alter columns to match models — don't restructure tables beyond what's
  needed to close the drift
- Allowed tools: file edit, docker, docker-compose, psql, alembic, pytest, curl
