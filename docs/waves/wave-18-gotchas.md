# Wave 18 — Gotchas

> **Source:** Harvested from `work/reports/wave-18/01-security-hardening.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Production refuses insecure SECRET_KEY
The security hardening makes prod refuse an insecure SECRET_KEY. Don't assume any random string works — the validator checks entropy/structure.

### Rate limiting on login
429 on rapid login. The auth rate-limiter can also kill the whole backend test suite (see wave-12 gotchas, commit `3e0f137`).

### GST shipped on invoices
GST was shipped on invoices in wave-18 (commit `2073c36` "invoice GST"). Previously listed as a wave-7 requirement — resolved later.
