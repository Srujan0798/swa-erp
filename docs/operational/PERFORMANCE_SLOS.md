# Performance SLOs

> **Read this first — who this is for:** someone with **no operations background** who needs to
> know "how fast is fast enough" and "what do I do if it's slow." Every number below comes from a
> real load test we ran. Nothing here is guessed.

---

## 1. Where these numbers come from (read before trusting any number)

All targets in this document are derived from **one real test run** captured on
**2026-08-19** and written up in [`docs/PERFORMANCE.md`](../PERFORMANCE.md).

**Plain-language caveat (this is the most important sentence in the file):**

> These measurements were taken on a **developer's laptop** (Apple Silicon, macOS), running the
> app inside Docker with **untuned, default development containers** for PostgreSQL and Redis.
> The client's actual production server is a **128 GB Windows Server, VPN-only** — a materially
> larger machine that has **never been load-tested**. We do **not** claim these numbers hold on
> the client's hardware. The defensible statement today is:
>
> *"Load tested at 10 / 50 / 100 / 150 concurrent users on a dev machine: p95 ≈ 29–130 ms, no
> server errors at any level. Client's Windows Server load test is pending."*
> — see `docs/PERFORMANCE.md:267-269`

"p95" means: **95% of requests finished faster than this number.** If p95 is 51 ms, then 95 out
of 100 requests took under 51 ms. It is the standard way to talk about "typical worst case"
without letting one slow outlier distort the picture.

---

## 2. The SLO table

Every row cites the line in `docs/PERFORMANCE.md` that produced it.

| Operation / load level | Target p95 (goal) | Acceptable p95 | Minimum p95 (CI hard floor) | Measured p95 (dev laptop) | Source |
|---|---|---|---|---|---|
| Steady state, **10 users** | ≤ 50 ms | ≤ 100 ms | ≤ 500 ms | **29 ms** | `PERFORMANCE.md:84` |
| Steady state, **50 users** | ≤ 50 ms | ≤ 100 ms | ≤ 500 ms | **30 ms** | `PERFORMANCE.md:142` |
| Steady state, **100 users** | ≤ 100 ms | ≤ 200 ms | ≤ 500 ms | **51 ms** | `PERFORMANCE.md:170` |
| Stress, **150 users** | ≤ 200 ms | ≤ 300 ms | ≤ 500 ms | **130 ms** | `PERFORMANCE.md:203` |
| `POST /api/auth/login` (per-request cost) | ≤ 400 ms | ≤ 500 ms | ≤ 1000 ms | **~210–310 ms** (BCrypt hashing) | `PERFORMANCE.md:92`, `:125` |
| Server error rate (HTTP 5xx) | 0% | 0% | 0% | **0% at every level** | `PERFORMANCE.md:7`, `:253` |
| Throughput at 100 users | — | — | — | **~51 req/s** | `PERFORMANCE.md:169` |

**How to read the three columns:**
- **Target** = what we aim for in normal operation.
- **Acceptable** = we will tolerate this under a brief load spike, but it warrants a look.
- **Minimum** = the hard floor enforced in CI (`perf_regression.yml`). If a change makes p95
  worse than this, the build fails. We set the floor generously (500 ms) because the *measured*
  numbers are far below it; the floor is a regression tripwire, not a performance goal.

---

## 3. The one honest warning: the "knee"

The test found a **degradation knee between 100 and 150 concurrent users** on the dev laptop:
p95 jumped from **51 ms (100 users) → 130 ms (150 users)** — roughly 2.5× for 1.5× the load.
That is still well inside the healthy boundary (p95 < 500 ms), but it tells us the app is no
longer scaling linearly past ~100 users **on this small hardware**.

> Source: `PERFORMANCE.md:234` and `PERFORMANCE.md:246`
> (`"the degradation knee sits between 100 and 150 users"`).

We have **no measurement on the client's larger server**, so we cannot say where the knee is
there. Until a run happens on that hardware, treat "100+ concurrent users" as **verified on a
laptop, unverified on the client's box.**

---

## 4. What "the tail" means (why login is slow)

Most endpoints sit at p95 ≤ 30–50 ms. The slow part is concentrated in two places:

1. **Login** (`/api/auth/login`) — p95 ~210–310 ms. This is **BCrypt password hashing**, a
   deliberate, CPU-bound cost that makes password guessing expensive for attackers. It is *not* a
   load effect and does not get worse with more users. `PERFORMANCE.md:92`, `:125`.
2. **Occasional slow list/detail queries** — `dashboard/executive` (p99 ~100–200 ms),
   `projects (list)` (p99 ~110–190 ms). These are rare outliers, not the common case.
   `PERFORMANCE.md:93-94`, `:126`.

---

## 5. Enforcement (how this becomes real)

- CI runs `tests/performance/` (Locust) and fails the build if p95 exceeds the **Minimum** column
  above. See `.github/workflows/perf_regression.yml`.
- The load profile and reproduction steps live in `tests/performance/README.md` and
  `docs/PERFORMANCE.md:271-283` (`make load-test-10/50/100/150`).
- **We do not claim the client's server meets these numbers.** Any capacity promise to the client
  must wait for a load test on their Windows Server. `PERFORMANCE.md:254-269`.

---

## 6. Plain-language summary for the on-site operator

- If pages feel slow but p95 is under ~200 ms, the bottleneck is **the network/VPN or the
  browser**, not the app.
- If p95 climbs past **500 ms** at 100 users, something changed — open
  `INCIDENT_RESPONSE_PLAYBOOK.md`.
- Login taking ~0.3 s is **expected**; it is BCrypt, not a bug.
- We have **never** tested the real production server. Don't promise "100+ users" on their
  hardware until we do.
