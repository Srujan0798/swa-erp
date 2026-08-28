# Wave-49 Task 01 — CRITICAL: orphaned rows possible in the core Inquiry→Client→Project chain

**This is the highest-priority finding of the whole audit.** It affects the exact workflow the client described as their core ask (Inquiry → Client → Agreement → Token → Document Reference).

## The bug, verified

`src/backend/db/session.py`'s `get_db()` has no `rollback()` on exception and no single commit-per-request:
```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
**21 of 25 repository files call `db.commit()` independently** inside their own functions (verified: `grep -c "\.commit()" src/backend/db/repositories/*.py` → 21 files with ≥1 hit).

`convert_inquiry()` in `src/backend/services/inquiry_service.py` calls, in sequence:
1. `_create_client_from_inquiry()` → `client_repo.create()` → **commits**
2. `_create_project_from_inquiry()` → `project_repo.create_project()` → **commits**
3. `audit_repo.create_entry()` → likely commits too

**If step 2 or 3 raises** (a validation error, a DB constraint, a race on a unique reference ID), **step 1's client row is already permanently committed.** The result: a Client with no Project, no Agreement, nothing — an orphan the user has to notice and manually clean up, with no automatic rollback, no error recovery, and (per the wave-48 audit) no audit-log entry to explain how it got there.

This is exactly the failure mode ADAPTOID-LITE.md's FM-11 (silent failures / no error recovery) warns about, on the single most important flow in the product.

## Files you own
- `src/backend/db/session.py`
- `src/backend/services/inquiry_service.py` (the proof-of-concept fix)
- `tests/wave-49/test_inquiry_conversion_atomicity.py` (new)

## The work

### 1. Fix `get_db()` to commit-once / rollback-on-exception
```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```
This alone does NOT fully fix the bug — the 21 repos still call `db.commit()` mid-request, which flushes each step to the DB permanently regardless of what happens later in the same request. The request-level commit/rollback wrapper only helps requests where NO repo-level commit happened yet.

### 2. Remove the premature commits from the core-chain repos, minimum viable fix
You do not need to touch all 21 repos in this wave — that's real but broader surgery. Fix the ones in the actual Inquiry→Client→Project path: `client_repo.py`, `project_repo.py`, and whatever `audit_repo.create_entry` does. Change their `db.commit()` calls to `db.flush()` (keeps the row visible within the same transaction for subsequent FK references, without permanently committing). Let the new `get_db()` wrapper own the actual commit.

**Verify nothing else in the request path relied on the mid-request commit being durable** (e.g. a background task reading the DB from a separate connection mid-request) — check before changing, don't assume.

### 3. Prove it with a real test
Write `tests/wave-49/test_inquiry_conversion_atomicity.py`: call `convert_inquiry()` with inputs engineered so client-creation succeeds and project-creation deliberately fails (e.g. mock/monkeypatch `project_repo.create_project` to raise). Assert **the client row does NOT exist afterward** — i.e., the whole conversion rolled back atomically. This is the acceptance proof, not a description.

### 4. Document the remaining 18+ repos as backlog
List every repo still doing mid-function commits in `BACKLOG.md` (if wave-40 has landed and created it) or in your report — this wave fixes the highest-value path, not all of them. State plainly what remains at risk.

## Acceptance criteria
- [ ] The new atomicity test fails on the OLD code (prove it — run against a stash/revert of your fix first) and passes after the fix
- [ ] `python3 -m pytest tests/wave-49/ tests/wave-9/test_inquiries.py -v` — paste real output, all green
- [ ] Full backend suite still green (no regression from the commit→flush change)
- [ ] Report states exactly which repos were fixed and which remain at risk

## Deliver
`work/reports/wave-49/01-transaction-atomicity.report.md`. Commit before writing it.

## Constraints
- Time budget: 150 min · commit per numbered item
- Do NOT attempt all 21 repos — scope is the Inquiry→Client→Project path only, backlog the rest
- If the fix reveals other code that assumed mid-request commits are durable, STOP and report it rather than guessing
