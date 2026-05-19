# Python rules

- Python 3.11+
- Type hints REQUIRED on every function signature
- Pydantic v2 for I/O; SQLAlchemy 2 declarative for ORM
- Imports: explicit; no `from X import *`
- Functions ≤ 50 lines; files ≤ 300 lines (refactor if larger)
- Error types: `ClientError(4xx)` / `ServerError(5xx)` / `IntegrationError(external)`
- Logging: structlog only; never `print`
- Tests: pytest; fixtures in `conftest.py`; one assert per test (mostly)
- No `dict`/`Any` at API boundary — Pydantic schemas required
- DB sessions via dependency injection; never global
- `Decimal(18,2)` for money; never `float`
- Datetimes: UTC in DB, Asia/Kolkata in display layer
- Soft deletes via `deleted_at` column; no hard `DELETE` for business data
- Alembic for every schema change
