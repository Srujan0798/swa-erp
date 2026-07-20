# Wave-9 / Wave-10 / Wave-11 — consolidated completion + gate-clear for Wave-12

## Status

| Wave | Task | Report | Result |
|------|------|--------|--------|
| wave-9 | 00 — shared reference-ID generator | `work/reports/wave-9/00-shared-id-generator.report.md` | DONE |
| wave-9 | 01 — Inquiry + Agreement API | `work/reports/wave-9/01-inquiry-agreement-api.report.md` | DONE |
| wave-9 | 02 — Token API | `work/reports/wave-9/02-token-api.report.md` | DONE |
| wave-9 | 03 — Document reference API | `work/reports/wave-9/03-document-reference-api.report.md` | DONE |
| wave-9 | 04 — Chain frontend | `work/reports/wave-9/04-chain-frontend.report.md` | DONE (note: see Vitest caveat below) |
| wave-10 | 01 — Sustainability metrics | `work/reports/wave-10/01-sustainability-metrics.report.md` | DONE |
| wave-11 | 01 — Reconcile dangling frontend | `work/reports/wave-11/01-reconcile-dangling-frontend.report.md` | NO-OP (already merged in `4e0655d`) |

**Gate for wave-12 is satisfied.** Independent verification (`work/wave-12/01-independent-verification.md`) is now unblocked.

## Independent verification I ran from this session

### Backend tests
```
python3 -m pytest tests/wave-7 tests/wave-8 tests/wave-9 tests/wave-10 -q --timeout=60
→ 151 passed, 32 warnings in 109.21s
```

- All 151 backend tests pass across wave-7, wave-8, wave-9 (00–03), and wave-10.
- 0 regressions vs the pre-wave-9 baseline (wave-7 still 42/42, wave-8 still 26/26 when those are isolated).
- 32 warnings are all the pre-existing `datetime.utcnow()` deprecation in soft-delete helpers across the repo (not introduced by this wave's work).

### Backend lint
```
python3 -m ruff check <all wave-9 / wave-10 new files>
→ All checks passed!
```
Repo-wide ruff reports 146 pre-existing issues (B008 default-arg calls, F401 re-exports, I001, UP006/045). None were introduced by wave-9/10/11 work; the per-file check on the deliverables is clean.

### Frontend
```
cd src/frontend && npx tsc --noEmit       → TSC EXIT 0
cd src/frontend && npx eslint . --ext ts,tsx --max-warnings 0  → ESLINT EXIT 0
cd src/frontend && npx vite build         → ✓ built in 4.64s
```

### Model / route inventory (sanity)
All wave-9/10 new tables present in `Base.metadata`:
- `reference_counters` (wave-9 / 00)
- `inquiries`, `service_agreements` (wave-9 / 01)
- `tokens` (wave-9 / 02)
- `document_references` (wave-9 / 03)
- `sustainability_metrics` (wave-10 / 01 — already in `0018` from prior session)

All wave-9/10 routes mounted in `app`:
- `/api/inquiries` (+ `/{id}/convert`)
- `/api/service-agreements`
- `/api/tokens`
- `/api/document-references`
- `/api/projects/{id}/sustainability/metrics`

## Known caveats the wave-12 verifier should know about

1. **Vitest is not installed in `src/frontend/package.json`.** Wave-9 / 04 (chain frontend) added `useInquiries.test.ts` (and 3 more hooks tests) following the `useTasks.test.ts` pattern, but they cannot run until `vitest` + `@testing-library/react` are added to devDependencies. TypeScript / ESLint / build all pass; the test files are valid but un-executed. This is a project-wide pre-existing gap, not specific to this wave.
2. **Pre-existing alembic oddity.** `alembic -c src/backend/alembic.ini upgrade <rev>` against a fresh test schema can print `Can't locate revision identified by '0014_project_tracking'` even though `ScriptDirectory.get_revision("0014")` finds the file. The pytest path uses `Base.metadata.create_all` (see `tests/conftest.py`) and works fine. Recorded in wave-9 / 00 and wave-9 / 01 reports.
3. **Multiple alembic heads.** Pre-existing in this repo (0006, 0008, 0009, 0010, 0011, 0013, 0015, 0017, 0018, 0019, 0020). Wave-9/10 migrations extend the chain correctly. Recorded in wave-9 / 00 report.
4. **Wave-9 / 02 used migration `0019` instead of the brief's `0018`.** Brief said `0018` but `0018` was already taken by the pre-existing `sustainability_metrics` migration; subagent used `0019` and chained it from `0018`. Recorded in wave-9 / 02 report.
5. **Wave-9 / 03 used migration `0020` instead of the brief's `0019`.** Same reason: `0019` taken by wave-9 / 02 tokens. Recorded in wave-9 / 03 report.
6. **Wave-10 / 01 was largely already on disk** from a prior session. Subagent added one missing piece: a `SustainabilityManager` tab on `ProjectDetailPage.tsx`, and cleaned two pre-existing lint nits (`import pytest` in the test file, `__all__` sort order in `api/__init__.py`).
7. **Wave-11 / 01 was a no-op** — the 16 files listed in the brief were already committed in `4e0655d` "feat(wave-11): finish and commit dangling frontend work". Subagent overwrote the stale NO-OP report with this explanation.

## How the dispatch happened

Per the user's request, all 6 subagents ran in parallel in two waves of 3 (and a retry for the one that errored):

| Pass | Subagent | Wave / Task | Subagent task_id |
|------|----------|-------------|------------------|
| 1 | A | wave-9 / 01 | `ses_0810517fbffeMup3JVkBaO0yoL` |
| 1 | B | wave-9 / 02 | `ses_0810178c1ffe4JTkgw8O3lFhHS` |
| 2 | C | wave-9 / 03 | `ses_080f65d15ffe46yCYc5nPf98FC` |
| 2 | D | wave-9 / 04 | `ses_080e2a6bfffey0YRFNnwtCai7V` |
| 2 | E | wave-10 / 01 | `ses_080daf20cffeyjjADUdiMLxfNq` (errored) → retried as `ses_080d8972affel1GTLzlLIKxtPM` |
| 2 | F | wave-11 / 01 | `ses_080dac566ffeM9v7OcxEULK3bW` |

Each subagent received the same worker protocol (read `work/WORKER_PROMPT.md`, read the exact task brief, run acceptance commands, write the report to the brief's specified path, stop) plus a one-paragraph heads-up about already-on-disk work, the shared `reference_id_service` from wave-9 / 00, the pre-existing alembic oddity, and the migration-id collision with `0018`.

## Time / tokens / model
~10 min orchestrator (this synthesis + 6 subagent dispatches) + 6 subagent runs in parallel / minimal orchestrator tokens, subagent tokens not tracked here / minimax-m3.
