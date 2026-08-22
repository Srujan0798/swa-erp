# Real SWA Excel data (internship source of truth)

**Do not treat `seed_demo.py` as production or client data.**  
Client source files live here:

```
resources/ERP_Sheets_Extracted/ERP Sheets/*.xlsx
resources/ERP Structure.zip
resources/MEETINGS_MASTER.md
resources/EXCEL_SHEETS_INVENTORY.md
```

## MVP sheets (imported)

| Sheet file | Importer type |
|------------|---------------|
| Inquiries Sheet.xlsx | `inquiries` |
| Clients Sheet.xlsx | `clients` |
| Service Agreements Sheet.xlsx | `agreements` |
| Project Tracking Sheet.xlsx | `projects` (sample extract may be empty) |
| Tokens Sheet.xlsx | `tokens` |
| Document Reference Sheet.xlsx | `document_references` |
| Time Logging Sheet.xlsx | `time_logs` |
| Sustainability Metrics Sheet.xlsx | `sustainability` |

Out of MVP (not imported): HR, marketing, complaints, research, training — per Meeting 2 / SCOPE_GUARD.

## Commands

```bash
# Preferred one-shot for local SWA trials (wipe + real sheets + link inquiries→projects + users)
make swa-live-local
# same as: make bootstrap-real

# Dry-run import only (no DB writes) — always first when validating a new extract
make import-real

# Wipe + commit sheets only (no inquiry→project linking)
make import-real-commit
```

Login after bootstrap: `admin@swa.co.in` / `admin123!`

App ports: UI **http://127.0.0.1:3100** · API **http://127.0.0.1:8100**

**Do not** use `make seed-demo` / `scripts/seed_demo.py` for client review.
## Sample extract reality check (2026-08)

The extracted workbooks are **partial samples** from SWA, not a full OneDrive dump:

| Entity | Approx rows in extract | Notes |
|--------|------------------------|-------|
| Inquiries | 3 | Real SWA-2025-INQ-* |
| Clients | 3 | Shabnam, Halcyon, Acme… SWA-2025-CLT-* |
| Agreements | 3 | All `service_name=INSUDESIGN`; client IDs CL-* (stub-created if missing) |
| Tokens | 4 | Under SA-011 |
| Document refs | 4 | CON/DBR/CAS/GAD sample |
| Projects | 0 | Tracking sheet header only in extract |
| Time logs | 1–3 | Sparse sample |
| Sustainability | 5 | Creates stub projects for PRJ-* refs |

Full go-live import uses the same tool against **frozen live OneDrive files** when Viraj names the owner.

## Viraj decisions (locked)

- APEX / INNER = **client names** (not SA types)
- INSUDESIGN = **service name**
- Yearly ID reset everywhere
- No Leads sheet; **Lead ID / LDI columns removed entirely** (Viraj 2026-08 — not stored, not historical)
