# Decision Index — Master Reference

**Single source of truth for all decisions. Every item links to source.**

---

## Decision Categories

| Category | File | Count | Status |
|----------|------|-------|--------|
| **Viraj Decisions** | `VIRAJ_DECISIONS.md` | 10 | 🔴 3 blocking, 🟡 4 confirm, 🟢 3 cosmetic |
| **IT Decisions** | `IT_DECISIONS.md` | 8 | 🔴 8 blocking deploy |
| **Open Items** | `OPEN_ITEMS_FROM_MEETINGS.md` | 9 | 🔴 3 blocking, 🟡 3 confirm, 🟢 1 cosmetic |
| **Resolved (ADR-0002)** | `docs/decisions/0002-core-id-chain-gap.md` | 3 | ✅ Resolved |

---

## Decision Map (What → Where → Who)

| Decision | Source | File | Owner |
|----------|--------|------|-------|
| Migration owner | Meeting 2 §7 | `VIRAJ_DECISIONS.md` #1 | Viraj |
| IT 8 answers | Meeting 2 §4 | `IT_DECISIONS.md` #1-8 | Viraj → IT |
| Internal URL | Meeting 2 §4 | `IT_DECISIONS.md` #6 | Viraj → IT |
| 4th Agreement ID | Meeting 1 §7 / ADR-0002 | `VIRAJ_DECISIONS.md` #4 | Viraj |
| Annual ID reset | Meeting 1 §7 / ADR-0002 | `VIRAJ_DECISIONS.md` #5 | Viraj |
| Windows Server | Meeting 2 §1 | `VIRAJ_DECISIONS.md` #6 | Viraj → IT |
| Reforge ID format | Meeting 1 §7 | `VIRAJ_DECISIONS.md` #7 | Viraj |
| Compliance versions | Meeting 2 §12 | `VIRAJ_DECISIONS.md` #8 | Viraj + Auditor |
| Windows Server 100% | Meeting 2 §1 | `VIRAJ_DECISIONS.md` #6 | Viraj → IT |
| Architecture for IT | Meeting 2 §11 | `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` | Viraj → IT |
| IT 8 questions | Meeting 2 §4 | `SEND_IT.md` | Viraj → IT |
| Migration owner | Meeting 2 §7 / ADR-0002 #4 | `VIRAJ_DECISIONS.md` #1 | Viraj |

---

## Resolved Decisions (No Action)

| Decision | Resolution | Source |
|----------|------------|--------|
| APEX/INNER = client names | Free-text `service_name`; INSUDESIGN = service | ADR-0002 Q1 |
| Yearly ID reset | Per-year counters implemented | ADR-0002 Q2 |
| Lead ID / LDI | Removed entirely; migration 0030 | ADR-0002 Q3 |
| GST on invoices | Built & verified (wave-7/11) | SUBMISSION.md |
| Client portal | Deferred — out of MVP | MEETINGS_MASTER.md §3 |
| HR/Finance/Satisfaction | Dropped from MVP | MEETINGS_MASTER.md §3 |
| Reforge/DPR | Role-gated (Auditor+Designer) | MEETINGS_MASTER.md §6 |
| Independent sheets | Dropped from MVP | MEETINGS_MASTER.md §3 |

---

## Quick Links

| File | Purpose |
|-------|---------|
| `VIRAJ_DECISIONS.md` | Your decision log — fill this |
| `IT_DECISIONS.md` | IT's 8 questions — forward to Vikrant |
| `OPEN_ITEMS_FROM_MEETINGS.md` | Full context from both meetings |
| `ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md` | Forward to IT with SEND_IT.md |
| `SEND_IT.md` | 8 questions for IT — forward to Vikrant |
| `SHOW_AND_ASK.md` | Demo script + what to ask live |
| `DEMO_SCRIPT.md` | 10-min demo walkthrough |
| `SMOKE_CHAIN` | `python3 scripts/smoke_chain.py` (live proof) |

---

## Decision Workflow

```
Viraj reads VIRAJ_DECISIONS.md
    → Answers 🔴/🟡 items
    → Forwards ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md + SEND_IT.md to IT
    → IT answers IT_DECISIONS.md (8 questions)
    → We fill docker-compose.prod.yml + .env.production.example
    → Deploy → Smoke test → Go-live
    → Viraj names migration owner → Run real Excel import
```

---

## One-Line Status

| Area | Status |
|------|--------|
| **Product code** | ✅ 10/10 — all gates pass |
| **Viraj decisions** | 🔴 3 blocking, 🟡 4 need confirmation |
| **IT decisions** | 🔴 8 blocking deploy |
| **Migration owner** | 🔴 Not named |
| **Demo readiness** | ✅ Ready (`make dev` + `smoke_chain.py`) |
| **Documentation** | ✅ Complete (all .md files above) |

---

*Updated: 2026-09-21 | All code gates pass | Decision files ready for Viraj/IT*