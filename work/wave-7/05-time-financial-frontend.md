# Task 05 — Time + Financials Frontend UI

## Goal
Build the frontend pages and components for time tracking, timesheet management, invoicing, and project P&L. Uses React 18, TypeScript, TailwindCSS, shadcn/ui, and TanStack Query. Depends on Tasks 01-04 backend APIs.

Reference spec: `.specify/specs/wave-7/spec.md` section Frontend.

## Files to Create / Modify

### CREATE: `src/frontend/src/types/time.ts`
TypeScript types matching backend schemas:
```typescript
export interface TimeEntry {
  id: string;
  project_id: string;
  task_id: string | null;
  user_id: string;
  date: string;
  hours: number;
  description: string;
  is_billable: boolean;
  created_at: string;
  deleted_at: string | null;
  user_name?: string;
  project_name?: string;
}

export interface Timesheet {
  id: string;
  user_id: string;
  week_start: string;
  week_end: string;
  status: "draft" | "submitted" | "approved" | "rejected";
  total_hours: number;
  billable_hours: number;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  user_name?: string;
  approved_by_name?: string;
}
```

### CREATE: `src/frontend/src/types/financial.ts`
```typescript
export interface Invoice {
  id: string;
  project_id: string;
  invoice_number: string;
  status: "draft" | "sent" | "paid";
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  total: number;
  currency: string;
  due_date: string | null;
  notes: string | null;
  created_by: string;
  paid_at: string | null;
  created_at: string;
  items: InvoiceItem[];
  project_name?: string;
  created_by_name?: string;
}

export interface InvoiceItem {
  id: string;
  invoice_id: string;
  description: string;
  quantity: number;
  rate: number;
  amount: number;
  category: string | null;
  time_entry_id: string | null;
}

export interface ProjectPnL {
  project_id: string;
  project_name: string;
  total_revenue: number;
  total_costs: number;
  net_profit: number;
  margin_pct: number;
  cost_breakdown: CostBreakdownItem[];
}

export interface CostBreakdownItem {
  category: string;
  amount: number;
  count: number;
  percentage: number;
}
```

### CREATE: `src/frontend/src/hooks/useTimeEntries.ts`
TanStack Query hooks:
- `useTimeEntries(filters)` — GET /api/time-entries with query params
- `useCreateTimeEntry()` — POST mutation, invalidates list
- `useUpdateTimeEntry(id)` — PATCH mutation
- `useDeleteTimeEntry(id)` — DELETE mutation

### CREATE: `src/frontend/src/hooks/useTimesheets.ts`
- `useTimesheets(filters)` — GET /api/timesheets
- `useTimesheet(id)` — GET /api/timesheets/{id}
- `useGenerateTimesheet(weekStart)` — POST mutation
- `useSubmitTimesheet(id)` — POST mutation
- `useApproveTimesheet(id)` — POST mutation
- `useRejectTimesheet(id)` — POST mutation

### CREATE: `src/frontend/src/hooks/useInvoices.ts`
- `useProjectInvoices(projectId)` — GET /api/projects/{id}/invoices
- `useInvoice(id)` — GET /api/invoices/{id}
- `useCreateInvoice(projectId)` — POST mutation
- `useGenerateFromTime(projectId, startDate, endDate)` — POST mutation
- `useUpdateInvoiceStatus(id)` — PATCH mutation
- `useDeleteInvoice(id)` — DELETE mutation

### CREATE: `src/frontend/src/hooks/useProjectPnL.ts`
- `useProjectPnL(projectId)` — GET /api/projects/{id}/pnl
- `useProjectCosts(projectId, filters)` — GET /api/projects/{id}/costs
- `useAddProjectCost(projectId)` — POST mutation
- `useDeleteProjectCost(projectId, costId)` — DELETE mutation

### CREATE: `src/frontend/src/components/time/TimeEntryForm.tsx`
- Form fields: project (select), date (date picker), hours (number, step 0.25), description (textarea), is_billable (checkbox)
- Validation: hours 0.25-24, required fields
- Submit creates/updates entry
- Cancel resets form

### CREATE: `src/frontend/src/components/time/TimeEntryList.tsx`
- Table with columns: Date, Project, Hours, Description, Billable, Actions
- Filter by date range, project
- Inline actions: edit, delete
- Row highlighting for billable vs non-billable

### CREATE: `src/frontend/src/components/time/TimesheetView.tsx`
- Weekly calendar grid showing entries per day
- Totals row: total hours, billable hours
- Status badge (draft/submitted/approved/rejected)
- Action buttons based on status:
  - Draft: Submit, Edit entries
  - Submitted: (read-only for submitter)
  - Rejected: Re-submit, Edit entries
  - Approved: (locked, read-only)

### CREATE: `src/frontend/src/components/time/TimesheetSummary.tsx`
- Week selector (prev/next week arrows)
- Total hours, billable hours, non-billable hours
- Status with color coding
- Approve/Reject buttons (for managers)

### CREATE: `src/frontend/src/components/invoices/InvoiceList.tsx`
- Table: Invoice #, Project, Status, Total, Due Date, Actions
- Status badges with colors (draft=gray, sent=blue, paid=green)
- Filter by project, status

