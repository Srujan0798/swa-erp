# Wave-48 Task 03 — CSP header + refresh-token rotation

## Verified findings
| # | Finding | Evidence |
|---|---|---|
| 7 | **No Content-Security-Policy header anywhere.** Access + refresh tokens are stored in frontend `localStorage` (confirmed prior verified fact about this codebase) — without a CSP, any XSS becomes full token theft with no mitigation. | `grep -rn "Content-Security-Policy" src/backend/` → 0 hits |
| 8 | **Refresh tokens never rotate.** `refresh_access_token()` in `auth_service.py` issues a new access token but reuses the SAME refresh token indefinitely — no new refresh token issued, old one never revoked. Combined with finding #7, a single XSS yields a refresh token valid for the full `JWT_REFRESH_TTL_DAYS` window with no rotation to limit blast radius. | `src/backend/services/auth_service.py:60-84` |

## Files you own
- `src/backend/main.py` (add CSP middleware)
- `src/backend/services/auth_service.py`
- `src/backend/db/repositories/refresh_token_repo.py`

## The work

### 1. Add a Content-Security-Policy header
A simple middleware or response-header addition. Given this is an internal SPA served from a known origin, start with a reasonably strict default (`default-src 'self'`) and adjust only for what the app genuinely needs (inline styles from Tailwind's runtime, if any — verify, don't guess). Do not weaken it to "report-only" without saying so explicitly.

### 2. Rotate refresh tokens on use
On each successful `refresh_access_token()` call: issue a NEW refresh token, persist it, and revoke/invalidate the one that was just used (`refresh_token_repo` already has `revoke_all_for_user` — check if a single-token revoke exists or add one, don't revoke all of a user's sessions on every refresh). Return the new refresh token in the response so the frontend can store it. Check `src/frontend/src/lib/api.ts` or wherever the refresh flow lives on the client side — it will need to save the new refresh token, not just the new access token.

## Acceptance criteria
- [ ] A response from the running app includes a `Content-Security-Policy` header — paste a real curl -I output
- [ ] Calling `/api/auth/refresh` twice with the SAME original refresh token: first call succeeds, second call FAILS (token was rotated out) — prove with two real calls and their outputs
- [ ] Frontend still logs in/refreshes/stays authenticated correctly after the change — verify manually or via the auth hook tests
- [ ] Full backend + frontend suites still green

## Deliver
`work/reports/wave-48/03-token-security-hygiene.report.md`. Commit before writing it.

## Constraints
- Time budget: 90 min · commit per item
- Do not revoke all of a user's active sessions on a single refresh — only the token just consumed
