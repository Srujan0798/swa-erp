# Industry alignment — meetings → code → docs

**Date:** 2026-08-23  
**Purpose:** Prove live-consultancy fidelity without rewriting the product.

## Evidence

```
python3 -m pytest tests/wave-9/ tests/wave-37/ -q
# 81 passed (chain + storage safety)

rg first_lead_id src/backend/schemas src/backend/models
# NO_LEAD_ID_IN_MODELS_SCHEMAS

# Full suite: see companion paste after solo run (must be 0 failed)
```

## Hierarchy of truth (enforced)

1. `resources/MEETINGS_MASTER.md` + ADRs  
2. Working code + fresh tests  
3. README / MASTER-FLOW / HANDOFF  
4. Historical wave reports  

## Decision matrix

| Meeting / ADR decision | Code | Doc |
|---|---|---|
| Inquiry→Client→SA→Token→DocRef→Time | BUILT (wave-9+) | README mermaid |
| `SWA-{year}-{TYPE}-{seq}` yearly reset | `reference_id_service.py` | ADR-0002 |
| DBR/KDR shared counter | `document_reference_service.py` | README |
| Convert: check client → always Project | inquiry convert | ADR-0002 |
| APEX/INNER clients; INSUDESIGN service | free-text | ADR-0002 |
| Lead ID removed | no schema fields | ADR-0002 |
| Time log owner-only (Admin all) | **FIXED** `time_tracking.py` | Meeting §4 |
| Finance not VIEWER | **FIXED** invoices/costs/revenue/executive | Meeting §4 |
| Doc mutations Designer+ | **FIXED** `documents.py` | Meeting matrix spirit |
| MinIO + Celery | BUILT wave-31 | MEETINGS footnote corrected |
| `/metrics` not anonymous | **FIXED** auth required | wave-37 RISK closed |
| Hourly rate not magic silent | settings `DEFAULT_HOURLY_RATE_INR` | wave-37 |
| Path traversal | LocalStorage containment | wave-37 |
| Deploy / IT | EXTERNAL | MASTER-FLOW wait |

## Residual (honest)

- JWT refresh rotation / access denylist (ops enhancement)
- Import per-row savepoints (larger change)
- Client Windows Server load test (needs Viraj machine)
- Some non-service modules still &lt;70% coverage (not meeting requirement)
