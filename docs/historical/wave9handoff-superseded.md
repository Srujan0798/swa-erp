FULL HANDOFF — swa-erp ERP project, all 25 waves
0. Identity
- Repo: /Users/srujansai/Desktop/swa-erp
- Project: Internal ERP for SWA Consultancy (Ahmedabad-based insulation engineering)
- Stack: Python 3.11, FastAPI, SQLAlchemy 2, Pydantic v2, PostgreSQL 16, Redis, Celery / React 18, Vite, TypeScript, Tailwind, shadcn/ui, TanStack Query
- Test infra: pytest + httpx ASGITransport (backend), Vitest + React Testing Library (frontend, partially wired), Playwright (E2E in tests/e2e/)
- Docker: colima engine, full stack in docker-compose.yml
1. Git state (HEAD = 45bff7f, working tree clean)
45bff7f wip: pre-migration snapshot
2ca65e6 docs: commit the preflight fixes that were left uncommitted
6b4ed57 ci: run Adaptoid validators as an external authority
9e92626 fix: replace deprecated datetime.utcnow() with timezone-aware datetime.now(timezone.utc)
2073c36 fix(wave-18): security hardening (SECRET_KEY validator, auth rate limit) + invoice GST
5ec8582 chore: full root/folder sweep — mcp.json portability bug, dead venv, waves 22-24, docs truth pass
bc113e6 docs: fix 3-way contradiction on project status + reintroduced RS256 claim
6b8814f docs: fix plan/ARCHITECTURE.md — stale since kickoff, several claims were never real
4315be2 chore: waves 18-21 — production readiness + handover, none blocked on Viraj/IT
07cb017 chore: wave-17 task brief — mount the notifications router
4be7536 fix(wave-15): last E2E strict-mode fix (7/7), correct false pytest claim in report
d5b2790 fix(wave-16): model/migration drift sweep — 2 missing tables, quote.code follow-up
c433218 fix(wave-15): E2E BOQ/quote flow selectors + fix quote creation 500
ab0a786 fix(wave-14): docker-compose auto-migrate + fix backend image missing scripts/
9852ec0 fix(wave-12): independent verification — fix migration chain, model drift, docker build
... (older waves 1-13)
2. Wave status
Wave	Status	Commit	Report
1-11	SHIPPED	various	✅ in work/reports/wave-1..11/
12 (independent verification)	SHIPPED	9852ec0	✅ 324/324 pytest, 7/7 E2E, Docker healthy, 10 bugs fixed
13 (Excel importer)	SHIPPED	466d8ae	✅
14 (docker migrations + seed)	SHIPPED	ab0a786	✅
15 (E2E BOQ/quote fixes)	SHIPPED	c433218, 4be7536	✅ 7/7 E2E
16 (model/migration drift sweep)	SHIPPED	d5b2790	✅ added migrations 0023 (notifications) + 0024 (timesheet_audit_log)
17 (mount notifications router)	SHIPPED	5ec8582 (in sweep commit)	✅ in work/reports/wave-17/
18 (security hardening + GST)	SHIPPED	2073c36	✅ 339/339 pytest (15 new tests)
19 (backup + ops scripts)	SHIPPED	(in recent batch)	✅ in work/reports/wave-19/
20 (production config templates)	SHIPPED	(in recent batch)	✅ in work/reports/wave-20/
21 (handover docs)	SHIPPED	(in recent batch)	✅ in work/reports/wave-21/
22 (RBAC + auth gaps)	NOT STARTED	—	brief in work/wave-22/
23 (correctness bugs)	NOT STARTED	—	brief in work/wave-23/
24 (dead code + UI wiring)	NOT STARTED	—	brief in work/wave-24/
25	NO BRIEF YET	—	work/wave-25/ is empty
3. What's currently passing
- 339/339 backend pytest (324 baseline + 15 from wave-18 GST + security tests)
- Frontend tsc --noEmit clean
- Frontend eslint --max-warnings 0 clean
- 7/7 Playwright E2E (login flow 4, dashboard 1, BOQ/quote flow 2)
- Docker stack healthy (postgres, redis, adminer, backend, frontend all up)
- Live API smoke validated end-to-end: inquiry→agreement→token→document reference→task; auth rate-limiter returns 429 on 6th login; new invoices show GST breakdown
4. Known unresolved issues (from 2026-07-21 full-project audit)
These are tracked in work/wave-22/, work/wave-23/, work/wave-24/ task briefs (not yet executed):
- Unauthenticated materials endpoints (no require_role on materials/material-categories API)
- Zero RBAC on financial modules (project_pnl, exports) — anyone authenticated can read
- Fabricated 70%/30%-ratio financial PDF report (no real data, no real formula)
- RBAC over-restrictive: gated PM-only across core chain when client matrix requires PM+Designer (and Auditor+Designer for Reforge/DPR)
- Other correctness bugs (wave-23) and dead-code/UI-wiring cleanup (wave-24)
5. External blockers (NOT code-resolvable)
- Viraj's 3 open decisions in docs/decisions/0002-core-id-chain-gap.md:
1. Client ID scheme (existing code vs new SWA-{year}-CLT-{seq} from reference_counters)
2. Year-reset behavior (reset Jan 1 vs continuous forever)
3. First-inquiry linkage (first_inquiry_id for legacy LDI-* values)
- IT's 8 infra answers in docs/IT_BRIEF.md (already sent, awaiting response)
6. Quick start for next orchestrator
# Confirm state
cd /Users/srujansai/Desktop/swa-erp
git status              # should be clean
git log --oneline -10
ls work/reports/wave-N/ # verify reports exist
python3 -m pytest tests/ -q --timeout=120   # 339/339
cd src/frontend && npx tsc --noEmit && npx eslint . --ext ts,tsx --max-warnings 0
npx playwright test tests/e2e/ --project=chromium   # 7/7

