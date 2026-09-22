# SWA ERP — Administrator Guide

Procedures for the person who administers the system (the **Admin**). Everything
below is built and verified. No dedicated IT department is required for day-to-day
operation — these steps cover accounts, backups, and health checks.

---

## 1. Create a user account

1. Log in as **Admin**.
2. Open **Users** (sidebar, under *More*).
3. Click **New User** and fill in: name, email, role.
4. Share the one-time password with the person privately; they change it on
   first login.

**Roles** (mirrors how the Excel sheets were already restricted):

| Role | Can do |
|------|--------|
| Admin | Everything, including user management and finance |
| PM | Inquiries, clients, projects, agreements, tokens, time |
| Designer | Document references, time logging |
| Auditor | Review compliance checklists and certify documents (read-only elsewhere) |
| Viewer | Read-only browse |

Passwords are stored hashed. If someone forgets theirs, reset it from the
**Users** page — there is no way to recover the old password.

---

## 2. Backups

Run from a terminal at the project folder (or schedule daily/weekly):

```bash
make backup-db       # daily — dumps the PostgreSQL database
make backup-files    # weekly — backs up uploaded documents
make restore-db      # restore from a dump (confirm before running)
```

If the company already has a backup process on the server, join the ERP backups
to it rather than running a separate schedule. Backups go to the configured
backup folder; keep at least the last 7 daily and 4 weekly copies.

---

## 3. Health check

If staff report the site is down:

```bash
curl http://127.0.0.1:8100/healthz   # should return {"status":"ok"}
```

- If the API answers but the site does not load: the frontend service needs a
  restart.
- If the API does not answer: restart the backend (database data is safe — it
  lives in its own volume).
- In a Docker deployment: `docker compose restart` restarts all services.

---

## 4. One-time Excel import (go-live day)

The import tool is ready. The sequence is fixed:

1. The Excel owner **freezes** the live OneDrive files (everyone stops editing).
2. Dry-run the import and review the row report together:

   ```bash
   make import-real
   ```

3. Commit the import only after the dry-run report looks right:

   ```bash
   make import-real-commit
   ```

4. Spot-check: open **Inquiries**, **Clients**, and **Service Agreements** and
   confirm the real `SWA-…` IDs appear.

After a successful import, the Excel files become a read-only archive.

---

## 5. If something looks wrong

- Check the health endpoint first (section 3).
- Do not edit the database directly — records are linked (Inquiry → Client →
  Project → Agreement → Token), and direct edits break the links.
- For deployment or server-level issues beyond these steps, escalate to the
  named server owner. The architecture overview
  (`ARCHITECTURE_OVERVIEW_FOR_VIRAJ.md`) has the full component map for IT.
