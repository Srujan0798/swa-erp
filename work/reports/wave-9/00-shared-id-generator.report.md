# Report — 00-shared-id-generator

## Result
DONE

## What I did
- Created `src/backend/models/reference_counter.py` (18 lines) — `ReferenceCounter` model keyed by `(entity_type, year)` with `last_seq` and a unique constraint
- Created `src/backend/services/reference_id_service.py` (40 lines) — `generate_reference_id(db, entity_type)` using a single-statement `INSERT ... ON CONFLICT (entity_type, year) DO UPDATE SET last_seq = reference_counters.last_seq + 1 RETURNING last_seq`, plus a `get_current_seq` helper
- Created `src/backend/alembic/versions/0015_add_reference_counters.py` (38 lines) — wires into the existing chain (`down_revision = "0014"`); the existing 0018 sustainability migration already declares `down_revision = "0015"`, so the chain is consistent
- Created `tests/wave-9/test_reference_id_service.py` (115 lines) — 10 tests covering: basic generation, monotonic increment, format, isolation between types, year keying, and a 50-thread concurrency test that asserts gapless, unique, sequential IDs (`TKN-001..TKN-050`)
- Modified `src/backend/models/__init__.py` — exported `ReferenceCounter` so it is registered with `Base.metadata` via the existing `import src.backend.models` in `tests/conftest.py` and `src/backend/alembic/env.py`

## Acceptance checks
- [x] `python3 -m pytest tests/wave-9/test_reference_id_service.py -q` — passed (10/10 in ~1.1s, evidence below)
- [x] 50 parallel calls for `entity_type="TKN"` produce exactly 50 distinct IDs, `TKN-001..TKN-050`, no gaps or dupes — passed (`TestConcurrency::test_50_parallel_calls_yield_gapless_sequential_ids` asserts `len(set(ids)) == 50` and `seqs == list(range(1, 51))` and `get_current_seq("TKN") == 50`)
- [x] Calling with two different `entity_type`s never collides or shares a counter — passed (`TestIsolationBetweenEntityTypes::test_two_types_have_independent_counters` and `test_counter_never_collides_across_types`)

## Decisions I made
- Chose the single-statement `INSERT ... ON CONFLICT (entity_type, year) DO UPDATE SET last_seq = reference_counters.last_seq + 1 RETURNING last_seq` approach over `SELECT ... FOR UPDATE` + manual insert because it is atomic in one round-trip and provably race-safe (PostgreSQL locks the conflict-target row during the upsert, so concurrent calls serialize on the row). The 50-thread test confirms no gaps and no dupes.
- Generated the row's UUID in Python (`uuid.uuid4()`) and passed it as a parameter rather than calling `gen_random_uuid()` in SQL, because the project DB does not have the `pgcrypto` or `uuid-ossp` extension enabled. This avoids a migration-time `CREATE EXTENSION` dependency.
- Year is part of the composite key, matching the design inference in `docs/decisions/0002-core-id-chain-gap.md` item #2. Dropping the year later is a one-line change in the lookup key (as the brief notes).
- Did NOT retrofit Client/Project here — the brief says this is the shared service for downstream tasks (01, 02, 03, 04) to use. Retrofits of existing entities belong with whoever adds new fields to those entities.

## Tests run
- `python3 -m pytest tests/wave-9/test_reference_id_service.py -q` → `10 passed in 1.10s`
- `python3 -m pytest tests/wave-9 -q` → `10 passed in 2.70s`
- `python3 -m pytest tests/wave-7 tests/wave-8 -q` → `68 passed` (regression check; nothing broken)
- `python3 -m ruff check src/backend/models/reference_counter.py src/backend/services/reference_id_service.py src/backend/alembic/versions/0015_add_reference_counters.py tests/wave-9/test_reference_id_service.py` → `All checks passed!`
- `alembic -c src/backend/alembic.ini heads` → confirms 0015 sits in the chain between 0014 and 0018; the chain is consistent (no new branches introduced)

## Issues / blockers
One non-obvious test-design gotcha worth recording so tasks 01-03 don't repeat it:
- The `db_session` fixture in `tests/conftest.py` holds a SQLAlchemy session open for the duration of the test. For the 50-thread concurrency test, this means the parent session occupies a pool slot while 50 worker threads each open their own session from the same engine. When pytest teardown runs the session-scoped `setup_test_db` fixture's `DROP SCHEMA public CASCADE`, the leftover pool connections deadlock against the DROP.
- Fix applied: the concurrency test does not request `db_session`; it opens its own sessions via `TestingSessionLocal()` and closes them deterministically. The non-concurrency tests in the same file use `db_session` and pass cleanly.
- Implication for downstream tasks: any test that fans out N sessions for parallelism should avoid simultaneously holding the function-scoped `db_session` open. Open and close all sessions inside the test body.

## Recommended next task
Task 01 (Inquiry + Agreement API) can now start. It will need:
- `from src.backend.services.reference_id_service import generate_reference_id`
- Call `generate_reference_id(db, "INQ")` when creating an Inquiry
- Call `generate_reference_id(db, "SA")` when creating a ServiceAgreement
- The format `SWA-{year}-{TYPE}-{seq:03d}` is the contract — store it in the entity's `reference_id` (or similar) field; the schema work for that is the task's responsibility, not this one's.

## Time / tokens / model
~25 min / minimal / minimax-m3
