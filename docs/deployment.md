# Deployment

**Rewritten 2026-07-21** — this file was a generic-VPS placeholder ("Hetzner/DigitalOcean, k8s
later") left over from project kickoff, describing a hypothetical target that has nothing to do
with the actual deployment target. The real target, confirmed with the client (Meeting 2, see
`resources/MEETINGS_MASTER.md`), is their own on-premises Windows Server, not a cloud VPS.

## Dev (now)
See `runbook.md` for local dev setup via `docker-compose.yml`.

## Production — real target, not the old placeholder

The actual target is: **on-premises Windows Server, 128GB RAM, VPN-only access, 100+
concurrent users per Meeting 2** — this was **IT's claim about the server; our wave-35 load
tests verified the app at **10/50/100 concurrent users, p95 ≈ 29–51 ms, no server errors** on
a dev machine (`docs/PERFORMANCE.md`). The client's Windows Server itself has not been
load-tested yet. This is not
staging/prod-on-a-VPS the way the old version of
this file assumed — there is no cloud hosting decision to make, it's already been made.

The real production config work is done, not "to be designed later":
- **`docker-compose.prod.yml`** — production-shaped compose file (separate from the dev
  `docker-compose.yml`), built in wave-20
- **`.env.production.example`** — production environment template, with every value that
  depends on the client's IT team's answers explicitly marked `# PENDING IT ANSWER`
- **`docs/DEPLOYMENT_CHECKLIST.md`** — the actual step-by-step deployment runbook, built in wave-20
- **`deliverables/SEND_IT.md`** — the 8 specific infra questions still blocking the final values in the
  files above (Docker Engine vs Desktop, Linux-container availability, free ports, TLS
  approach, internal hostname, where Postgres/Redis run, deploy access model) — already sent to
  the client's IT contact, awaiting reply as of this writing
- **`docs/decisions/0003-it-server-call-brief.md`** — the reasoning behind each of those 8 questions

Check `work/reports/wave-20/` to confirm these actually landed before trusting this list — this
file describes what wave-20 was scoped to build, verify against the report before relying on it.

## What's genuinely still undecided
Nothing architectural — the stack (FastAPI/Postgres/Redis/React, Docker-based) was decided at
kickoff (`docs/decisions/0001-tech-stack.md`) and never changed. What's pending is purely
server-specific facts only the client's IT team can supply — see `docs/IT_BRIEF.md`'s 8
questions. There is no "when to migrate to k8s" decision to make; this is a single on-prem
server for one company's internal team, not a cloud service planning for horizontal scale.
