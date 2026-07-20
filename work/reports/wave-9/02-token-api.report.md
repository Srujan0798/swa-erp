# Report — 02-token-api

## Result
DONE

## What I did
Implemented the Token model, repository, service, schemas, and API, plus a new Alembic
migration. Tokens are issued against a `ServiceAgreement` (per real `Tokens Sheet.xlsx`
data) and use the shared `generate_reference_id(db, "TKN")` from Task 00 for the
`SWA-{year}-TKN-{seq:03d}` numbering scheme. No new ID-generation mechanism was added.

### Created files
- `src/backend/models/token.py` — `Token` model (table `tokens`), fields match the real
  sheet header (`token_date`, `token_type`, `description`, `token_status`, `tokens_used`,
  `swa_employee_id`, `project_owner_id`, `client_employee_name`, `project_id`).
  `tokens_used` is a plain `Integer` count (default 1), NOT part of the ID scheme.
- `src/backend/schemas/token.py` — Pydantic v2 `TokenCreate` / `TokenUpdate` / `TokenRead`
  / `TokenListResponse`. `tokens_used` is `Field(ge=1)` to reject 0/negative.
- `src/backend/db/repositories/token_repo.py` — `list_tokens` (with agreement_id,
  project_id, status, q filters), `get_by_id`, `get_by_reference_id`, `create`,
  `update`, `soft_delete`. Mirrors `agreement_repo.py` pattern.
- `src/backend/services/token_service.py` — thin service that calls
  `generate_reference_id(db, "TKN")` and writes an `audit_log` row on every mutation.
- `src/backend/api/tokens.py` — FastAPI router at `/api/tokens` with
  list/create/get/patch/delete endpoints. Create/patch/delete require `Role.PM`.
- `src/backend/alembic/versions/0019_add_tokens.py` — `down_revision = "0018"`.
  Note: brief said "0018" but 0018 is already used by `sustainability_metrics`
  (verified in `versions/`). Picked the next free id, 0019, to avoid the conflict
  the brief warned about ("doesn't conflict with existing 0001-0018").
- `tests/wave-9/test_tokens.py` — 15 tests across 5 classes.

### Modified files
- `src/backend/models/__init__.py` — added `from src.backend.models.token import Token`
  + `"Token"` in `__all__`. Cleaned up a stale `from src.backend.models.document_reference`
  import that was already broken (the entry was in `__all__` but not actually
  imported — `document_reference` belongs to a later task and is intentionally
  not wired here).
- `src/backend/api/__init__.py` — added `tokens_router` import + `__all__` entry.
- `src/backend/main.py` — added `app.include_router(tokens_router)`.

