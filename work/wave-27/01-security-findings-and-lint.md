# Wave-27 Task 01 — Security-review findings + lint debt

## What to do
Fix 3 findings from an automated security review of recent commits, plus the accumulated ruff
debt. All are confirmed, none are speculative.

## Files to modify
- `scripts/backup_db.sh`, `scripts/restore_db.sh`
- `.pre-commit-config.yaml`
- Whatever ruff flags (backend only)
- CREATE: `tests/wave-27/test_backup_script_safety.py`

## Files you must NOT touch
- Anything under `work/`, `docs/`, `resources/` — this is a code-only task
- Test files other than your own new one

## The core problem (inline)

### 1. Credentials leaking into logs — `scripts/backup_db.sh` and `scripts/restore_db.sh`
Both scripts (written in wave-19) echo or otherwise expose the database connection string, which
contains the password, into stdout/logs. On a client's Windows Server these logs may be
collected, emailed, or retained. Fix:
- Never echo `$DATABASE_URL` or any string containing a password. If you need to show the user
  which DB is being targeted (which `restore_db.sh` legitimately must, since it's destructive),
  print **only host/port/dbname** — parse them out, never the credentials.
- Prefer passing the password to `pg_dump`/`psql` via the `PGPASSWORD` environment variable or a
  `.pgpass` file rather than embedding it in a connection-string argument, because command
  arguments are visible to any user running `ps` on the machine.
- Check `set -x` / debug tracing isn't enabled anywhere in either script — that would echo every
  expansion including secrets.

Preserve the existing confirmation prompt in `restore_db.sh` — it must still clearly tell the
user which database is about to be overwritten, just without the password.

### 2. Unpinned third-party pre-commit hook — `.pre-commit-config.yaml`
A hook is referenced by a mutable ref (branch/tag) rather than a pinned commit SHA. That means
an upstream change silently executes new code on every developer's machine at commit time — a
real supply-chain risk. Fix: pin every `repo:` entry to a full commit SHA with the human-readable
version retained as a trailing comment, e.g.:
```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: 9188e37e6d7b4dfa5b7ceb5c2a2f0b19dbfbf2fd  # v0.6.9
```
Run `pre-commit autoupdate` then convert the resulting tags to SHAs, or resolve each manually.

### 3. Ruff debt — 145 errors, 56 auto-fixable
Run `ruff check src/backend/ --fix` for the auto-fixable set, then review what remains.
- Fix the remainder where the fix is mechanical and obviously safe (unused imports, import
  sorting, deprecated typing syntax).
- Where a rule is genuinely inappropriate for this codebase — `B008` in particular fires on
  FastAPI's `Depends()` in default arguments, which is the framework's intended idiom, not a bug
  — add a scoped `per-file-ignores` or targeted `noqa` with a one-line reason comment rather than
  contorting working code to satisfy the linter.
- **Do not change runtime behavior to satisfy a linter.** If a rule can only be satisfied by a
  behavioral change, leave it, `noqa` it with a reason, and note it in your report.

## Acceptance criteria
- [ ] Neither backup script can emit a password: verify by running each with a password-bearing
  `DATABASE_URL` and grepping the full output for the password string — must be absent
- [ ] `restore_db.sh` still names the target database (host/port/dbname) before its confirmation prompt
- [ ] A real backup → restore round-trip still works against a scratch database (create one, restore
  into it, drop it — do NOT test-restore over the dev database)
- [ ] Every `repo:` in `.pre-commit-config.yaml` is pinned to a full 40-char SHA
- [ ] `ruff check src/backend/` — clean, or every remaining item is an explicit documented ignore
- [ ] `python3 -m pytest tests/ -q` → **344 passed minimum**, zero failures

## Critical test-suite note — read before running pytest
This suite produces false mass-failures under two known conditions, both already fixed but easy
to reintroduce:
1. Stray/parallel pytest processes racing on the shared `swa_erp_test` Postgres → `DROP SCHEMA`
   deadlocks. Confirm none are running: `ps aux | grep pytest`.
2. The auth rate limiter (5 logins/min/IP). `tests/conftest.py` sets
   `DISABLE_AUTH_RATE_LIMIT=1` at import time — **do not remove or reorder that line**, it must
   execute before `src.backend.main` is imported. If you see mass `KeyError: 'access_token'`,
   that's this.

## How to deliver
1. Fix all 3 findings + lint
2. Run every acceptance check
3. Report to `work/reports/wave-27/01-security-findings-and-lint.report.md`, stating the exact
   ruff before/after counts and listing every rule you chose to ignore with its reason
4. Stop

## Constraints
- Time budget: 90 min
- Never weaken a security control to make a check pass
- Allowed tools: file edit, bash, pytest, ruff, psql, pre-commit
