# MASTER-FLOW — THE ONE PATH (no variants, no branches)

> **Role:** The single-path "what to do, ask, continue" answer. Part of the front-door set —
> start at [README.md](README.md).

> This is the ONLY file you need to know where you are and what's next.
> Everything else is reference. If a file isn't named here, you don't need it right now.
> The whole project, as ONE line:
>
> **CODE DONE → VERIFIED → RELEASED → VIRAJ DATA Qs ✅ → SERVER/DEPLOY ANSWERS (via Viraj, no IT dept) → DEPLOY → MIGRATE → LIVE**

---

## Reality check (group chat 2026-08-11)

- Srujan **already sent** the 3 data Qs + 8 server Qs in the client WhatsApp group (not as
  separate MD files to "resend").
- Viraj **answered** the 3 data questions. Locked in ADR-0002. **No code change.**
- Viraj: **"There is no IT department"** — he will try to get the 8 server answers when he can;
  he is busy. Srujan already replied "ok no worries."
- So: do **not** keep asking to "send SEND_IT.md / SEND_VIRAJ.md." Those files are **source
  drafts** for messages already delivered. Next messages are **follow-ups in the same group**.

---

## THE ONE FLOW (now)

```
[1] DONE  — product v1.0.1 shipped, verified
[2] DONE  — 3 data Qs asked + Viraj answered (group)
[3] DONE  — 8 server Qs asked in group; no IT dept; Viraj owns finding answers when free
[4] NOW   — short group follow-up: confirm his 3 answers + LDI example (he asked for it)
[5] WAIT  — Viraj (or whoever he points to) on server/deploy facts when he's free
[6] DEPLOY — when enough server facts exist: fill PENDING markers, deploy
[7] MIGRATE — Excel → ERP (who runs it = Viraj decides)
[8] LIVE
```

---

## PART A — VIRAJ DATA ANSWERS (locked)

| # | Answer | Code |
|---|--------|------|
| 1 | APEX / INNER = **clients**; INSUDESIGN = **service name** | Already free-text `service_name` |
| 2 | Yearly reset **everywhere** (`2025-…-011` → `2026-…-001`) | Already per-(type, year) |
| 3 | No Leads sheet (removed); he wanted LDI **example** | No Leads module; optional historical field |

Group follow-up text: `deliverables/REPLY_VIRAJ.md` (short WhatsApp form at top).

## PART B — SERVER / DEPLOY (no IT department)

The 8 questions still matter for **first production install**, but the owner is **Viraj**
(or someone he nominates), not a separate IT team. Draft list remains in
`deliverables/SEND_IT.md` for reference only — **already posted in group.**

Until answers exist, safe defaults for a small on-prem trial (if Viraj wants a temporary path):

- Docker Engine free + WSL2 if Windows Server
- Compose stack (Postgres + Redis + app + optional MinIO) all in Docker
- Self-signed HTTPS or HTTP-only **only on VPN** (document risk)
- Hostname/IP he chooses later
- Daily DB + uploads backup via our `make backup-*` scripts until company backup joins

Do **not** invent company hostname/ports without him. Prefer wait over wrong prod config.

---

## PART C — FILES THAT MATTER

| File | Role now |
|------|----------|
| `MASTER-FLOW.md` | Where you are |
| `deliverables/REPLY_VIRAJ.md` | Next group message (confirm + LDI example) |
| `docs/DEPLOYMENT_CHECKLIST.md` | After server facts exist |
| `deliverables/SUBMISSION.md` | Full handoff package (reference) |

`SEND_VIRAJ.md` / `SEND_IT.md` = **already-sent message drafts**, not to re-blast.

---

## THE ONLY REMAINING RISK

Viraj is busy and there is no IT dept → **server answers may be slow**. That delays deploy,
not the product. Code is done. Do not rebuild. Do not re-ask the same 8 unless he asks you to.

**Next human action:** wait for Viraj. Confirm + LDI message already sent.

**When he is free for install:** `docs/INSTALL_NO_IT.md` (no-IT one-sitting guide) → then
Excel import + handover docs.
