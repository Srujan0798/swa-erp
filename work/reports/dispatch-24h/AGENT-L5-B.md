# AGENT-L5-B

Repo: `/Users/srujansai/Desktop/swa-erp` (main). Project Tracking sheet vs product.

## Findings

- Dry-run paste (same run as L5-A): `projects total= 0 created= 0 updated=  0` — the client's **Project Tracking Sheet.xlsx sample is empty**, exactly as Meeting 2 recorded.
- **No fake tracking rows created or seeded.** The importer reads the sheet, finds 0 rows, imports nothing.
- Projects in the product come from **Inquiry → Convert** (`inquiry_service.py` convert creates the client's project with yearly `PRJ` id — verified in L3-A report and wave contracts). The dev DB's projects (CON/DBR/CAS/GAD chain) were created by convert + `make swa-live-local`, not by a faked tracking import.

## Verification

- `python3.11 scripts/import_real_sheets.py` dry-run output above (fresh paste).
- Importer ORDER still contains `("projects", "Project Tracking Sheet.xlsx")` so when the client's sheet has real rows later, import resumes without code change.

No code change. No commit.