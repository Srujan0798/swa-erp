# Wave-26 — Handoff Consolidation, PHASE 1 (EXTRACTION)

## Read this first — it applies to all four wave-26 tasks

**Purpose of this wave:** the project has accumulated ~320 handoff/session artifacts across four
locations plus a dozen current docs. Before the final submission, all durable content must be
extracted, de-duplicated, and consolidated into a small canonical set. **Phase 1 (this wave) is
EXTRACTION ONLY.** You are not merging, not deleting, not rewriting anything.

**Absolute rules for every wave-26 task:**
1. **DO NOT delete, move, rewrite, or edit ANY existing file.** Not one. Phase 2 does that,
   after the orchestrator merges your findings. If you think a file should be deleted, say so in
   your report — do not act on it.
2. **DO NOT edit any source code, test, or config.** This wave touches documentation only, and
   in Phase 1 it doesn't even touch that — you only READ and WRITE YOUR OWN REPORT.
3. Your only write is your own report file, at the exact path your task specifies.
4. **Do not trust any status claim you read.** These documents contradict each other heavily and
   many are months stale. When a document asserts a fact about the system ("N tests pass", "X is
   implemented", "wave-N is current"), either verify it against the actual repo or mark it
   `UNVERIFIED`. Never copy a claim forward as fact.

## Ground truth as of 2026-08-05 (verify anything that contradicts this)

- Git HEAD: `3e0f137`, working tree clean, `main` synced to origin
- **Test suite: 344 passed, 0 failed** (`python3 -m pytest tests/ -q`, full clean run)
- Waves 1-21 shipped; waves 22-24 have task briefs written but NOT executed; wave-25 was a
  docs-truth pass done inline
- Canonical current docs already exist and are known-good: `resources/MEETINGS_MASTER.md`,
  `docs/PROJECT_HISTORY.md`, `docs/decisions/0001`-`0004`, `plan/EXECUTION.md`,
  `plan/ARCHITECTURE.md`, `docs/IT_BRIEF.md`, `docs/SCOPE_GUARD.md`
- Two external blockers, unresolved: Viraj's 3 open decisions
  (`docs/decisions/0002-core-id-chain-gap.md`) and IT/Vikrant's 8 infra answers
  (`docs/IT_BRIEF.md`)

## MANDATORY OUTPUT SCHEMA

Every wave-26 report MUST use exactly these sections, in this order. The orchestrator merges
these mechanically — deviation breaks the merge.

```markdown
# Wave-26 Task <N> — <name> — EXTRACTION REPORT

## 1. INVENTORY
| File | Bytes | Date | One-line what-it-is | Verdict |
(Verdict ∈ UNIQUE-VALUE | DUPLICATE-OF:<file> | SUPERSEDED-BY:<file> | NOISE | STALE-BUT-HISTORIC)

## 2. DECISIONS FOUND
Every decision recorded anywhere in your scope. One row each.
| Decision | Stated by whom | Date | Still true? (YES/NO/UNVERIFIED) | Evidence (file:line) | Already in a canonical doc? (which, or NO) |

## 3. OPEN QUESTIONS / UNRESOLVED ITEMS FOUND
| Question | Who must answer | First raised (date) | Still open? | Evidence (file:line) | Already tracked in canonical docs? |

## 4. REQUIREMENTS / INTENT FOUND
Anything describing what the client wanted that is NOT already in resources/MEETINGS_MASTER.md.
| Requirement | Source (file:line) | Confirmed present in MEETINGS_MASTER.md? (YES/NO) |

## 5. TECHNICAL FACTS / GOTCHAS WORTH KEEPING
Non-obvious things a future engineer would waste hours rediscovering.
| Fact | Evidence (file:line) | Already in docs/PROJECT_HISTORY.md? (YES/NO) |

## 6. CONTRADICTIONS FOUND
Where two documents (or a document and the real repo) disagree.
| Claim A (file:line) | Claim B (file:line) | Which is true, and how you verified |

## 7. DELETE / ARCHIVE RECOMMENDATION
Your recommendation only — you do NOT act on it.
| File | Recommend | Why | Anything that must be extracted first? |
(Recommend ∈ KEEP-AS-IS | ARCHIVE | MERGE-INTO:<target> | SAFE-TO-DELETE)

## 8. WHAT I COULD NOT DETERMINE
Be explicit. An honest gap is worth more than a confident guess.
```

## Delivery
Write your report to the exact path in your task file, then STOP. Do not proceed to Phase 2.
Do not start another task. Do not "helpfully" clean anything up.
