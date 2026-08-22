# MASTER-FLOW — THE ONE PATH (no variants, no branches)

> **Role:** The single-path "what to do, ask, continue" answer. Part of the front-door set —
> start at [README.md](README.md).

> **ONE LINE:**
>
> **CODE DONE → QUALITY TRACK DONE (32–39) → VIRAJ DATA Qs ✅ → SERVER/DEPLOY (Viraj, no IT) → DEPLOY → MIGRATE → LIVE**

---

## Hierarchy of truth (read in this order)

1. **Client decisions:** [`resources/MEETINGS_MASTER.md`](resources/MEETINGS_MASTER.md) + [`docs/decisions/`](docs/decisions/)
2. **Working system:** `src/backend/`, `src/frontend/`, tests
3. **Evaluator front door:** [`README.md`](README.md)
4. **Session catch-up:** [`HANDOFF.md`](HANDOFF.md)
5. **Map:** [`HIERARCHY.md`](HIERARCHY.md)
6. **Wave status:** [`work/ACTIVE.md`](work/ACTIVE.md) (32–39 all SHIPPED)
7. **Submission pack:** [`deliverables/SUBMISSION.md`](deliverables/SUBMISSION.md)

Wave reports under `work/reports/` are **historical evidence** — if they conflict with a fresh
pytest/vitest paste, the fresh paste wins for front-door claims.

---

## THE ONE FLOW (now)

```
[1] DONE  — product v1.0.1 (waves 1–31)
[2] DONE  — Viraj data Qs (ADR-0002)
[3] DONE  — professional-grade waves 32–39 (CI, coverage, load, review, packaging)
[4] DONE  — industry truth pass started (metrics aligned to green suites)
[5] NOW   — WAIT on Viraj for server/deploy facts (no IT department)
[6] NEXT  — when he has machine time: docs/INSTALL_NO_IT.md → deploy
[7] NEXT  — Excel freeze + make import-real (owner = Viraj decides)
[8] LIVE
```

**Do not** re-blast `SEND_IT.md` / `SEND_VIRAJ.md` into the group. Drafts already posted.

---

## PART A — Locked with Viraj

| Topic | Answer | Code |
|---|---|---|
| APEX / INNER | **Clients** | Free-text client names |
| INSUDESIGN | **Service name** | Free-text `service_name` |
| Yearly ID reset | **Yes, everywhere** | `reference_counters` per `(type, year)` |
| Leads / LDI | **No Leads module; Lead ID columns removed** | Migration 0030 |

## PART B — Server / deploy (external)

Owner: **Viraj** (or nominee). Checklist reference: `deliverables/SEND_IT.md`.  
When ready: [`docs/INSTALL_NO_IT.md`](docs/INSTALL_NO_IT.md).

## PART C — Engineering seal

- Backend: **565 passed / 0 failed / 1 skipped** (post final-close)
- Frontend: **522 passed / 0 failed**
- Seal: [`work/reports/FINAL-CLOSE.report.md`](work/reports/FINAL-CLOSE.report.md)
- Industry hardening (RBAC/metrics) continues only if gaps vs Meeting 1 remain — see plan

## THE ONLY REMAINING EXTERNAL RISK

Viraj is busy and there is no IT dept → **server answers may be slow**. That delays **deploy**,
not the product. Do not rebuild. Do not re-ask the same 8 unless he asks.
