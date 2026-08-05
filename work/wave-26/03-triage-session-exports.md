# Wave-26 Task 03 — Triage the 142 raw session exports (122MB)

**Read `work/wave-26/00-EXTRACTION-SCHEMA.md` first.** You edit NOTHING except your own report.

## Scope
`docs/historical/session_exports/` — 142 raw `.json` session logs, ~122MB total

## Critical context
These are raw OpenCode session dumps — machine telemetry, not prose. A prior pass classified
them as "not prose, nothing to consolidate, archived as-is" **without actually opening them**.
That was a reasonable triage call under time pressure, but it was never verified. You are
verifying it.

122MB of JSON almost certainly contains mostly tool-call traces and token accounting. But it may
also contain the **full text of assistant reasoning and user instructions** from 142 sessions —
which, if so, is the single largest untapped record of what was actually decided and why during
this project. That possibility is worth 45 minutes to rule in or out.

## Method — be disciplined about size, do NOT cat these files
1. Check structure first on ONE file:
   `python3 -c "import json;d=json.load(open(PATH));print(type(d));print(list(d)[:20] if isinstance(d,dict) else len(d))"`
   Then map the schema — what fields exist, which contain natural-language text vs. telemetry.
2. Once you know the schema, write a small throwaway Python script (put it in
   `/tmp/`, NOT in the repo) that walks all 142 files and extracts only the natural-language
   fields (user messages, assistant text) — skipping tool traces, token counts, embeddings.
3. Report the aggregate: how much real prose exists across all 142, versus telemetry.
4. Grep the extracted prose for the same high-signal patterns as task 02:
   decisions, dead ends, client statements, blockers, gotchas.
5. Cross-check any hits against `docs/PROJECT_HISTORY.md` and `resources/MEETINGS_MASTER.md`.

## The specific question you must answer definitively
**"Do these 142 JSON files contain recoverable decision/intent content that exists nowhere else
in the project — yes or no?"**

If yes: extract it and put it in section 2/4/5 of your report.
If no: state the method that justifies that conclusion, including how many files you actually
parsed and what fields you checked. Do not guess.

## Also report
- Total size and whether these are worth keeping in the repo at all long-term (122MB of
  machine logs in git history is a real cost — but note they are ALREADY committed, so deleting
  them now does NOT shrink the repo, it only removes them from the working tree. Factor that
  into your recommendation and say so explicitly.)
- Whether any file contains secrets/credentials/API keys that shouldn't be in a repo that might
  be handed to a client. **This is important — flag anything sensitive immediately and
  prominently at the very top of your report, above all other sections.**

## Deliver
Report to `work/reports/wave-26/03-triage-session-exports.report.md` using the mandatory schema.
Then STOP.

## Constraints
- Time budget: 45 min
- Edit nothing in the repo but your report; scratch scripts go in `/tmp/`
- Never paste raw JSON dumps into your report — summarize
- Allowed tools: read, grep, python3, git (read-only)