### CREATE: `src/frontend/src/components/invoices/InvoiceDetail.tsx`
- Invoice header: number, status, dates
- Line items table: description, qty, rate, amount
- Totals: subtotal, tax, total
- Action buttons: Send, Mark Paid (based on status)

### CREATE: `src/frontend/src/components/invoices/InvoiceForm.tsx`
- Form to create invoice manually
- Add line items dynamically
- Auto-calculate subtotal/tax/total
- Submit creates invoice

### CREATE: `src/frontend/src/components/pnl/ProjectPnLDashboard.tsx`
- Summary cards: Revenue, Costs, Net Profit, Margin %
- Cost breakdown bar chart (or simple table with progress bars)
- Revenue vs Costs comparison
- Cost category list with amounts and percentages

### CREATE: `src/frontend/src/components/pnl/CostEntryForm.tsx`
- Form to add manual cost entry
- Fields: category (select), description, amount, date
- Category options: material, vendor, overhead, other

### CREATE: `src/frontend/src/pages/TimeTrackingPage.tsx`
- Tab layout: "My Time" | "Timesheets"
- My Time tab: TimeEntryForm + TimeEntryList for current user
- Timesheets tab: TimesheetView + TimesheetSummary
- Week navigation

### CREATE: `src/frontend/src/pages/InvoicesPage.tsx`
- InvoiceList with project filter
- Create Invoice button → modal or new page
- Invoice detail view (route: /invoices/:id)

### CREATE: `src/frontend/src/pages/ProjectPnLPage.tsx`
- Takes project_id from route params
- ProjectPnLDashboard component
- CostEntryForm to add costs
- Cost list with delete action

### MODIFY: `src/frontend/src/pages/ProjectDetailPage.tsx`
Add a "Financials" tab that embeds ProjectPnLPage or links to it.

### MODIFY: `src/frontend/src/App.tsx` (or router file)
Add routes:
- `/time-tracking` → TimeTrackingPage
- `/invoices` → InvoicesPage
- `/invoices/:id` → InvoiceDetail (inline or separate page)
- `/projects/:id/pnl` → ProjectPnLPage

### MODIFY: `src/frontend/src/components/layout/Sidebar.tsx` (or navigation)
Add nav items:
- "Time Tracking" → /time-tracking
- "Invoices" → /invoices

## Files you must NOT touch
- `src/backend/` (all backend is Tasks 01-04)
- `src/frontend/src/hooks/useAuth.ts`
- `src/frontend/src/pages/LoginPage.tsx`

## Skills to use
- `tdd` — write component tests with Vitest + React Testing Library
- `code-review` — self-review before declaring done

## The core problem (inline)

### Component patterns
Follow existing patterns from `src/frontend/src/pages/`:
- Functional components with explicit return types
- TanStack Query for data fetching
- shadcn/ui components (Button, Card, Table, Dialog, Badge, etc.)
- TailwindCSS for styling

### API integration
All API calls go through hooks using `fetch` with auth headers from `useAuth`. Pattern:
```typescript
const api = useAuth();
const response = await fetch("/api/...", {
  headers: { Authorization: `Bearer ${api.token}` },
});
```

### Form patterns
Use controlled components with React state. Validation on submit. Show errors inline.

### Edge cases to handle
- Empty states: "No time entries this week", "No invoices yet"
- Loading states: skeletons or spinners
- Error states: toast notifications
- Optimistic updates for mutations
- Date formatting: use local date strings, not ISO

## Acceptance criteria (executable, not prose)
- [ ] `cd src/frontend && npx vitest run` passes
- [ ] `cd src/frontend && npx eslint src/` clean
- [ ] Time entry form creates entry, shows in list
- [ ] Weekly timesheet shows entries grouped by day with totals
- [ ] Submit timesheet updates status badge
- [ ] Invoice list shows all invoices with correct statuses
- [ ] Invoice detail shows line items and totals
- [ ] Generate invoice from time entries populates items
- [ ] P&L dashboard shows revenue, costs, profit, margin
- [ ] Cost breakdown shows categories with amounts
- [ ] Navigation includes Time Tracking and Invoices links
- [ ] All pages responsive (mobile-friendly)

## Test File
Create `src/frontend/src/__tests__/time-financials.test.tsx` with at least:
- `test_time_entry_form_renders` — form fields present
- `test_time_entry_list_shows_entries` — table renders
- `test_timesheet_view_shows_totals` — totals calculated
- `test_invoice_list_renders` — table with invoices
- `test_invoice_detail_shows_items` — line items present
- `test_pnl_dashboard_renders` — summary cards present
- `test_cost_breakdown_shows_categories` — categories listed

## How to deliver
1. Create all types, hooks, components, pages, routes + tests
2. Run `cd src/frontend && npx vitest run` — all pass
3. Run `cd src/frontend && npx eslint src/` — clean
4. Write report to `work/reports/wave-7/05-time-financial-frontend.report.md`
5. Stop

## Constraints
- Time budget: 60 min
- No new dependencies without flagging (use existing shadcn/ui components)
- Match existing patterns (see `src/frontend/src/pages/ProjectsPage.tsx`, `src/frontend/src/hooks/useDashboard.ts`)
- Allowed tools: `vitest`, `eslint`, `prettier`