# If you need to restart the stack
colima start
docker-compose build && docker-compose up -d
docker exec swa-erp-backend-1 alembic -c src/backend/alembic.ini upgrade heads
docker exec swa-erp-backend-1 python scripts/seed_demo.py
7. Worker dispatch protocol (for remaining waves 22-25)
Each wave brief in work/wave-N/01-*.md is self-contained. Worker gets:
1. work/WORKER_PROMPT.md (universal protocol)
2. The task brief
Report goes to the path inside the brief (usually work/reports/wave-N/01-...report.md). Do NOT have the worker commit — orchestrator batches the commit at end of round.
8. Architectural patterns to match
- Backend service pattern: src/backend/services/<entity>_service.py exposes one function per operation, takes db: Session + actor_id: uuid.UUID, returns ORM model or raises typed exception.
- API pattern: src/backend/api/<entity>.py uses Depends(get_db) + Depends(require_role(Role.X)) + HTTPException for errors. Mount in src/backend/main.py and export in src/backend/api/__init__.py.
- Repo pattern: src/backend/db/repositories/<entity>_repo.py exposes list_*, get_by_id, create, update, soft_delete. Soft-delete via deleted_at column.
- Reference IDs: generate_reference_id(db, "TYPE") from src/backend.services.reference_id_service returns SWA-{year}-{TYPE}-{seq:03d}. Already used by INQ, SA, CLT, TKN, DRAWING.
- Pydantic v2: all schemas use BaseModel, Field(...), ConfigDict(from_attributes=True) for *Read.
- Migrations: alembic revision --rev-id=NNNN_*.py (zero-padded). One file per concern.
9. Orchestrator memory
- orchestrator/memory/MEMORY.md — auto-memory shared between Claude ↔ Kimi
- HANDOFF.md — this file (updated after every merged wave)
- plan/EXECUTION.md — wave status table (must match reality)
- docs/decisions/ — ADRs in chronological order (most recent first)
- docs/decisions/0002-core-id-chain-gap.md — Viraj's 3 unresolved decisions
- docs/IT_BRIEF.md — IT's 8 unanswered infra questions
10. What I did in THIS session (for context)
1. Committed 9852ec0 (wave-12: 8 files, 470 insertions): migration chain fixes, model drift fixes (0021 tasks, 0022 documents), email-validator in requirements.txt, nginx.conf SPA fallback, independent verification report
2. Dispatched 6 subagents in parallel for waves 9/10/11, then 3 more for waves 14/15/16, then 1 each for 17/18/19/20/21/22/23/24
3. Subagents all wrote reports; orchestrator + me committed in batches
4. Committed 2073c36 (wave-18)
5. Final pytest: 339/339 pass in ~3 minutes
That's the full handoff. The project is in a clean, committable, verifiable state. Waves 22-24 are the remaining real work; wave-25 needs a brief written first.