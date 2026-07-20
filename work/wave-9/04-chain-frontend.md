# Task 04 — Frontend for Inquiry → Agreement → Token → Document Reference chain

## What to do
Build the UI for the new chain: Inquiries list + detail + "Convert to Client" action;
Agreements tab on Client detail page; Tokens list scoped to an Agreement; Document References
list scoped to a Token. Follow existing patterns from `src/frontend/src/pages/ClientsPage.tsx`
and `src/frontend/src/components/clients/`.

**Depends on Tasks 01-03 being merged** (needs the live API contracts). If those endpoints
aren't ready yet, build against the schemas documented in Tasks 01-03 and mock the API client
functions, then wire up once merged.

## Files to create
- CREATE: `src/frontend/src/pages/InquiriesPage.tsx`
- CREATE: `src/frontend/src/pages/InquiryDetailPage.tsx`
- CREATE: `src/frontend/src/components/inquiries/InquiryForm.tsx`
- CREATE: `src/frontend/src/components/inquiries/ConvertToClientButton.tsx`
- CREATE: `src/frontend/src/components/agreements/AgreementsTab.tsx` (mounted on ClientDetail)
- CREATE: `src/frontend/src/components/agreements/AgreementForm.tsx`
- CREATE: `src/frontend/src/components/tokens/TokensList.tsx`
- CREATE: `src/frontend/src/components/tokens/TokenForm.tsx`
- CREATE: `src/frontend/src/components/documentRefs/DocumentReferenceList.tsx`
- CREATE: `src/frontend/src/components/documentRefs/DocumentReferenceForm.tsx`
- CREATE: `src/frontend/src/hooks/useInquiries.ts`, `useAgreements.ts`, `useTokens.ts`, `useDocumentReferences.ts` (TanStack Query, follow `useClients.ts` pattern)

## Files to modify
- MODIFY: `src/frontend/src/App.tsx` — add routes `/inquiries`, `/inquiries/:id`
- MODIFY: `src/frontend/src/components/layout/Sidebar.tsx` — add "Inquiries" nav item
- MODIFY: `src/frontend/src/components/clients/ClientDetail.tsx` (or equivalent) — mount `AgreementsTab`
- MODIFY: `src/frontend/src/lib/api.ts` — add API client functions for all 4 new resources
- MODIFY: `src/frontend/src/types/api.ts` — add TS types matching backend schemas from Tasks 01-03

## Files you must NOT touch
- `src/backend/`
- Existing routes/components for clients/projects/tasks beyond the ClientDetail mount point above

## The core problem (inline)
This is standard CRUD UI following the codebase's existing TanStack Query + shadcn/ui pattern.
Key UX requirements from the domain:
- Inquiry list shows status badges (New/Contacted/Converted/Dropped); "Convert" action opens a
  dialog, NOT a direct one-click action — per the corrected backend flow (Task 01), conversion
  first checks for an existing Client match by name. If the API returns an ambiguous/no-match
  response, the dialog must let the user either pick an existing Client from a list or confirm
  creating a new one, then always ends by creating a Project. On success, navigate to the new
  Project's detail page (not a Client page — the flow always ends at Project, per the client's
  own description of the process).
- Agreements tab (mounted on Client detail) shows `reference_id` (e.g. `SWA-2025-SA-011`) +
  `service_name` (free text, not a fixed dropdown — see ADR-0002, the agreement type list isn't
  confirmed) + start/end date + status; "New Agreement" form.
- Tokens list is nested under an Agreement (breadcrumb: Client > Agreement > Tokens); shows
  `reference_id` (`SWA-2025-TKN-NNN`) prominently since that's the number staff actually reference.
- Document References list shows under a Project, with an optional Token filter (a
  DocumentReference belongs to a Project always, and optionally to a Token — see Task 03); shows
  `document_type` (free text, e.g. "DBR"/"KDR"/"Concept Note") + `reference_id` + revision + status.

## Acceptance criteria
- [ ] `npm run typecheck` (or `tsc --noEmit`) clean
- [ ] `npm run lint` clean
- [ ] Manual flow works end-to-end against a running backend: create Inquiry → Convert → land
  on Client → add Agreement → add Token → add Document Reference
- [ ] No console errors in browser dev tools during the flow above

## How to deliver
1. Implement pages/components/hooks
2. Run typecheck + lint
3. Start `make dev`, walk the flow in a browser, screenshot the Inquiries list and one detail page
4. Write report to `work/reports/wave-9/04-chain-frontend.report.md` (include screenshot paths)
5. Stop

## Constraints
- Time budget: 90 min
- Match existing shadcn/ui component usage — don't introduce a new UI kit
- Allowed tools: file edit, npm/vite, browser
