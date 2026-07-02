# Task 05 — Frontend: BOQ & Quotes UI

## Goal
Build the frontend UI for BOQ upload, version browsing, quote builder, and quote approval workflow. Integrate into existing project detail page.

## Files to Create/Modify

### 1. API Types
Extend `src/frontend/src/types/api.ts`:
```typescript
export interface BOQ {
  id: string;
  project_id: string;
  version_number: number;
  file_name: string;
  file_path: string;
  parsed_by_name: string | null;
  parsed_at: string;
  notes: string | null;
  item_count?: number;
}

export interface BOQItem {
  id: string;
  boq_id: string;
  line_number: number;
  category: string | null;
  description: string;
  specification: string | null;
  unit: string;
  quantity: number;
  rate: number;
  amount: number;
}

export interface BOQListResponse {
  items: BOQ[];
  total: number;
  page: number;
  page_size: number;
}

export interface Quote {
  id: string;
  project_id: string;
  boq_id: string;
  version_number: number;
  status: QuoteStatus;
  subtotal: number;
  markup_percent: number;
  markup_amount: number;
  tax_percent: number;
  tax_amount: number;
  total_amount: number;
  terms: string | null;
  validity_days: number;
  valid_until: string | null;
  created_by_name: string | null;
  approved_by_name: string | null;
  approved_at: string | null;
  sent_at: string | null;
  client_response: string | null;
  client_response_at: string | null;
  client_response_notes: string | null;
  created_at: string;
}

export type QuoteStatus = "draft" | "pending_approval" | "approved" | "sent" | "accepted" | "rejected";

export interface QuoteItem {
  id: string;
  quote_id: string;
  line_number: number;
  category: string | null;
  description: string;
  specification: string | null;
  unit: string;
  quantity: number;
  rate: number;
  amount: number;
}

export interface QuoteListResponse {
  items: Quote[];
  total: number;
  page: number;
  page_size: number;
}
```

### 2. API Methods
Extend `src/frontend/src/lib/api.ts`:
```typescript
listBoqs: (projectId: string, params?: { page?: number; page_size?: number }) =>
  request<BOQListResponse>(`/api/projects/${projectId}/boqs?...`)
getBoq: (id: string) => request<BOQ>(`/api/boqs/${id}`)
getBoqItems: (id: string, params?: { page?: number; page_size?: number }) =>
  request<{ items: BOQItem[]; total: number; page: number; page_size: number }>(`/api/boqs/${id}/items?...`)
uploadBoq: (projectId: string, file: File, notes?: string) => {
  const form = new FormData();
  form.append("file", file);
  if (notes) form.append("notes", notes);
  return request<BOQ>(`/api/projects/${projectId}/boqs`, { method: "POST", body: form });
}
deleteBoq: (id: string) => request<void>(`/api/boqs/${id}`, { method: "DELETE" })

listQuotes: (projectId: string, params?: { page?: number; page_size?: number }) =>
  request<QuoteListResponse>(`/api/projects/${projectId}/quotes?...`)
getQuote: (id: string) => request<Quote>(`/api/quotes/${id}`)
createQuote: (projectId: string, data: { boq_id: string; markup_percent?: number; tax_percent?: number; terms?: string; validity_days?: number }) =>
  request<Quote>(`/api/projects/${projectId}/quotes`, { method: "POST", body: JSON.stringify(data) })
updateQuote: (id: string, data: Partial<Quote>) =>
  request<Quote>(`/api/quotes/${id}`, { method: "PATCH", body: JSON.stringify(data) })
deleteQuote: (id: string) => request<void>(`/api/quotes/${id}`, { method: "DELETE" })
submitQuote: (id: string) => request<Quote>(`/api/quotes/${id}/submit`, { method: "POST" })
approveQuote: (id: string) => request<Quote>(`/api/quotes/${id}/approve`, { method: "POST" })
sendQuote: (id: string) => request<Quote>(`/api/quotes/${id}/send`, { method: "POST" })
respondQuote: (id: string, data: { response: "accepted" | "rejected"; notes?: string }) =>
  request<Quote>(`/api/quotes/${id}/respond`, { method: "POST", body: JSON.stringify(data) })
cloneQuote: (id: string) => request<Quote>(`/api/quotes/${id}/clone`, { method: "POST" })
downloadQuotePdf: (id: string) =>
  fetch(`/api/quotes/${id}/pdf`, { headers: { Authorization: `Bearer ${getAccessToken()}` } })
```

