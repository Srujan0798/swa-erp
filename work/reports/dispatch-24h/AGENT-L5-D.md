# AGENT-L5-D

Repo: `/Users/srujansai/Desktop/swa-erp` (main). Name/service mappings — verified in importer + schema.

## Findings

- **INSUDESIGN = service_name**: `scripts/bootstrap_real.py:419` reads free-text `Service Name` straight into `ServiceAgreementCreate.service_name` (plain `str`, min 1 max 255 — no enum anywhere). The live SA-011+INSUDESIGN row imports as a service name.
- **APEX/INNER = client names**: importer resolves clients **by name** (`_client_by_name`, `scripts/bootstrap_real.py:150-153`; Excel Clients sheet gives APEX/INNER). No special-casing, no enum, no third entity type.
- **No 4th SA type enum exists**: agreement schema has `service_name: str` + free-text `status`; there is no `sa_type`/`agreement_type` column (checked model + schemas + importer). LOCKED rule 1 respected — APEX/INNER are clients, INSUDESIGN is a service.

## Verification

- `grep -n "service_name" scripts/bootstrap_real.py` → line 419 mapping; missing Service Name → row error (no silent default).
- Dry-run (L5-A paste): agreements 3 rows, 0 errors — names round-trip.

No code change. No commit.