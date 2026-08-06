# Wave-28 Task 01 — Execute the documentation consolidation (wave-26 Phase 2)

## What to do
Execute the consolidation that wave-26's four extraction reports concluded. **Every action below
is backed by a specific finding** — read `work/reports/wave-26/*.report.md` first, especially
report 01 §7 and report 04 §9/§10, so you understand why each move was decided.

This is the "delete/merge/archive" phase. Wave-26 deliberately forbade any file changes; this
task is where they happen.

## Governing rule from CLAUDE.md — ARCHIVE, DON'T DELETE
This project's kernel says: *"Don't delete — archive."* Old plans → `docs/historical/`, failed
experiments → `attic/`. Follow that. The only true deletions permitted here are (a) an empty
directory and (b) a byte-identical duplicate being replaced by a symlink. Everything else moves.

Use `git mv` for every move so history is preserved.

## The work — 6 items

### 1. Extract wave9handoff.md §8 BEFORE archiving it (do this first — it's the only unique content)
Report 01 found `wave9handoff.md` §8 contains architectural conventions that exist in **no**
canonical doc and would cost a future engineer hours to rediscover. Extract these into
`docs/conventions.md` (they are conventions, that's the right home):
- Backend **service** convention: one function per operation, takes `db: Session` +
  `actor_id: uuid.UUID`, returns an ORM model or raises a typed exception
- Backend **repository** convention: `<entity>_repo.py` exposing `list_*`, `get_by_id`,
  `create`, `update`, `soft_delete`, with soft-delete via a `deleted_at` column
- **Reference-ID service**: `generate_reference_id(db: Session, entity_type: str) -> str`
  returning `SWA-{year}-{TYPE}-{seq:03d}`; entity codes in use: `SA`, `INQ`, `CLT`, `TKN`, plus
  document counter keys. Note ADR-0002 documents a different, db-less signature — **the code is
  authoritative**, so correct ADR-0002's signature to match reality while you're there.
- **Alembic**: revisions are zero-padded 4-digit (`0001`…`0025`), one migration per concern,
  always create with `--rev-id=NNNN_descriptive_name`

Also add to `docs/PROJECT_HISTORY.md` (it's a gotcha, that's its home):
- **The auth rate-limiter test-suite trap**: the limiter allows 5 logins/min/IP; the whole suite
  shares one IP; `tests/conftest.py` must set `DISABLE_AUTH_RATE_LIMIT=1` *before* importing the
  app. Symptom is mass `KeyError: 'access_token'` across unrelated modules — the same
  "looks-like-everything-is-broken" signature as the Postgres ENUM/fixture bug already recorded
  there. Reference commit `3e0f137`.

### 2. Extract the undocumented gotchas found in the session exports
Report 03 found these in the 122MB of session prose, present in no canonical doc. Verify each
against the current code first (some may already be fixed — if so, record it as history, not as
an open bug), then add the ones that represent real, recurring traps to
`docs/PROJECT_HISTORY.md`:
- `invoice.py` `date`/`Date` import collision bug
- BOQ RBAC bug
- `.join("boq")` path-construction bug
- `conftest.py` overwrite hazard
- `datetime not JSON serializable` in export paths

Keep these terse — one line each, stating the trap and how to avoid it. If verification shows one
was a one-off already fixed and unlikely to recur, say so in your report and skip it rather than
padding the history file.

### 3. Archive the 3 root handoffs
```
git mv HANDOFF_FINAL.md  docs/historical/HANDOFF_FINAL-superseded.md
git mv wave9handoff.md   docs/historical/wave9handoff-superseded.md
git mv wave10handoff.md  docs/historical/wave10handoff-superseded.md
```
Only after item 1 has extracted wave9handoff's §8. Then **remove their three
PENDING CONSOLIDATION entries from `HIERARCHY.md`** (both the table rows and the bullet-list
entries — the Adaptoid FM-08 validator reads the bullets).

### 4. Kill the CLAUDE.md / KIMI.md duplication
Verified byte-identical (`diff` returns nothing). Two identical files is a divergence trap — edit
one, the other silently goes stale. Replace `KIMI.md` with a symlink to `CLAUDE.md`:
```
git rm KIMI.md && ln -s CLAUDE.md KIMI.md && git add KIMI.md
```
Verify git stores it as a symlink (mode `120000` in `git ls-files -s KIMI.md`).
**If symlinks turn out to be a problem** (Windows Server is the deployment target and the client
may clone there), fall back to: keep `KIMI.md` as a 3-line stub that says "This project's kernel
is `CLAUDE.md` — Kimi and Claude read the identical file; see CLAUDE.md." Choose one, state which
and why in your report.

### 5. Remove OS_SETUP.md from the repo
48KB generic agentic-project template. Not swa-erp-specific, wrong audience for a repo being
handed to a client, and report 04 confirms a copy exists outside the repo at
`~/Desktop/OS_SETUP.md`. Per the archive-don't-delete rule: `git mv OS_SETUP.md attic/OS_SETUP.md`
(create `attic/` if absent). Then remove its references from `HIERARCHY.md`, `README.md`, and
`orchestrator/core/identity.md` — **check each reference and rewrite the sentence** so it still
reads correctly; don't leave dangling mentions.

### 6. De-duplicate ADR-0003
`docs/decisions/0003-it-server-call-brief.md` embeds a full copy of the IT brief (roughly lines
84-251) that also lives in `docs/IT_BRIEF.md`. One artifact in two files will drift — it already
did once with the RS256 claim. Strip the embedded copy from the ADR and replace it with a pointer
to `docs/IT_BRIEF.md`. Keep the ADR's own reasoning (why each of the 8 questions is being asked)
— that part is genuinely ADR content and is not duplicated.

## Acceptance criteria
- [ ] `docs/conventions.md` contains all 4 architectural conventions from item 1
- [ ] ADR-0002's `generate_reference_id` signature matches the real code
- [ ] `docs/PROJECT_HISTORY.md` contains the rate-limiter trap + verified gotchas from item 2
- [ ] Repo root has no `HANDOFF_FINAL.md`, `wave9handoff.md`, `wave10handoff.md`, `OS_SETUP.md`
- [ ] `HIERARCHY.md` no longer lists them (bullets AND table) and has no dangling OS_SETUP refs
- [ ] `grep -rn "OS_SETUP" --include="*.md" .` returns only `attic/` hits
- [ ] ADR-0003 contains no duplicated brief text, only a pointer + its own reasoning
- [ ] `git log --follow` works on each archived file (proves `git mv`, not delete+create)
- [ ] Pre-commit preflight PASSES (`git commit` runs Adaptoid — FM-08 scope check must be green)
- [ ] `python3 -m pytest tests/ -q` → **344 passed minimum** (this task shouldn't touch code, so
  any change here is a regression you introduced)

## How to deliver
1. Do items 1 and 2 (extraction) BEFORE items 3-6 (moves) — order matters, you cannot extract
   from a file after you've moved it
2. Run every acceptance check
3. Report to `work/reports/wave-28/01-execute-doc-consolidation.report.md` listing every file
   moved/changed and confirming nothing was lost
4. Stop

## Constraints
- Time budget: 100 min
- `git mv` for every move — never delete-and-recreate, it destroys history
- If any extraction target turns out to already exist in the canonical doc, say so and skip it
  rather than duplicating
- Allowed tools: file edit, git, grep, diff, pytest
