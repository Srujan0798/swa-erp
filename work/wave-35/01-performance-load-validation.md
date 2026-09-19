# Wave-35 Task 01 — Prove the performance claims (100+ concurrent users, never tested)

**Depends on wave-32.** Can run in parallel with 33 and 34.

## The problem

Every client-facing document in this repo states the system supports **100+ concurrent users**
(`deliverables/SUBMISSION.md`, `SEND_IT.md`, `plan/ARCHITECTURE.md`, the meeting record). It
comes from Meeting 2, where it was IT's statement about *the server's* capacity — **not a
measurement of this application.**

**It has never been load-tested.** For an industry submission, a stated performance figure with
no evidence is the kind of claim a reviewer will probe first — and "we never measured it" is a
bad answer. Either substantiate it or restate it honestly.

`locust==2.43.4` is **already in `requirements.txt`** and has never been used.

## Files to create
- `tests/performance/locustfile.py` — realistic user-journey load profile
- `tests/performance/README.md` — how to run it, how to read results
- `docs/PERFORMANCE.md` — the published results (this becomes submission evidence)
- `Makefile` — `make load-test` target

## Files you must NOT touch
- Application code — **unless** load testing reveals a genuine bottleneck worth fixing. If it
  does, fix it and document before/after numbers. That's the best possible outcome here.

## The work

### 1. Realistic load profile (not synthetic hammering)
Model what SWA staff actually do (see `resources/MEETINGS_MASTER.md`): mostly reads (dashboards,
lists, project/client detail), periodic writes (create inquiry, log time, issue token, generate
document reference), occasional heavy operations (PDF export, report generation).

Weight the tasks to match. A flood of identical requests to one endpoint is not a load test — it
proves nothing about real usage.

### 2. Measure, at minimum
- **Throughput** (req/s) and **latency** (p50/p95/p99) per endpoint group
- **Error rate** under load — the number that actually matters
- Behaviour at 10 / 50 / 100 / 150 concurrent users (find where it degrades, not just whether
  100 works)
- **Database**: identify N+1 queries and missing indexes under load. This codebase uses
  `selectinload` in places but it has never been verified under concurrency.

### 3. Then tell the truth in the docs
Three possible honest outcomes — all acceptable:
- **It handles 100+** → publish the numbers, claim is now evidence-backed. Best case.
- **It handles fewer** → publish the real number and correct every doc that says 100+. An
  accurate "verified to N concurrent users" is far stronger than an unverified 100.
- **It degrades on specific endpoints** → publish which, fix what's cheap (indexes, N+1), and
  document the rest as known limits.

**Do not tune the test to produce a flattering number.** The point is a defensible figure.

### 4. Environment honesty
You'll be testing on a dev machine, not the client's 128GB Windows Server. **State the test
environment explicitly** and do not extrapolate to their hardware — present it as "measured on
X, the client's server is materially larger."

## Acceptance criteria
- [ ] `make load-test` runs a realistic profile against a running stack
- [ ] `docs/PERFORMANCE.md` published with: test environment, methodology, p50/p95/p99 latency,
      throughput, error rate, and the concurrency level at which degradation begins
- [ ] Every doc claiming "100+ concurrent users" is either **substantiated** by these results or
      **corrected** to the measured figure — grep for the claim and fix each instance
- [ ] Any N+1 query or missing index found is documented; cheap fixes applied with before/after
      numbers
- [ ] Full backend suite still green after any changes

## Deliver
Report → `work/reports/wave-35/01-performance-load-validation.report.md`. Include raw locust
output, the results table, environment caveats, and every doc you corrected. Commit before
writing.

## Constraints
- Time budget: 150 min
- **Report the real numbers even if they're disappointing** — that's the entire value of this
  wave. A corrected honest claim is a professional outcome; an unverified claim left standing is
  the risk.
- Allowed: file edit, git, docker, locust, pytest, psql
