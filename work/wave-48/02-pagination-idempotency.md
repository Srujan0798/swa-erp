# Wave-48 Task 02 — Unbounded list endpoints + idempotency on money writes

Second slice of the same live-audit pass as task 01. Independent of task 01 — different files, can run in parallel.

## Verified findings
| # | Finding | Evidence |
|---|---|---|
| 5 | **`compliance.py` and `sustainability_metrics.py` have unpaginated list endpoints.** `list_standards`, `list_checklist`, `list_metrics` return everything, unbounded. 18/27 routers use `page_size`; these two don't. | `grep -n "@router.get" src/backend/api/{compliance,sustainability_metrics}.py` |
| 6 | **No idempotency protection anywhere.** A client retry on a network blip (e.g. token creation, invoice creation) can create duplicates — there is no `Idempotency-Key` handling at all. | `grep -rl "Idempotency" src/backend/` → 0 hits |

## Files you own
- `src/backend/api/compliance.py`, `src/backend/services/compliance_service.py` (or wherever `get_checklist_items_list` lives)
- `src/backend/api/sustainability_metrics.py`, `src/backend/services/sustainability_metric_service.py`
- `src/backend/core/idempotency.py` (new)
- ONE money-mutating endpoint as a proof-of-concept for idempotency — pick token creation (`src/backend/api/tokens.py`) since it's the highest-volume ID-generating endpoint in the client's real workflow

## The work

### 1. Paginate the two list endpoints
Match the existing `page`/`page_size` convention used by the other 18 routers exactly — same param names, same response envelope shape. Don't invent a new pagination style.

### 2. Idempotency-Key support (proof of concept, not project-wide)
Add a lightweight `Idempotency-Key` header check on `POST /tokens` (or the real token-creation route — verify the path first): if a request arrives with a header value seen before within a short window (e.g. 24h), return the original response instead of creating a duplicate. Store the key→response mapping in Redis if available, else a DB table — check what's already available in this stack before adding new infra. **This is a proof of concept on one endpoint; do not attempt to add it everywhere in this wave.** Document in the report which other endpoints would benefit most (invoice creation, agreement creation) as a backlog item for a future wave.

## Acceptance criteria
- [ ] `GET /api/compliance/standards?page=1&page_size=10` and the metrics equivalent return a paginated envelope matching the existing convention — paste real responses
- [ ] Sending the same `Idempotency-Key` twice to the token-creation endpoint returns the SAME token, not two — prove it with two real curl calls and their outputs
- [ ] Full backend suite still green

## Deliver
`work/reports/wave-48/02-pagination-idempotency.report.md`. Commit before writing it.

## Constraints
- Time budget: 90 min · commit per item
- Idempotency is proof-of-concept scope only — one endpoint, documented backlog for the rest
