# Incident Response Playbook

> **For:** the on-site person at SWA who has **no ops background** and no IT department to call.
> **Goal:** tell you, in plain steps, what to do when the system is broken — and what "broken"
> actually looks like. Bookmark this file.

---

## 0. First, stay calm and confirm

Before you "fix" anything, answer three questions:

1. **Is it actually down, or just slow?** Open `PRODUCTION_WALKTHROUGH.md` and run the health
   checks there. A slow page is different from a dead page.
2. **How many people are affected?** One person? One team? Everyone?
3. **Did anything change recently?** A restart, a new file import, a Windows update, a power cut?

Write the answers down. You'll need them.

### Severity cheat-sheet (so you know how fast to move)

| Level | Means | Example | Move fast? |
|---|---|---|---|
| **SEV-1** | Nobody can use the system, or data may be lost | Postgres won't start, all pages 503 | **Immediately** |
| **SEV-2** | A major feature is broken for everyone, no workaround | Can't log in, can't import data | Same day |
| **SEV-3** | One feature broken, workaround exists | Can't export a PDF but can view on screen | Next day |
| **SEV-4** | Cosmetic / docs only | A label is wrong | Whenever |

---

## 1. Scenario: PostgreSQL is down

**Symptom:** every page errors; `/readyz` returns `503` with `"db": "error: ..."`
(see `PRODUCTION_WALKTHROUGH.md`). `docker-compose logs backend` shows connection-refused errors.

**Steps:**
1. Check the container: `docker-compose ps` — is `postgres` listed as `Up (healthy)`?
2. If it's `Restarting` or `Exit`, look at its logs: `docker-compose logs --tail=50 postgres`.
3. If the volume looks corrupted (rare): **do not delete `pg_data`** — that is the database.
   Restore from the last backup (`docs/runbook_backup_restore.md`).
4. If it's just stopped: `docker-compose restart postgres`, wait ~10 s for healthy, re-check
   `/readyz`.
5. If it won't come up and you have a backup, follow
   `docs/runbook_backup_restore.md` → "Restore database".

---

## 2. Scenario: Redis is down (and why `/readyz` lies)

**Symptom:** `/readyz` returns `503` with `"redis": "error: ..."`. **Important:** the app may
still *serve some pages* (it reads from the DB), but `/readyz` will report not-ready, so a load
balancer or health check will pull the app out of rotation.

**Why this matters on a laptop without Docker:** on a machine where Redis isn't running,
`/readyz` returns `503` and **two automated tests fail**. That is expected — it is the readiness
check doing its job, not a bug. Don't "fix" the test; fix Redis.

**Steps:**
1. `docker-compose ps` — is `redis` `Up (healthy)`?
2. `docker-compose restart redis`, wait for `redis-cli ping` to answer `PONG`.
3. Re-check `/readyz` — `redis` should read `ok`.
4. Redis holds **background jobs and caches, not the database.** If Redis is empty after a
   restart, in-flight exports/email jobs may need re-triggering (see Scenario 4).

---

## 3. Scenario: Celery background jobs are stuck

**Symptom:** exports (PDF/slides), report generation, or email never finish. The `worker`
container may be dead, or the queue is backed up.

**Steps:**
1. Check the worker: `docker-compose ps` → is `worker` `Up`?
2. Look at the queue depth via Prometheus metric `celery_queue_depth`
   (see `docs/operational/OBSERVABILITY.md` §2). A number that only grows = stuck.
3. If the worker crashed: `docker-compose restart worker`.
4. If a single bad job is wedged, restarting the worker drops in-progress jobs (they're not lost
   from the DB, but their results are). Re-trigger the export from the UI.
5. Re-check: the queue depth should drop to ~0 within a minute of the worker being healthy.

---

## 4. Scenario: JWT secret needs rotation (suspected token leak)

**What a JWT is, in one sentence:** when you log in, the server gives the browser a signed token
(a string) that proves who you are for the next hour. "Rotation" means changing the secret the
server uses to sign tokens, which invalidates every currently-issued token — forcing everyone to
log in again.

**Steps (do this if a token/secret may have leaked):**
1. Generate a new strong secret:
   ```bash
   openssl rand -hex 32
   ```
2. Put the new value in the environment / `.env` as `SECRET_KEY` (the compose file reads
   `SECRET_KEY` with a fallback of `dev-secret-change-me` — **never** ship that default to
   production; see `SECURITY_PERIMETER_GUIDE.md`).
3. Restart the backend: `docker-compose restart backend` (and `worker`, which also reads
   `SECRET_KEY`).
4. All users are now logged out and must log in again. Tell people in advance if you can.
5. Old tokens are rejected immediately because they were signed with the old secret.

> Note: this invalidates **all** sessions, including ones that were fine. There is no "revoke just
> one user" path today — rotation is the blunt instrument. See `SECURITY_PERIMETER_GUIDE.md` for
> the known JWT gap (refresh tokens stay valid up to 30 days).

---

## 5. Scenario: Disk full from `uploads/`

**Symptom:** uploads fail, exports fail to save, or the server starts throwing 500s with "no
space left on device." Uploaded files (documents, BOQ files, exports) live in the
`uploads/` directory (local storage) or MinIO.

**Steps:**
1. Check free space: `df -h` on the host; or inside the backend container, check the upload
   volume.
2. Find the biggest offenders: `du -sh uploads/* | sort -h | tail`.
3. **Do not delete files that are still referenced** by records in the app (e.g. client documents
   tied to a project). Deleting them breaks those records.
4. Safe cleanup targets: old export outputs that nobody opened, temporary import staging files.
5. If you must reclaim space, archive old uploads to external storage first, then remove from the
   live `uploads/` directory.
6. Restart the backend after freeing space if it had crashed.

---

## 6. General recovery order (when unsure)

1. **Confirm** with the health checks in `PRODUCTION_WALKTHROUGH.md`.
2. **Stabilize** — restart the single broken container; don't nuke everything.
3. **Check dependencies** — Postgres and Redis must both be healthy or `/readyz` stays 503.
4. **Communicate** — tell users what's broken and roughly when it'll be back.
5. **After recovery** — note what happened in `docs/audits/` so it isn't a mystery next time.

---

## 7. What we intentionally do NOT claim

We do **not** have automated paging, an on-call rotation, or a status page today. When something
breaks, the person reading this file *is* the on-call. That is why these steps are written in
plain language.
