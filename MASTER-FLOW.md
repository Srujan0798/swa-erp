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

## PART A — SEND TO VIRAJ (copy-paste this message)

> Viraj, the build is complete and verified. Three data questions only — a sentence each is
> enough:
>
> 1. **4th Service Agreement type** — your sample data has `INSUDESIGN` as a service name, but we
>    only know of three verbally (IESK/APEX/Inner). Is INSUDESIGN a real 4th type, or was it a
>    data-entry variant?
> 2. **Yearly ID sequence** — IDs look like `SWA-2025-SA-011`. Does the counter restart at 1 on
>    Jan 1 each year, or keep counting across years? (System is built so either is a one-line
>    change.)
> 3. **`LDI-*` IDs** — is that the legacy form of an Inquiry ID, or something different? There is
>    no "Leads Sheet" in the 21 source files, so I can't confirm from the data alone.

**Why this matters (short):** nothing breaks if unanswered — those fields stay free-text and the
importer uses sensible defaults. But the wrong guess may need a one-line fix after go-live.

---

## PART B — SEND TO IT/VIKRANT (copy-paste this message)

> IT team, the app is ready to deploy on the company server. We need 8 factual answers to
> configure it correctly the first time. A sentence or two each is fine; if you don't know one,
> say so and who to ask.
>
> 1. **Docker** — is Docker already installed on the server? If yes, free "Docker Engine" or paid
>    "Docker Desktop"? If nothing, it just needs installing (free version is fine).
> 2. **WSL2** — the app uses standard Linux-style containers on the Windows Server. Can you
>    confirm WSL2 is available or can be enabled?
> 3. **Free ports** — about 5 port numbers need to be free (database, Redis, file storage ×1–2,
>    the app itself). What's already running/reserved on that machine?
> 4. **HTTPS** — staff log in with passwords over VPN, so the connection must be encrypted. Does
>    the company have an internal certificate authority, or should we set up a self-signed
>    certificate to start?
> 5. **Backups** — is there an existing backup process on the server? (Database + uploaded files
>    need daily backup — better to join the existing process than build a separate one.)
> 6. **Internal web address** — what will staff type/click to reach the app (e.g. `erp.swa.local`
>    or an IP)? This must be locked before final setup.
> 7. **Database placement** — database + Redis in the same Docker setup, or installed directly on
>    Windows as services? Either works; which is easier for your team to maintain long-term?
> 8. **Deploying updates** — when a new version is ready, what's the best way to push it: direct
>    remote access, a couple of commands we send, or an existing process you already use?

**Why this matters (short):** deployment cannot be configured correctly without these — the
production files have explicit `PENDING IT ANSWER (Q#)` markers for exactly these values, and
the deploy must not proceed until they're filled.

---

## PART C — THE 3 FILES THAT MATTER (and nothing else)

| File | When you touch it |
|---|---|
| **`MASTER-FLOW.md`** (this file) | Every time you wonder what's next |
| **`docs/decisions/0002-core-id-chain-gap.md`** | Only for Viraj's question details (Part A) |
| **`docs/IT_BRIEF.md`** | Only for IT's question details (Part B) |

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
