# Continue prompts — paste when a Claude session dies mid-close

Always `cd /Users/srujansai/Desktop/swa-erp` first.  
Always re-read `work/FINAL-CLOSE/ANTI-FABRICATION.md` and run **P01** before continuing.

---

## S2 — Resume into Wave-37 (after Phase 0–2 done)

```
Resume FINAL-CLOSE for swa-erp. Read work/FINAL-CLOSE/README.md and ULTIMATE-CLOSE-GUIDE.md.

Assume Phases 0–2 may already be done — VERIFY with git log + pytest/vitest before claiming so:
- ACTIVE/HANDOFF synced?
- 401/403 tests fixed (0 fail on those files)?
- TaskCard flake fixed?
- Vitest in CI?
- Solo pytest tests/ -q → 0 failed, cov ≥85%?

If Phase 2 incomplete, finish P05–P09 first.

Then execute Phase 3 only: Protocols P11–P14 (+P15 if needed) per work/wave-37/01-independent-review.md.
Deliver work/reports/wave-37/01-independent-review.report.md with real tool outputs and triage table.
Do NOT start wave-38 in this session unless wave-37 is fully verified and committed.
Anti-fabrication rules apply. One pytest at a time.
```

---

## S3 — Resume into Wave-38 + close seal (after Wave-37 done)

```
Resume FINAL-CLOSE for swa-erp. Read work/FINAL-CLOSE/DEFINITION-OF-DONE.md.

VERIFY wave-37 is actually done:
- work/reports/wave-37/01-independent-review.report.md exists on main
- Suite still 0 failed

Then Phase 4: P17–P19 per work/wave-38/01-submission-package.md.
Every metric must cite work/reports/wave-N/*. Forbidden: 100% complete, global no-module<70%, stale 65.86% frontend.

Then Phase 5: P20 — write work/reports/FINAL-CLOSE.report.md, mark ACTIVE 37/38 SHIPPED, refresh HANDOFF, push origin/main.

Stop when DEFINITION-OF-DONE A–E are true. State external deploy blockers honestly.
```

---

## S-RESUME — Generic mid-protocol crash

```
Resume FINAL-CLOSE. Run Protocol P01 first.
Tell me: HEAD, last commit message, which Protocol P0x was in progress, what evidence already exists on disk.
Continue from the first incomplete protocol in work/FINAL-CLOSE/PROTOCOLS.md order.
Do not restart finished phases. Do not fabricate. Solo pytest only.
```

---

## If Claude asks “are we 100% done?”

Answer template for you (human):

> Not until FINAL-CLOSE.report.md exists and DEFINITION-OF-DONE checkboxes are all true. Check work/FINAL-CLOSE/DEFINITION-OF-DONE.md.
