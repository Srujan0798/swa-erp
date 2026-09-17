# Wave-48 Task 03 — Token security hygiene (commit `f92b945`) — Verification Report

- HEAD at verification: `8652036` (`feat(security): METRICS_REQUIRE_AUTH flag, default True`)
- Verified commit: `f92b9452d8317933dc9258bc3eba21263ec5ef13` — `fix(wave-48): CSP header + refresh token rotation + idempotency PoC` (Tue Sep 15 2026)
- Worker scope: report-only, no code changes made.

## 1. What `f92b945` claimed

```
- Add Content-Security-Policy: default-src 'self' middleware
- Rotate refresh tokens on use (new token issued, old one revoked via revoke_single)
- Add Idempotency-Key header support on POST /tokens (Redis or in-process dict fallback)
- Frontend saves new refresh token from refresh response
- revoke_single added to refresh_token_repo (does NOT revoke all sessions)
```

Files changed (`git show --stat f92b945`): `src/backend/core/idempotency.py` (+136), `src/backend/main.py` (+10), `src/backend/schemas/auth.py` (+1), `src/backend/services/auth_service.py` (+11), `src/frontend/src/lib/api.ts` (+2) + its test (+6).

## 2. Verification — what survives at HEAD (code greps, raw)

- CSP: `src/backend/main.py:136` → `response.headers["Content-Security-Policy"] = "default-src 'self'"` — PRESENT.
- Rotation: `src/backend/services/auth_service.py:14` imports `revoke_single`; line 88 calls `revoke_single(db, valid_token.id)` — PRESENT.
- Idempotency: `src/backend/core/idempotency.py` — **ABSENT** (`grep: No such file or directory`; zero `Idempotency-Key`/`idempotency` hits anywhere under `src/backend/`). It was deliberately removed two days later by `93696da` (`fix(wave-50): deterministic test suite + cleanup idempotency stub`): `src/backend/core/idempotency.py | 136 ------------` (deleted) and `src/backend/api/tokens.py | 20 --` ("remove incomplete idempotency PoC code"). So the Idempotency-Key portion of `f92b945` is **reverted at HEAD by design**, not silently lost.

## 3. Verification — endpoint tests at HEAD (raw)

Same run as report 02: `python3 -m pytest tests/wave-6/test_compliance.py tests/wave-10/test_sustainability_metrics.py tests/wave-9/test_tokens.py -q` → `1 failed, 35 passed`. All 16 token tests pass except the concurrency one. RAW failure:
```
_ TestTokenConcurrency.test_20_parallel_creates_produce_gapless_sequential_ids _
...
E   psycopg2.errors.ForeignKeyViolation: insert or update on table "tokens" violates foreign key constraint "tokens_agreement_id_fkey"
E   DETAIL:  Key (agreement_id)=(66d4e304-1d7e-4153-b232-f1f5140514e2) is not present in table "service_agreements".
...
tests/wave-9/test_tokens.py:356: in worker
    t = create_token_service(
```
This is a parallel-create test-isolation defect (workers racing against a rolled-back/missing agreement row), unrelated to CSP/rotation/idempotency. No dedicated tests for CSP header presence, refresh rotation, or Idempotency-Key were found in `tests/` (`grep` for `Idempotency-Key|revoke_single|Content-Security-Policy|default-src` under `tests/` → only pagination `page_size` hits and unrelated idempotency mentions).

## 4. Before/after

- Before `f92b945`: no CSP header; refresh tokens reusable (no rotation); no idempotency support.
- After `f92b945`, as surviving at HEAD: CSP `default-src 'self'` middleware live; refresh-token rotation via `revoke_single` live; **Idempotency-Key PoC removed by `93696da`** — POST /tokens has no idempotency support at HEAD.

## 5. DoD checklist

- [x] CSP header present in middleware — PASS (main.py:136)
- [x] Refresh rotation via `revoke_single` present — PASS (auth_service.py:14,88)
- [x] Idempotency-Key status determined honestly — REVERTED by `93696da` (not present; removal was explicit, not rot)
- [ ] Token test file fully green — 15/16 pass; 1 pre-existing concurrency FK failure pasted raw above
- [ ] Dedicated security tests (CSP header asserted, rotation round-trip, replay-of-old-refresh rejected) — NOT PRESENT in suite; recommended, not fabricated

## 6. Residual risks

1. The reverted idempotency PoC leaves POST /tokens without duplicate-submit protection; if still wanted, it needs a fresh design (the stub's per-process dict fallback was never production-safe — `93696da` was right to remove it; Redis-backed is the way).
2. CSP/rotation have **zero test coverage** — a future refactor could drop either silently. Owning agent should add: `assert response.headers["Content-Security-Policy"] == "default-src 'self'"` and a refresh-then-replay-old-token-must-fail test.
3. The `test_20_parallel_*` FK failure needs quarantine/fix independent of this report.
