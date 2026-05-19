# SWA ERP — Constitution

These are non-negotiable principles. Every wave, every task, every decision is checked against these. Changing the constitution requires an explicit ADR.

## Tech principles

1. **Python 3.11 + FastAPI for backend.** No Django, no Flask. Type-hinted everywhere. Pydantic v2 for all I/O.
2. **PostgreSQL only.** No SQLite in prod, no NoSQL. Alembic migrations for every schema change.
3. **React + Vite + TypeScript strict mode.** No CRA, no Next.js (we don't need SSR for an internal ERP).
4. **No ORM-free SQL strings in services.** Use SQLAlchemy 2 declarative + repositories.
5. **No business logic in routers.** Routers depend on services; services depend on repositories.
6. **No `from X import *`.** Explicit imports only.
7. **No raw `dict`/`Any` at API boundaries.** Always Pydantic schemas.

## Data principles

8. **Money is `Decimal(18,2)`.** Never float. INR is the default currency; multi-currency ready.
9. **Datetimes are UTC in DB.** Display in Asia/Kolkata. No naive datetimes anywhere.
10. **Audit log is append-only.** Every mutation gets an `audit_log` entry: who, when, what before, what after.
11. **No hard deletes for business data.** Use `deleted_at` soft-delete. Workers and audit logs are exempt.
12. **Optimistic locking via `version` column.** Updates require `If-Match` on critical entities.

## Security principles

13. **Secrets via env only.** Never in code, never in repo. `.env` is gitignored.
14. **Passwords via bcrypt cost 12.** Never plaintext, never reversible.
15. **JWT short-lived (1h access, 30d refresh).** Rotate refresh tokens.
16. **RBAC enforced server-side.** Frontend hides UI but server is the source of truth.
17. **SQL via parameterized queries only.** No string concatenation, no f-strings into SQL.
18. **CORS strict.** Allowlist frontend origin only.

## Workflow principles

19. **Two-tier development.** Orchestrator plans + reviews; OpenCode workers execute. No mixing.
20. **Wave-based shipping.** Each wave is end-to-end demoable before the next begins.
21. **Acceptance criteria are executable.** Every task has runnable tests in `contracts/`.
22. **Never delete; archive.** `attic/`, `docs/historical/`, `prompts/archive/`.
23. **ADRs for every major decision.** `docs/decisions/0NNN-title.md`. No oral history.
24. **CLAUDE.md stays short.** "Would removing this cause Claude to make mistakes?" If no, cut.

## Domain principles (SWA-specific)

25. **Compliance standards are versioned.** NBC 2016, NBC 2024 — code never assumes "latest". Standards are data, not code.
26. **Project lifecycle is enforced.** Lead → Quote → Awarded → Design → Vendor → Execution → Validation → Closed. Skipping a state requires admin override + ADR.
27. **BOQ ingestion is schema-first.** Validate before any DB write. Reject with clear errors. No partial inserts.
28. **GST + Indian regulatory awareness.** Invoices carry GSTIN, HSN/SAC codes; PAN on client records.
29. **No coupling to rfq2boq (Project 1).** ERP accepts BOQ files of any source. Zero direct API calls between the two products.

## Quality principles

30. **Test coverage ≥ 75% on services.** Routers and models lower; services and parsers must hit 75%+.
31. **No flaky tests.** Quarantine + fix within one wave. Don't ignore.
32. **No new dependencies without ADR.** Every new pip/npm package needs justification.
33. **Performance budgets.** API <500ms P95, page load <1.5s P95, BOQ parse <30s for 100 lines.
34. **Lint + format gated in CI.** ruff, black, eslint, prettier, mypy strict.

## Process principles

35. **/clear between unrelated tasks.** Don't pollute context.
36. **Plan before code.** For any change touching >1 file, /plan first.
37. **Sub-agents for investigation.** Use `agents/codebase-explorer.md` for exploring; don't bloat main context.
38. **Verify before approving.** Orchestrator runs acceptance commands before /merge.

## Out of scope (constitution-level)

- Multi-tenancy (until explicit wave with ADR)
- Mobile apps (until usage demands)
- Real-time collaboration (WebSocket-based co-editing)
- AI features inside the ERP (Project 1 is upstream; ERP is operational)
- Custom CAD/BIM tooling
- Replacement accounting (invoicing only; exports to accountants)

Any feature in this list requires an ADR + constitutional amendment before work begins.
