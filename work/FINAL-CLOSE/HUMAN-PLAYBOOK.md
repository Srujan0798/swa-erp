# Human playbook — what **you** do / say

You are not the coder for this close. You paste prompts, watch for lies, and decide when to stop.

---

## My recommendation (locked)

**Full close:** hygiene → stabilize → wave-37 → wave-38 → seal.  
That is the only path that matches “industry internship / professional bar” without self-owning.

---

## How to start (today)

1. Open terminal → `cd /Users/srujansai/Desktop/swa-erp`
2. Open **new** Claude Code session (fresh context)
3. Open `work/FINAL-CLOSE/prompts/PASTE-TO-CLAUDE.md`
4. Select all → copy → paste into Claude → Enter
5. Let it run Phase 0–2 in session 1 (or further if context holds)

Optional: commit this pack first so Claude sees it on a clean tree:

```bash
git add work/FINAL-CLOSE work/reports/COMPLETION-HANDOFF-VERDICT.md
git commit -m "$(cat <<'EOF'
docs(final-close): ultimate close pack + living verdict

Executable protocols P01–P20, paste prompts, and DoD for
hygiene → stabilize → wave-37 → wave-38 → seal.
EOF
)"
```

---

## How to continue

| If session ends after… | Paste |
|---|---|
| Hygiene/stabilize incomplete | `CONTINUE-SESSIONS.md` → **S-RESUME** |
| Stabilize done, 37 not done | **S2** |
| 37 done, 38 not done | **S3** |

---

## What you say to Claude (short)

**Start:** paste `PASTE-TO-CLAUDE.md` (don’t paraphrase).  
**Nudge:** “Continue next incomplete protocol. Paste pytest/vitest output. No claims without commands.”  
**Challenge:** “Show me the report path and the command that produced each %.”  
**Stop:** “Write NOT DONE with blockers — don’t fake wave-38.”

---

## What you say to Viraj / group (if anything)

Default: **nothing** (server wait already acknowledged).  
If they ask status:

> Engineering side is in final professional close (review + submission package). Product features were already done. When you have server time, we use the no-IT install guide — no need to re-answer a long questionnaire unless something changed.

Do **not** paste architecture questions that re-open the stack.

---

## What you say when someone asks “is it finished?”

**Before FINAL-CLOSE.report.md:**  
> Feature-complete since v1.0.1. Professional evidence close in progress (review + packaging).

**After DEFINITION-OF-DONE true:**  
> Closed for internship submission. Company deploy waiting on server facts (no IT dept).

---

## Red flags — kill the session narrative

- Report says all tests pass but doesn’t paste failures/node ids  
- “No module under 70%” globally  
- Starts rewriting README before wave-37 report exists  
- Wants to message Viraj 8 questions again  
- Spawns 5 concurrent pytest/opencode test runners  

---

## Time expectation (honest)

| Phase | Rough |
|---|---|
| 0–2 Hygiene + stabilize | 1–3 hours |
| 3 Wave-37 | 3–5 hours (biggest) |
| 4–5 Wave-38 + seal | 2–4 hours |

Usually **2–3 Claude sessions**. Not a 10-minute paste.
