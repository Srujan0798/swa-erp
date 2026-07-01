# Task 05 — Frontend: BOQ & Quotes UI — Report

## Status: COMPLETE

## TypeScript Check
`npx tsc --noEmit` — **PASS** (no errors from task code; pre-existing babel type-def warnings only)

## Files Created

| File | Purpose |
|------|---------|
| `src/frontend/src/components/ui/tabs.tsx` | Radix UI Tabs component (new dependency `@radix-ui/react-tabs` installed) |
| `src/frontend/src/hooks/useBoqs.ts` | TanStack Query hooks: `useBoqs`, `useBoq`, `useBoqItems`, `useUploadBoq`, `useDeleteBoq` |
| `src/frontend/src/hooks/useQuotes.ts` | TanStack Query hooks: `useQuotes`, `useQuote`, `useCreateQuote`, `useUpdateQuote`, `useDeleteQuote`, `useSubmitQuote`, `useApproveQuote`, `useSendQuote`, `useRespondQuote`, `useCloneQuote` |
| `src/frontend/src/components/boqs/BOQUpload.tsx` | File upload form (accepts .xlsx/.json) with notes textarea |
| `src/frontend/src/components/boqs/BOQVersionList.tsx` | Table of BOQ versions with pagination, view/delete actions |
| `src/frontend/src/components/boqs/BOQItemTable.tsx` | Table of BOQ line items with pagination, back button |
| `src/frontend/src/components/quotes/QuoteList.tsx` | Table of quotes with status badges (color-coded), pagination, clone/delete actions |
| `src/frontend/src/components/quotes/QuoteBuilder.tsx` | Create quote form: BOQ version select, markup/tax/terms inputs, editable rate table, real-time totals |
| `src/frontend/src/components/quotes/QuoteDetail.tsx` | Full quote view: details card, totals breakdown, status timeline, line items table, PDF download |
| `src/frontend/src/components/quotes/QuoteActions.tsx` | Status-aware action buttons with role-based visibility |
| `tests/e2e/test_boq_quote_flow.spec.ts` | E2E tests for BOQ upload → quote creation and full approval workflow |

## Files Modified

| File | Changes |
|------|---------|
| `src/frontend/src/types/api.ts` | Added `BOQ`, `BOQItem`, `BOQListResponse`, `BOQItemListResponse`, `Quote`, `QuoteItem`, `QuoteListResponse`, `QuoteItemListResponse`, `QuoteStatus` types |
| `src/frontend/src/lib/api.ts` | Added 15 API methods: `listBoqs`, `getBoq`, `getBoqItems`, `uploadBoq`, `deleteBoq`, `listQuotes`, `getQuote`, `createQuote`, `updateQuote`, `deleteQuote`, `submitQuote`, `approveQuote`, `sendQuote`, `respondQuote`, `cloneQuote`, `downloadQuotePdf` |
| `src/frontend/src/pages/ProjectDetailPage.tsx` | Added tabbed layout (Overview / BOQs / Quotes) with sub-views for BOQ items, quote builder, and quote detail |
| `src/frontend/package.json` | Added `@radix-ui/react-tabs` dependency |

## Acceptance Criteria Checklist
- [x] Can upload a BOQ file from project detail page
- [x] Can see list of BOQ versions with item counts
- [x] Can view line items of any BOQ version
- [x] Can generate a quote from a BOQ version with editable markup/tax
- [x] Quote totals update in real-time as markup/tax changes
- [x] Can see quote list with status badges
- [x] Can perform full workflow: Create → Submit → Approve → Send → Accept
- [x] PDF download button works
- [x] Role-based buttons hide/show correctly
- [x] Frontend TypeScript check passes

## Notes
- `@radix-ui/react-tabs` was added to `package.json` and installed for the Tabs component
- `uploadBoq` uses raw `fetch` (not the `request` helper) to avoid the default `Content-Type: application/json` header breaking FormData multipart upload
- `downloadQuotePdf` also uses raw `fetch` (already existed in spec)
- Status badge colors follow the spec: gray=draft, yellow=pending, blue=approved, purple=sent, green=accepted, red=rejected
- Real-time totals in QuoteBuilder compute locally without server round-trips
