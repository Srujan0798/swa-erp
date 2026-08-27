# Wave 23 — Gotchas

> **Source:** Harvested from `work/reports/wave-23/01-correctness-bugs.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Financial PDF uses real ProjectCost data
The financial PDF was fixed to use real ProjectCost data, not stub/mock data. If you touch the PDF generation, verify against real project cost data.

### Money as Decimal
All money fields use Decimal(18,2), INR default, multi-currency ready. Don't use float for money anywhere in the codebase.

### Real soft-delete on Task
Task now has real soft-delete via `deleted_at` column. Hard-delete would break audit trails and foreign-key relationships.

### Project.version optimistic locking (0027)
Project has optimistic locking via `version` column (migration 0027). Concurrent edits can cause `OptimisticLockError` — handle in service layer.
