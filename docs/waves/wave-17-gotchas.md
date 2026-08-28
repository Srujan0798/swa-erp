# Wave 17 — Gotchas

> **Source:** Harvested from `work/reports/wave-17/01-mount-notifications-router.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Notifications router mounted but handlers are stubs
The wave-17 "notifications router" mount landed but the handlers are still stubs — `list_notifications` returns `[]`, `mark_read` returns `{}`. This is exactly the wave-24 item #6, still unfixed at wave-26 time of writing.

Check `src/backend/api/notifications.py:22,31` and `main.py:18,58`.
