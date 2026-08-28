# Data Intake Protocol (Excel Import)

> **For:** the person tasked with loading SWA's real Excel sheets into the system — likely for the
> first time, with **no IT help**. This explains the *real* import path (not the demo seed), what
> files are expected, and the exact commands to run. Read it before you touch `make swa-live-local`.

---

## 1. Two very different ways to get data in (don't confuse them)

| Command | What it loads | When to use |
|---|---|---|
| `make seed-demo` | Fake "demo" data from `scripts/seed_demo.py` | **Never** for client review — it is not real SWA data |
| `make swa-live-local` (alias `make bootstrap-real`) | **Real** SWA Excel sheets from `resources/` | The only correct path for client/go-live data |
| `make import-real` | Dry-run of the real import (no writes) | **Always run this first** to validate a new extract |
| `make import-real-commit` | Wipe + commit real sheets only (no inquiry→project linking) | When you want just the sheets in, nothing else |

> Source: `docs/REAL_DATA.md`, `Makefile`.

---

## 2. Where the real source files live

The client's source workbooks are **not** in the database — they are Excel files on disk:

```
resources/ERP_Sheets_Extracted/ERP Sheets/*.xlsx
resources/ERP Structure.zip
resources/MEETINGS_MASTER.md
resources/EXCEL_SHEETS_INVENTORY.md
```

> These are **partial samples** extracted from SWA (not a full OneDrive dump). A full go-live import
> uses the **same tool** against *frozen live OneDrive files* once Viraj names the owner.
> See `docs/REAL_DATA.md:47-62`.

---

## 3. Which sheets are actually imported (MVP scope)

The importer is driven by a `sheet_type` string. The supported MVP sheets:

| Excel file | Importer `sheet_type` | Lands in |
|---|---|---|
| Inquiries Sheet.xlsx | `inquiries` | Inquiry records |
| Clients Sheet.xlsx | `clients` | Client records |
| Service Agreements Sheet.xlsx | `agreements` | Service agreements |
| Project Tracking Sheet.xlsx | `projects` | Projects (the sample extract may be empty) |
| Tokens Sheet.xlsx | `tokens` | Token records |
| Document Reference Sheet.xlsx | `document_references` | Document references |
| Time Logging Sheet.xlsx | `time_logs` | Time entries |
| Sustainability Metrics Sheet.xlsx | `sustainability` | Sustainability metrics |

**Out of scope (not imported):** HR, marketing, complaints, research, training — per Meeting 2 /
SCOPE_GUARD.
> Source: `docs/REAL_DATA.md:13-26`; `src/backend/services/import_service.py:912-963` (`SHEET_CONFIG`).

---

## 4. The step-by-step safe procedure

**Step 1 — Dry run, always first.** This parses the sheets and reports what it *would* do, without
writing anything:
```bash
make import-real
```
Expected: a report per sheet with `total_rows`, `created`, `updated`, `skipped`, and any `errors`.
If you see errors, **stop and read them** — do not skip to a commit.

**Step 2 — Full load (wipe + real sheets + link inquiries→projects + users):**
```bash
make swa-live-local      # same as: make bootstrap-real
```
Login afterwards: `admin@swa.co.in` / `admin123!`
App URLs: UI **http://127.0.0.1:3100** · API **http://127.0.0.1:8100**.

**Step 3 — If you only want the sheets, no linking:**
```bash
make import-real-commit
```

---

## 5. How the importer behaves (so surprises aren't scary)

- **Per-sheet result object** tracks `total_rows`, `created`, `updated`, `skipped`, `errors`
  (`import_service.py:47-72`). A row that fails parsing goes into `errors`, it does **not** abort
  the whole sheet.
- **Stubs:** when a sheet references a client/project that doesn't exist yet, the importer can
  create a stub (e.g. `SWA-SYS-UNLINKED`) so links aren't lost. Stub creation is **off by default**;
  enable with `allow_stubs=True` or `IMPORT_ALLOW_STUBS=1`. For the sample extract, agreements
  create stub clients if missing. `import_service.py:26-41`.
- **Date parsing** accepts `YYYY-MM-DD`, `DD/MM/YYYY`, `DD-MM-YYYY`, and datetime variants; `N/A`
  and blanks become "no date". `import_service.py:85-100`.
- **Numbers** strip thousands separators (commas) and treat `N/A`/blank as null; a non-numeric value
  raises a row error rather than corrupting the DB. `import_service.py:103-120`.
- **Yearly ID reset** and the "no Leads sheet / no Lead ID" rule are applied per Viraj's locked
  decisions (`docs/REAL_DATA.md:64-69`).

---

## 6. "The import finished but something looks wrong" checklist

1. Did you run `make import-real` first? If not, you skipped the validation step — re-run it.
2. Check the `errors` list in the import output. A few row errors are normal for a messy sample
   extract; a sheet with *all* rows in `errors` means a column-name mismatch — compare the file to
   `resources/EXCEL_SHEETS_INVENTORY.md`.
3. Are clients/projects showing as stubs? You probably need `IMPORT_ALLOW_STUBS=1`, or the source
   sheet that defines them wasn't imported yet (import order matters: clients before agreements).
4. **Do not** run `make seed-demo` to "fix" gaps — that loads fake data. Re-run the real import.
5. Full go-live against live OneDrive files is a separate, deliberate step — confirm with Viraj
   before doing it.

---

## 7. What we do NOT claim

The extracted workbooks are **partial samples** (e.g. Projects = 0 rows in the current extract).
The import tool is proven against these samples; the *full* live import is untested until the real
files are supplied. Treat any "0 rows imported" for a sheet as "the sample was empty," not "the
tool failed."
