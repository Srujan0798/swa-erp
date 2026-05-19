---
name: review-report
description: Verify a worker report against acceptance contracts and spec. Boris's #1 rule — always run commands yourself.
---

# review-report

## Steps
1. Read `work/reports/wave-N/0X-task.report.md`
2. Read matching `work/wave-N/0X-task.md`
3. Read `.specify/specs/wave-N/contracts/`
4. RUN every acceptance command via Bash
5. Spawn `agents/verifier.md` for independent review
6. Cross-check decisions against constitution and ADRs
7. Decide APPROVE / REVISE / REJECT

## Red flags
- Worker claims passed but didn't paste output
- Worker added files not in the brief's CREATE list
- Worker modified files in the FORBIDDEN list
- Decisions violate constitution (e.g., used SQLite, deleted instead of soft-deleted)
- Tests pass but cover only happy path
