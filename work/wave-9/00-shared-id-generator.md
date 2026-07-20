# Task 00 — Shared reference-ID generator (do this FIRST, everything else depends on it)

## What to do
Build one shared service that generates `SWA-{year}-{TYPE}-{seq:03d}` reference IDs, backed by
an atomic per-type-per-year counter. Every entity in wave-9 (Inquiry, ServiceAgreement, Token)
and the retrofit to Client/Project uses this — build it once, correctly, before the other tasks
start, so nobody reinvents numbering.

Evidence this is the real scheme (not guessed): actual sample IDs found in
`resources/ERP_Sheets_Extracted/ERP Sheets/*.xlsx`: `SWA-2025-INQ-001` (Inquiry),
`SWA-2025-CLT-001` (Client), `SWA-2025-SA-011` (Service Agreement), `SWA-2025-TKN-001` (Token),
`SWA-2025-EMP-001` (Employee). See `docs/decisions/0002-core-id-chain-gap.md` item #1.

## Files to create
- CREATE: `src/backend/models/reference_counter.py` — one row per `(entity_type, year)`, locked row for atomic increment
- CREATE: `src/backend/services/reference_id_service.py` — `generate_reference_id(db, entity_type: str) -> str`
- CREATE: `src/backend/alembic/versions/0015_add_reference_counters.py`
- CREATE: `tests/wave-9/test_reference_id_service.py` — MUST include a concurrency test: N
  parallel calls for the same `entity_type` produce N distinct, gapless, sequential IDs

## Files to modify
- MODIFY: `src/backend/models/__init__.py`

## The core problem (inline)

### Counter model
```python
class ReferenceCounter(Base):
    __tablename__ = "reference_counters"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "INQ", "CLT", "SA", "TKN", etc
    year: Mapped[int] = mapped_column(nullable=False)
    last_seq: Mapped[int] = mapped_column(nullable=False, default=0)
    __table_args__ = (UniqueConstraint("entity_type", "year", name="uq_refcounter_type_year"),)
```

### Service — must be race-safe
```python
def generate_reference_id(db: Session, entity_type: str) -> str:
    year = datetime.utcnow().year
    # SELECT ... FOR UPDATE on the (entity_type, year) row (create it if missing, still under lock)
    # increment last_seq, commit, return f"SWA-{year}-{entity_type}-{seq:03d}"
```
Use `SELECT ... FOR UPDATE` (row lock) inside the same transaction as the increment — do not
read-then-write without a lock, it will produce duplicate IDs under concurrent requests. If the
row for `(entity_type, year)` doesn't exist yet, insert it inside the same locked transaction
(handle the race on first-ever creation with `ON CONFLICT DO NOTHING` + retry, or an
`INSERT ... ON CONFLICT (entity_type, year) DO UPDATE SET last_seq = reference_counters.last_seq + 1 RETURNING last_seq`
single-statement approach, which is the cleanest fix for the race).

Year-reset behavior (counter keyed by year, resets to 1 each Jan 1) is a design inference — see
ADR-0002 open item #2. Keep it config-shaped (the year is just part of the lookup key) so
switching to "continuous forever" later is a one-line change (drop `year` from the key), not a
rewrite.

## Acceptance criteria
- [ ] `python3 -m pytest tests/wave-9/test_reference_id_service.py -q` passes, concurrency test included
- [ ] 50 parallel calls for `entity_type="TKN"` produce exactly 50 distinct IDs, `TKN-001..TKN-050`, no gaps or dupes
- [ ] Calling with two different `entity_type`s never collides or shares a counter

## How to deliver
1. Implement model + migration + service + concurrency test
2. Run acceptance commands
3. Write report to `work/reports/wave-9/00-shared-id-generator.report.md`
4. Stop — tasks 01-03 depend on this merging first

## Constraints
- Time budget: 60 min
- This MUST land before tasks 01, 02, 03 start — it's a hard dependency, not a suggestion
- Allowed tools: file edit, pytest, ruff