### 3. Hooks
Create `src/frontend/src/hooks/useBoqs.ts`:
- `useBoqs(projectId, page?, pageSize?)`
- `useBoq(boqId)`
- `useBoqItems(boqId, page?, pageSize?)`
- `useUploadBoq()` — mutation
- `useDeleteBoq()` — mutation

Create `src/frontend/src/hooks/useQuotes.ts`:
- `useQuotes(projectId, page?, pageSize?)`
- `useQuote(quoteId)`
- `useCreateQuote()` — mutation
- `useUpdateQuote()` — mutation
- `useDeleteQuote()` — mutation
- `useSubmitQuote()` — mutation
- `useApproveQuote()` — mutation
- `useSendQuote()` — mutation
- `useRespondQuote()` — mutation
- `useCloneQuote()` — mutation

### 4. Components

Create `src/frontend/src/components/boqs/BOQUpload.tsx`:
- File input (accept .xlsx, .json)
- Notes textarea
- Upload button with loading state
- Success/error feedback

Create `src/frontend/src/components/boqs/BOQVersionList.tsx`:
- Table of versions: Version #, File Name, Items, Parsed By, Date, Actions (View, Delete)
- Pagination

Create `src/frontend/src/components/boqs/BOQItemTable.tsx`:
- Table of line items: Line #, Category, Description, Spec, Unit, Qty, Rate, Amount
- Pagination
- Optional: category filter

Create `src/frontend/src/components/quotes/QuoteList.tsx`:
- Table of quotes: Quote #, Status (badge), Subtotal, Total, Valid Until, Actions
- Status badge colors: draft=gray, pending=yellow, approved=blue, sent=purple, accepted=green, rejected=red
- Actions per row based on status and user role

Create `src/frontend/src/components/quotes/QuoteBuilder.tsx`:
- Form to create quote from a BOQ version
- Select BOQ version dropdown
- Markup % input (default 15)
- Tax % input (default 18)
- Terms textarea
- Validity days input (default 30)
- Preview table of items with editable rates
- Real-time totals preview: Subtotal + Markup + Tax = Total
- "Create Quote" button

Create `src/frontend/src/components/quotes/QuoteDetail.tsx`:
- Full quote view with all fields
- Item table
- Totals breakdown card
- Terms & conditions
- Status timeline: Created → Submitted → Approved → Sent → [Accepted/Rejected]
- Action buttons based on status + role:
  - Draft: Edit, Submit
  - Pending: Approve (admin only), Reject to Draft
  - Approved: Send
  - Sent: Record Response (Accept/Reject)
  - Rejected: Clone to Draft

Create `src/frontend/src/components/quotes/QuoteActions.tsx`:
- Small component with status-aware action buttons
- Uses current user role to show/hide buttons

### 5. Pages
Modify `src/frontend/src/pages/ProjectDetailPage.tsx` (or create if not existing):
- Add tabs: Overview | BOQs | Quotes
- BOQ tab: BOQUpload + BOQVersionList
- Quote tab: QuoteList + button to create new quote
- Clicking a quote opens QuoteDetail (could be inline or modal)

### 6. Routing
Ensure project detail page has tabs or sections for BOQs and Quotes.

## Acceptance Criteria
- [ ] Can upload a BOQ file from project detail page
- [ ] Can see list of BOQ versions with item counts
- [ ] Can view line items of any BOQ version
- [ ] Can generate a quote from a BOQ version with editable markup/tax
- [ ] Quote totals update in real-time as markup/tax changes
- [ ] Can see quote list with status badges
- [ ] Can perform full workflow: Create → Submit → Approve → Send → Accept
- [ ] PDF download button works
- [ ] Role-based buttons hide/show correctly
- [ ] Frontend lint and build pass

## E2E Tests
Create `tests/e2e/test_boq_quote_flow.spec.ts`:
- `admin can upload BOQ and generate quote` — full flow
- `quote approval workflow` — submit, approve, send, accept

## Notes
- Use shadcn/ui `Tabs` component for project detail page sections
- Use `Badge` component for quote status colors
- Use `Dialog` or `Sheet` for quote builder/detail
- Real-time totals: compute in React state, don't round-trip to server
- For rate editing in quote builder, use `onChange` handlers on each row's rate input
- Keep the UI simple and functional — polish can come later