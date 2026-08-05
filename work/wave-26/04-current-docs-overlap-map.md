# Wave-26 Task 04 — Overlap/duplication map of ALL current docs

**Read `work/wave-26/00-EXTRACTION-SCHEMA.md` first.** You edit NOTHING except your own report.

## Scope — every *current* (non-archived) markdown doc in the repo
Root: `README.md`, `CLAUDE.md`, `KIMI.md`, `HANDOFF.md`, `HANDOFF_FINAL.md`, `HIERARCHY.md`,
`HOW_TO_RUN.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `OS_SETUP.md`, `wave9handoff.md`,
`wave10handoff.md`
Plus: `plan/*.md`, `docs/*.md`, `docs/decisions/*.md`, `resources/*.md`,
`deliverables/handover/*.md`, `orchestrator/**/*.md`, `.specify/*.md`
Excluded: anything under `docs/historical/` (tasks 02 and 03 own that)

## Why this task exists
The other three wave-26 tasks extract content from *historical* material. This task maps the
*current* material — because the Phase 2 consolidation can't be planned until we know exactly
which current docs overlap, contradict, or duplicate each other.

Known problem cases to pay special attention to (all confirmed, not hypothetical):
- `CLAUDE.md` and `KIMI.md` are believed to be **byte-identical duplicates** (same size, 3847
  bytes) — verify with `diff` and say definitively. If they are identical, that's a maintenance
  trap: an edit to one silently diverges from the other.
- `HANDOFF.md`, `HANDOFF_FINAL.md`, `wave9handoff.md`, `wave10handoff.md` are **four documents
  all claiming to be the handoff**, with different and conflicting status claims.
- `OS_SETUP.md` is 48KB — the single largest doc in the repo. Determine what it actually is
  (it appears to be a generic project-template/methodology doc, not swa-erp-specific) and
  whether it still earns a place in a repo being handed to a client.
- `docs/deployment.md` vs `docs/DEPLOYMENT_CHECKLIST.md` vs `docker-compose.prod.yml` comments —
  three places describing deployment.
- `docs/SCOPE_GUARD.md` vs `orchestrator/core/scope-guard.md` — two scope documents.
- `deliverables/handover/*` (4 client-facing docs) vs the internal docs they were derived from.

## What to produce
A **complete overlap matrix**: for each topic the docs cover (project status, architecture,
deployment, scope, meeting requirements, how-to-run, conventions, history, handover), list every
doc that covers it and mark which one should be canonical.

For each doc also determine: **who is the audience?** (orchestrator / worker agents / future
developer / the client / nobody-anymore). A doc with no live audience is a deletion candidate.
This audience question is the key input to Phase 2 — a client-facing handover doc and an
internal orchestrator process doc have completely different retention rules.

## Specific deliverable beyond the standard schema
In addition to sections 1-8, add:

```markdown
## 9. PROPOSED CANONICAL SET
The minimum set of docs that should survive Phase 2, each with its single clear purpose and
audience, and what gets merged into it.
| Canonical doc | Audience | Purpose | Absorbs (list of files) |

## 10. PROPOSED DELETION / ARCHIVE LIST
| File | Action | Why | What must be extracted first |
```

Be genuinely opinionated here — a vague map is useless. The orchestrator will merge your
proposal with the other three reports and make final calls, so give a real recommendation, not
a menu of options.

## Deliver
Report to `work/reports/wave-26/04-current-docs-overlap-map.report.md`. Then STOP.

## Constraints
- Time budget: 75 min
- Edit nothing but your report — especially do not "helpfully" delete the duplicate you find
- Use `diff` to prove duplication claims rather than eyeballing
- Allowed tools: read, grep, diff, git (read-only)
