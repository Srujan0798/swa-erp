# MASTER-FLOW — THE ONE PATH (no variants, no branches)

> This is the ONLY file you need to know where you are and what's next.
> Everything else is reference. If a file isn't named here, you don't need it right now.
> The whole project, as ONE line:
>
> **CODE DONE → VERIFIED → RELEASED → ASK 2 PEOPLE (3+8 questions) → THEIR ANSWERS → DEPLOY → GO-LIVE MIGRATION**

---

## THE ONE FLOW (read top to bottom, do it in this order only)

```
[1] DONE   — all 31 waves shipped, v1.0.0 tagged, full test suite green (413 passed)
[2] SEND   — 3 questions to Viraj  (copy-paste from Part A below)
[3] SEND   — 8 questions to IT     (copy-paste from Part B below)
[4] WAIT   — for the 11 answers. NOTHING in code depends on you meanwhile.
[5] DEPLOY — when IT answers arrive: fill the PENDING IT ANSWER markers in
             docker-compose.prod.yml + .env.production.example, run deployment
[6] MIGRATE — when Viraj answers arrive: run the Excel importer against real data
[7] LIVE   — hand over access, close the project
```

There is no step 8. There are no alternate paths. If you are unsure what to do,
re-read this file. If something isn't on this line, it is not your problem right now.

---

## PART A — SEND TO VIRAJ: the file is `deliverables/SEND_VIRAJ.md`

Full brief + the 3 questions, ready to send as-is. Nothing else needed. If you want the question
details behind it, see `docs/decisions/0002-core-id-chain-gap.md`.

## PART B — SEND TO IT/VIKRANT: the file is `deliverables/SEND_IT.md`

Full brief + the 8 questions, ready to send as-is. Nothing else needed. This is the single
sendable version of the IT brief (older draft copy: `docs/IT_BRIEF.md` — do not send that one).

---

## PART C — THE 3 FILES THAT MATTER (and nothing else)

| File | When you touch it |
|---|---|
| **`MASTER-FLOW.md`** (this file) | Every time you wonder what's next |
| **`deliverables/SEND_VIRAJ.md`** | Send to Viraj (Part A) |
| **`deliverables/SEND_IT.md`** | Send to IT/Vikrant (Part B) |

Every other document in this repo is **already-written history**: the wave reports, the ADRs,
the runbooks, the submission package. They exist as evidence and reference. You do NOT act on
them. If you find yourself reading an old ADR or a wave report to decide "what's next", stop —
the answer is in this file.

---

## PART D — WHEN THE ANSWERS COME BACK

- **IT answers →** open `docker-compose.prod.yml` + `.env.production.example`, fill every
  `PENDING IT ANSWER (Q#)` with the real values, then follow `docs/DEPLOYMENT_CHECKLIST.md`
  (or `docs/runbook.md`) step by step. Deploy. Verify login over VPN.
- **Viraj answers →** if Q2 (year reset) or Q3 (LDI) change a default, it's a one-line code fix
  + one migration, then `make test`. Then run the Excel import (SUBMISSION.md §7) against the
  real data with Viraj as the migration owner.
- **Both → project is LIVE.** Close it. Keep this file as the handover.

---

## THE ONLY REMAINING RISKS (both external, neither yours to fix in code)

1. Viraj never answers → fields stay free-text/nullable, defaults hold, tiny fix possible later. Low risk.
2. IT never answers → no production deploy. High risk, purely a client-side hold. Nothing you can
   build around it.

**You are done with code. You are waiting on two people. That is the whole truth.**
