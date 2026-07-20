# Task 01 — Dead code cleanup and missing UI wiring (found by 2026-07-21 full-project audit)

## What to do
Clean up confirmed dead code and wire up confirmed missing frontend functionality. Each item has
a file:line citation from a full-codebase audit — verify then fix, don't re-derive from scratch.

## Files to modify
- MODIFY: `src/backend/api/tasks.py` (remove dead debug endpoint)
- DELETE: `src/frontend/src/pages/TasksBoardPage.tsx` (confirmed unreferenced anywhere)
- MODIFY: `src/frontend/src/pages/UsersPage.tsx` (fix broken "New User" button, add delete-user UI)
- MODIFY: `src/frontend/src/pages/ClientDetailPage.tsx` (add client-delete UI, admin-gated)
- MODIFY: wherever `TokensList.tsx` and `DocumentReferenceList.tsx` should actually be rendered
  (investigate first — see below)
- MODIFY: `src/backend/api/notifications.py` (un-stub the handlers)
- MODIFY: `src/frontend/src/hooks/` + relevant page/component to actually call the notifications
  API (investigate whether a notifications UI exists anywhere or needs to be added)
- MODIFY: `src/backend/models/document.py` (remove the dead, never-used `deleted_at` column — OR
  wire it up consistently with every other module's soft-delete pattern; pick one, see below)

## Files you must NOT touch
- Anything already covered by wave-22 (RBAC) or wave-23 (correctness) — this task is UI wiring
  and dead-code removal only, not security or business-logic fixes

## The core problem (inline)

### 1. Dead debug endpoint
`src/backend/api/tasks.py:200-210`, `GET .../tasks/{task_id}/debug` duplicates the regular
task-read endpoint, confirmed unused by any frontend caller. Remove it entirely (route,
handler, and its test if one exists solely for it).

### 2. Dead frontend page
`src/frontend/src/pages/TasksBoardPage.tsx` is never imported anywhere (`TasksPage.tsx` uses
`KanbanBoard` directly instead). Confirm this with a fresh grep before deleting (audits can be
wrong; verify), then delete the file if truly unreferenced.

### 3. "New User" button does nothing
`src/frontend/src/pages/UsersPage.tsx` line ~8/21: `useCreateUser()` is called but its returned
mutation object is never bound to a variable or wired to the button's `onClick`. Fix: actually
wire the button to open a create-user form/dialog (check how other "New X" buttons in this
codebase are implemented — e.g. `NewClientPage.tsx`/`NewVendorPage.tsx` pattern — and follow
the same UX convention) and call the mutation on submit.

### 4. No delete-user or delete-client UI
Both `api.deleteUser` (via `useDeleteUser` hook) and `api.deleteClient` exist and work on the
backend but have zero UI callers. Add a delete action to `UsersPage.tsx` (admin-only, matches
backend gating) and `ClientDetailPage.tsx` (admin-only). Follow the existing delete-confirmation
UX pattern already used elsewhere in the app (check how vendor or project deletion, if any UI
exists for those, handles confirmation — don't invent a new pattern).

### 5. Tokens and Document References are unreachable in the running app
`src/frontend/src/components/tokens/TokensList.tsx` and
`src/frontend/src/components/documentRefs/DocumentReferenceList.tsx` are fully built, fully
wired to working hooks/API, but never imported by any page or parent component — confirmed by
grep, zero references outside their own files. This means two core-chain features (built in
wave-9) are completely invisible in the actual UI despite working end to end via API.
Investigate: these were originally meant to be nested under an Agreement (for Tokens) and a
Project (for DocumentReferences) per `work/wave-9/04-chain-frontend.md`'s original design. Find
where `AgreementsTab.tsx` (or equivalent) and the Project detail page currently stand, and
actually mount these list components in the right place so they're reachable through normal
navigation — this is the fix, not a redesign.

### 6. Notifications: stub handlers, zero frontend
`src/backend/api/notifications.py`: `list_notifications` always `return []` (never queries
`NotificationRepository`, despite the repository existing and being correct per earlier audits),
and `mark_read` always `return {}` without persisting anything. Fix both handlers to actually
use `NotificationRepository`. Then add minimal frontend wiring — at minimum a notifications
bell/dropdown in the top nav (check `src/frontend/src/components/layout/` for where a
reasonable mount point is) that calls the now-working list endpoint and lets a user mark one
read. Keep this minimal — a working list + mark-read is the goal, not a rich notifications UX.

### 7. Document model's dead `deleted_at` column
`src/backend/models/document.py` has a `deleted_at` column that's never read or written
anywhere — the actual delete mechanism uses a different `is_active` flag instead
(`api/documents.py`). Pick ONE approach and document why in the report:
- **Option A (recommended, lower risk)**: remove the dead `deleted_at` column via a migration,
  since `is_active` already works and is exercised by tests — don't maintain two competing
  soft-delete mechanisms
- **Option B**: migrate `documents` to use `deleted_at` like every other module, deprecating
  `is_active` — higher risk, touches more callers, only do this if Option A turns out to be
  blocked by something during implementation (e.g. `is_active` is used for a different, genuine
  purpose beyond soft-delete — check before assuming)

## Acceptance criteria
- [ ] Dead debug endpoint removed, no test references it
- [ ] `TasksBoardPage.tsx` removed (after confirming zero references)
- [ ] "New User" button opens a working create-user flow, verified against a running backend
- [ ] Admin can delete a user and a client from the UI (with confirmation), verified against a running backend
- [ ] Tokens list is reachable via normal navigation (Client → Agreement → Tokens), verified in browser
- [ ] Document References list is reachable via normal navigation (Project → Document References), verified in browser
- [ ] `GET` on the notifications endpoint returns real data for the current user, not `[]` unconditionally
- [ ] A minimal notifications UI exists and successfully lists + marks-read against the live API
- [ ] Document's dead `deleted_at` situation is resolved one way or the other, not left ambiguous
- [ ] `python3 -m pytest tests/ -q` — 324+ pass — **run with no other pytest process active and
  a freshly reset test DB**
- [ ] `npm run typecheck` and `npm run lint` — clean
- [ ] `ruff check` on touched backend files — clean

## How to deliver
1. Fix all 7 items
2. Verify each UI change in an actual running browser against `make dev` or the docker stack,
   not just typecheck-clean
3. Run every acceptance check
4. Write report to `work/reports/wave-24/01-dead-code-and-ui-wiring.report.md`, include
   screenshots or a clear description of what you clicked through to verify
5. Stop

## Constraints
- Time budget: 150 min — this is the largest task in this wave set, budget accordingly
- Match existing UX patterns exactly rather than inventing new ones
- Allowed tools: file edit, npm, browser, pytest, ruff