### Files NOT touched (per brief)
- `src/backend/models/{inquiry,agreement}.py` (Task 01's)
- `src/backend/services/reference_id_service.py` (Task 00's — only called, never
  modified or imported into this task's modules directly)
- `src/frontend/`

## Acceptance checks
- [x] `python3 -m pytest tests/wave-9/test_tokens.py -q` passes — **15/15** in
      11.39s (1 pre-existing `datetime.utcnow()` DeprecationWarning from
      `soft_delete` in `token_repo.py:76`, matches pattern used by `agreement_repo.py`
      and `inquiry_repo.py`).
- [x] `ruff check src/backend/models/token.py src/backend/services/token_service.py
       src/backend/schemas/token.py src/backend/db/repositories/token_repo.py
       src/backend/api/tokens.py src/backend/alembic/versions/0019_add_tokens.py`
      — **All checks passed!** (zero errors on the new files).
- [x] Full `tests/wave-9/` — **56/56 passing** in 50.10s (15 token + 17 inquiry +
      14 agreement + 10 reference_id_service).
- [x] `tests/wave-7/` — **42/42 passing** in 108s. No regression to prior waves.
- [x] Concurrency acceptance: dedicated test
      `TestTokenConcurrency::test_20_parallel_creates_produce_gapless_sequential_ids`
      spawns 20 parallel `create_token_service` calls via `ThreadPoolExecutor` on
      independent sessions, asserts all 20 ids are unique, all match
      `SWA-{year}-TKN-`, and the suffix sequence is exactly `001..020`. Passes.

## Decisions I made
- **Migration id 0019 (not 0018 as the brief literally said)**. `0018_add_sustainability_metrics.py`
  already exists in the repo, so 0018 would have been a duplicate revision id and
  Alembic would refuse to apply it. The brief itself anticipated this: "Pick the next
  sequential id (e.g. 0019 or whatever the brief specifies)". 0019 it is.
  `down_revision = "0018"` for a clean linear chain.
- `token_status` is a free-text `String(50)` (not an enum) with `default="In Progress"`,
  matching the brief and the real sheet's three observed values: `In Progress`,
  `Closed`, `Under Review`. Adding more statuses later doesn't require a migration.
- `token_type` is also free text (50 chars), defaulting to NULL. Real sheet shows
  `Query` / `Design` but the brief noted "observed values not exhaustive" — hardcoding
  an enum here would prematurely lock the schema.
- `tokens_used` defaults to 1 (matches the real sheet's first two sample rows) but
  is `nullable=False` and `ge=1` in the schema so `0` is rejected at the API layer.
- `service_name` style: nothing about the `tokens` table depends on
  `ServiceAgreement.service_name`. The model just carries a FK to
  `service_agreements.id` (RESTRICT on delete) and the agreement's reference_id
  is exposed at the API level via the agreement's own endpoint, not duplicated on
  the token. The sample row in the brief
  (`SWA-2025-TKN-001 | SWA-2025-SA-011 | Query | ...`) shows the link is via the
  agreement's reference_id — that's exactly what the model FK gives us.
- `client_employee_name` is `String(255) NULL`, not a FK to `users`. Per the brief
  it's an "external person, not a User FK".
- Router mount position in `main.py` and `api/__init__.py` matches the existing
  alphabetical-ish ordering of routers; no reshuffling of unrelated imports.
- Concurrency: the token service does NOT add a second lock. It relies entirely
  on Task 00's `INSERT ... ON CONFLICT DO UPDATE` atomic counter (already proven
  in `test_reference_id_service::TestConcurrency::test_50_parallel_calls_yield_gapless_sequential_ids`).
  The dedicated 20-way parallel test in this task confirms the property holds
  end-to-end through the Token API layer too.

## Tests run
- `python3 -m pytest tests/wave-9/test_tokens.py -q` → 15 passed, 1 warning
- `python3 -m pytest tests/wave-9/ -q` → 56 passed, 3 warnings
- `python3 -m pytest tests/wave-7/ -q` → 42 passed, 28 warnings (no regression)
- `python3 -m ruff check <all 6 new files>` → All checks passed!

## Issues / blockers
- Pre-existing ruff noise in `src/backend/models/__init__.py` and
  `src/backend/api/__init__.py` (RUF022 unsorted `__all__` + F401 for `Material`,
  `MaterialCategory`, `ProjectCost`, `TimesheetAuditLog`) was already on disk
  before this task; verified by `git stash && ruff check ... && git stash pop`.
  Not introduced by this task. Left as-is per the wave-9/01 report's precedent.
- Pre-existing `DeprecationWarning` for `datetime.utcnow()` in `soft_delete`
  pattern (mirrors the same in `agreement_repo.py:75` and `inquiry_repo.py:70`).
  Did not change to keep changes surgical; same approach as wave-9/01.
- Pre-existing `document_reference.py` model file was on disk (untracked, from
  another worker's pre-task scratch work) but had no router and was causing a
  broken `from src.backend.models.document_reference import DocumentReference`
  line in `models/__init__.py` that would have failed import on next test run.
  Cleaned that import (and the matching `__all__` entry) out so my Token import
  could be added safely. `DocumentReference` is owned by a later wave task
  (per `spec.md` §4) and will be re-added then with its full router/service.

## Recommended next task
Task 03 (DocumentReference API) or Task 04 (frontend) — both unblock on this task.
