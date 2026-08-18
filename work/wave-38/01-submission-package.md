# Wave-38 Task 01 — Professional submission package

**RUNS LAST.** Depends on 32-37 all landing. This wave packages *verified reality* — if it runs
early it will document claims that later waves invalidate. Verify all six reports exist first.

## What this is for

This is an **industry internship submission**, assessed by professionals. The evaluator's
experience is: they open the repo, skim for 10 minutes, and form a judgement. Right now that
10 minutes lands on internal wave-tracking docs and orchestration scaffolding — real engineering
history, but it reads as process exhaust, not as a professional deliverable.

The engineering is genuinely strong. **This wave makes that legible.**

## Files to create/modify
- `README.md` — **complete rewrite** as a showcase (currently an internal quick-start)
- `docs/ARCHITECTURE.md` — architecture with real rendered diagrams (mermaid)
- `deliverables/TECHNICAL_REPORT.md` — the engineering case study
- `deliverables/SUBMISSION.md` — refresh with post-32-37 verified numbers
- `deliverables/DEMO_SCRIPT.md` — a tight walkthrough script for a live/recorded demo

## Files you must NOT touch
- `work/` and `docs/historical/` — genuine project history, stays as-is. Don't sanitise it; a
  reviewer who digs in should find honest engineering records, including the failures.

## The work

### 1. README as the front door
A professional evaluator decides in 60 seconds. It needs, in order:
- **What this is** — one paragraph: an ERP replacing ~20 live Excel sheets for a real
  consultancy, digitising their existing workflow
- **The core business flow** — the Inquiry → Client → Agreement → Token → Document Reference →
  Time Log chain, as a rendered mermaid diagram. This is the intellectual core of the project;
  lead with it.
- **Verified quality metrics** — coverage %, test count, load-test numbers, security scan status.
  **Every number must come from waves 32-37's actual reports**, with a pointer to the evidence.
- **Tech stack + why** (link ADR-0001)
- **Run it in 3 commands**
- **Where the detail lives**

No badge that isn't backed by a real gate (wave-32 made CI real — badges are now honest).

### 2. Architecture with real diagrams
Mermaid diagrams that render on GitHub: system context, the core-chain data model, request
lifecycle, deployment topology. **Mark target-state vs. built explicitly** — this repo has a
documented history of diagrams implying things existed when they didn't; don't regress that.

### 3. Technical report — the differentiator
This is what separates a professional submission from a code dump. Structure:
- **Problem** — the client's real situation (cite `resources/MEETINGS_MASTER.md`, quote Viraj)
- **Requirements discovery** — including the genuinely interesting part: the original build
  produced a generic CRM, and re-reading the raw meeting transcripts revealed the client's actual
  requested workflow was a specific ID chain that hadn't been built at all
  (`docs/decisions/0002-core-id-chain-gap.md`). **Tell this honestly.** Catching and correcting a
  fundamental requirements misread is a stronger engineering signal than pretending it went
  smoothly.
- **Architecture + key decisions** (the ADRs)
- **Engineering rigour** — the wave-32-37 evidence: real CI gates, coverage, SAST, load tests,
  independent review findings and how they were triaged
- **Honest limitations** — pull from `SUBMISSION.md` §4. Do not sand these off.
- **What was learned**

Write it for an engineer who wasn't there. No unexplained internal jargon ("wave-22" means
nothing to them — explain the process once, then use it).

### 4. Demo script
A 5-10 minute walkthrough hitting the core chain end-to-end with real reference IDs, GST on an
invoice, and role-based access. `deliverables/DEMO_WALKTHROUGH.md` exists — build on it, make it
tight and rehearsable.

### 5. Optional, high-value: publish a showcase
Consider building an **Artifact** (publishable HTML page) summarising the project — architecture
diagram, quality metrics, the core flow. Load the `artifact-design` skill first if you do. This
gives a shareable link rather than asking an evaluator to clone a repo. Use `dataviz` skill
conventions for any charts.

## Acceptance criteria
- [ ] README readable in 60s, leads with the business problem + core-chain diagram
- [ ] **Every metric traceable** to a wave-32-37 report — a reader can verify each claim
- [ ] All mermaid diagrams render correctly on GitHub (check, don't assume)
- [ ] Technical report covers all 6 sections including the requirements-misread story and the
      real limitations
- [ ] Demo script rehearsed end-to-end against a running stack at least once
- [ ] **Zero claims that waves 32-37 didn't verify** — grep your own numbers against the reports
- [ ] Full suite green; all gates pass

## Deliver
Report → `work/reports/wave-38/01-submission-package.report.md` listing every claim made and its
source report. Commit before writing.

## Constraints
- Time budget: 210 min
- **Do not inflate.** The honest verified position is genuinely strong; overstating it is the one
  thing that would undermine it under professional scrutiny.
- Allowed: file edit, git, mermaid, Artifacts, dataviz/artifact-design skills, pytest
