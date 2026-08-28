# Wave 24 — Gotchas

> **Source:** Harvested from `work/reports/wave-24/01-dead-code-and-ui-wiring.report.md` — real gotchas only, nothing invented.

## Known pitfalls

### Dead debug endpoint removed
A dead debug endpoint was removed. If you see references to it in old docs/handoffs, they're stale.

### Dead page removed
A dead page was removed. Navigation refs to it are now stale in old handoffs.

### Notifications still stubs
Notifications router is mounted (wave-17) but handlers still return `[]`/`{}` — this is wave-24 item #6, still unfixed. `src/backend/api/notifications.py:22,31`.

### Delete-user/client UI wired
Delete user and delete client UI are now wired. Previously only available via API.

### Tokens + DocumentReference reachable via navigation
These were previously not reachable via navigation — now they are. Old navigation docs may be stale.

### Notifications un-stubbed (0026)
Migration 0026 un-stubbed notifications. But handlers are still stubs (see above).
