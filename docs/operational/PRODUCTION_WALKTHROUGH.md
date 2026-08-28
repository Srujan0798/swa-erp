# Production Walkthrough

> **For:** someone with **no ops background** who needs to tell "the system is healthy" from "the
> system is broken" — without reading code. After reading this you should be able to open a
> terminal and confirm the system is alive.

---

## 1. The big picture (one paragraph)

SWA ERP is a web app. A **frontend** (the screens people click) talks to a **backend** (the brain
that does the work) over the network. The backend stores data in **PostgreSQL** (the database) and
uses **Redis** (a fast scratch-pad for jobs and caches). Long-running jobs (PDF/export generation)
are handled by a separate **worker** process so the website stays responsive. **MinIO** is optional
file storage (only used if `STORAGE_BACKEND=minio`). Everything runs as Docker containers.

---

## 2. The containers (what should be running)

Run `docker-compose ps`. On a healthy dev machine you should see these services (names match
`docker-compose.yml` exactly):

| Container | What it is | Should be |
|---|---|---|
| `postgres` | The database | `Up (healthy)` |
| `redis` | Scratch-pad / job broker | `Up (healthy)` |
| `minio` | Optional file storage | `Up (healthy)` (only if using MinIO) |
| `migrate` | One-shot DB migration step | `Exit 0` (ran once, then stopped — this is normal) |
| `backend` | The API brain | `Up` |
| `worker` | Background job processor | `Up` |
| `frontend` | The website | `Up` |
| `adminer` | A database viewer (dev only) | `Up` (optional) |

> **`migrate` showing as exited/completed is correct.** It runs `alembic upgrade heads` once at
> startup and then stops. Don't try to "restart" it repeatedly.

---

## 3. The ports (what to type in a browser)

These are the **dev** defaults. They are chosen so SWA doesn't collide with other apps that use
3000/8000.

| What | URL | Backed by |
|---|---|---|
| Website (frontend) | **http://localhost:3100** | `frontend` container, port 80 → host 3100 |
| API (backend) | **http://localhost:8100** | `backend` container, port 8000 → host 8100 |
| Database viewer (dev) | http://localhost:8180 | `adminer` |
| MinIO console (if used) | http://localhost:9000 | `minio` |

> On the **client's Windows Server** these ports may differ (VPN, reverse proxy). The walkthrough
> above describes the dev setup that the load tests used (`docs/PERFORMANCE.md:18-20`).

---

## 4. The two health checks (the most useful 2 commands you have)

The backend exposes two URLs. Learn these; they are your first line of diagnosis.

### `/healthz` — "is the process alive?"
```bash
curl http://localhost:8100/healthz
```
- **Always returns:** `{"status": "ok"}` (HTTP 200) as long as the backend process is running.
- **Cost:** near zero — it does NOT check the database or Redis.
- **Use it for:** "did the backend crash?" If this fails, the process is dead.

### `/readyz` — "can it actually serve users?"
```bash
curl http://localhost:8100/readyz
```
This checks **three things** and returns a report:

```json
{
  "status": "ok",
  "checks": {
    "db": "ok",
    "redis": "ok",
    "migrations": "ok"
  }
}
```

- **`db`** — can it talk to PostgreSQL? (`SELECT 1` succeeds)
- **`redis`** — can it talk to Redis? (`PING` succeeds)
- **`migrations`** — is the database schema up to date? (current revision == head)

**What the response means:**

| `/readyz` returns | Meaning | Action |
|---|---|---|
| `200` + all `ok` | Fully healthy | Nothing to do |
| `503` + `db: error` | Database unreachable | See Incident Playbook §1 |
| `503` + `redis: error` | Redis unreachable | See Incident Playbook §2 |
| `503` + `migrations: pending` | Schema behind code | Run `alembic upgrade heads` |

> **Critical gotcha:** `/readyz` returns **503 when Redis is absent**. On a laptop without Docker,
> or with Redis stopped, this is expected and **two automated tests will fail** because of it. That
> is the health check working correctly, not a code bug. See `INCIDENT_RESPONSE_PLAYBOOK.md` §2.

---

## 5. A 60-second "is it healthy?" checklist

1. `docker-compose ps` → all needed containers `Up (healthy)`.
2. `curl http://localhost:8100/healthz` → `{"status":"ok"}`.
3. `curl http://localhost:8100/readyz` → status `ok`, all three checks `ok`.
4. Open **http://localhost:3100** in a browser → login page loads.
5. Log in → dashboard renders, lists open.

If all five pass, the system is healthy. If not, match the failing step to the Incident Playbook.

---

## 6. Where the logs are

All containers print logs to stdout. View them with:
```bash
docker-compose logs --tail=50 backend      # the API
docker-compose logs --tail=50 worker       # background jobs
docker-compose logs --tail=50 postgres     # database
```
Each log line carries a `request_id` so you can follow one user action across the system (see
`OBSERVABILITY.md`).
