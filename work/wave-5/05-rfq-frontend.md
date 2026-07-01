# Task 05 — RFQ UI (Request for Quotation)

## Goal
Build the RFQ frontend workflow: create RFQs from projects, manage RFQ lifecycle, record vendor responses, compare quotes across vendors, and award to selected vendor.

## Files to Create/Modify

### 1. Types
Create `src/frontend/src/types/rfq.ts`:
```typescript
export type RFQStatus = "draft" | "sent" | "responded" | "compared" | "awarded" | "closed" | "cancelled";

export interface RFQ {
  id: string;
  project_id: string;
  vendor_id: string;
  vendor_name: string;
  status: RFQStatus;
  rfq_number: string;
  created_by: string;
  created_by_name: string;
  sent_at?: string;
  responded_at?: string;
  awarded_at?: string;
  notes?: string;
  created_at: string;
  items: RFQItem[];
}

export interface RFQItem {
  id: string;
  material_id: string;
  material_name: string;
  material_unit: string;
  quantity: number;
  vendor_rate?: number;
  notes?: string;
}

export interface RFQCompareItem {
  material_id: string;
  material_name: string;
  unit: string;
  quantity: number;
  vendor_rates: {
    rfq_id: string;
    vendor_id: string;
    vendor_name: string;
    rate: number;
  }[];
}
```

### 2. API Hooks
Create `src/frontend/src/hooks/use-rfqs.ts`:
- `useProjectRFQs(projectId, params)` — query GET /api/projects/{project_id}/rfqs with status filter
- `useRFQ(rfqId)` — query GET /api/rfqs/{id}
- `useCreateRFQ()` — mutation POST /api/projects/{project_id}/rfqs
- `useSendRFQ()` — mutation POST /api/rfqs/{id}/send
- `useRespondRFQ()` — mutation POST /api/rfqs/{id}/respond
- `useAwardRFQ()` — mutation POST /api/rfqs/{id}/award
- `useCloseRFQ()` — mutation POST /api/rfqs/{id}/close
- `useCancelRFQ()` — mutation POST /api/rfqs/{id}/cancel
- `useCompareRFQs(projectId, materialIds)` — query GET /api/projects/{project_id}/rfqs/compare

### 3. RFQ List Page
Create `src/frontend/src/pages/rfqs/rfq-list.tsx`:
- Accessible from project detail page (tab or section)
- Table: RFQ #, Vendor, Status (badge color), Items Count, Created, Actions
- Status filter tabs: All, Draft, Sent, Responded, Awarded, Closed
- "Create RFQ" button
- Click row → RFQ detail

### 4. RFQ Create Form
Create `src/frontend/src/pages/rfqs/rfq-create.tsx`:
- Step 1: Select vendor (dropdown, searchable)
- Step 2: Add materials (search + select, quantity input)
  - Material search from materials catalog
  - Add multiple items
  - Each item: material name, unit, quantity, notes
- Step 3: Review and submit
- Pre-fill materials from project BOQ if available

### 5. RFQ Detail Page
Create `src/frontend/src/pages/rfqs/rfq-detail.tsx`:
- Header: RFQ #, Vendor, Status badge, Project link
- Items table: Material, Unit, Qty, Vendor Rate, Total
- Status-dependent action buttons:
  - DRAFT: [Send] [Edit] [Cancel]
  - SENT: [Record Response] [Cancel]
  - RESPONDED: [Compare] [Close]
  - COMPARED: [Award] [Close]
  - AWARDED: [Close]
  - CLOSED/CANCELLED: (read-only)
- Notes section
- Timestamps: Created, Sent, Responded, Awarded

### 6. Vendor Response Form
Create `src/frontend/src/pages/rfqs/rfq-response.tsx`:
- Dialog or page to record vendor's quoted rates
- Table: Material, Qty, [Rate input], Notes
- Auto-fill rate from previous responses if available
- Submit updates all vendor_rate fields

### 7. Comparison View
Create `src/frontend/src/pages/rfqs/rfq-compare.tsx`:
- Triggered from project level: "Compare RFQs" button
- Shows all RFQs for project that are RESPONDED or COMPARED
- Table: Material | Qty | Vendor A Rate | Vendor B Rate | ... | Best Price
- Highlight lowest rate per material row
- Total row per vendor
- "Award" button under each vendor column
- Visual indicator for best overall vendor (lowest total)

### 8. Award Confirmation
Create `src/frontend/src/pages/rfqs/rfq-award-dialog.tsx`:
- Confirmation dialog before awarding
- Shows: vendor name, total amount, item count
- Confirm → calls award endpoint
- Success → navigate to RFQ detail with updated status

### 9. Project Integration
Modify `src/frontend/src/pages/projects/project-detail.tsx`:
- Add "RFQs" tab or section
- Shows RFQ list for this project
- "Create RFQ" button
- "Compare Vendors" button (navigates to comparison view with project's RFQs)

### 10. Router
Modify `src/frontend/src/App.tsx` or router config:
- `/projects/:projectId/rfqs` → RFQList
- `/projects/:projectId/rfqs/new` → RFQCreate
- `/rfqs/:rfqId` → RFQDetail
- `/rfqs/:rfqId/respond` → RFQResponse
- `/projects/:projectId/rfqs/compare` → RFQCompare

## Files you must NOT touch
- `src/frontend/src/pages/vendors/` (Task 04)
- `src/frontend/src/pages/materials/` (Task 04)
- `src/frontend/src/hooks/use-vendors.ts`, `use-materials.ts` (Task 04)

## Acceptance Criteria
- [ ] `pytest tests/wave-5/test_rfq_frontend.py` passes (or vitest)
- [ ] `npm run lint` clean
- [ ] `npm run typecheck` passes
- [ ] Can create RFQ from project: select vendor, add materials with quantities
- [ ] RFQ list shows correct status badges with colors
- [ ] Status transitions reflected in UI (buttons change based on status)
- [ ] Can record vendor response with rates per item
- [ ] Comparison view shows side-by-side rates with best price highlighted
- [ ] Award confirmation dialog shows totals before confirming
- [ ] Project detail page has RFQ section
- [ ] All mutations invalidate relevant queries for fresh data

## Test File
Create `tests/wave-5/test_rfq_frontend.test.tsx` with at least:
- `test_rfq_list_renders` — renders table with RFQ data
- `test_rfq_status_badges` — correct colors per status
- `test_rfq_create_form` — renders vendor select and material inputs
- `test_rfq_detail_shows_items` — items table renders
- `test_rfq_action_buttons_by_status` — correct buttons per status
- `test_rfq_compare_renders` — comparison table with vendor columns
- `test_rfq_award_dialog` — confirmation dialog renders with totals

## Notes
- Status badge colors: draft=gray, sent=blue, responded=yellow, compared=purple, awarded=green, closed=gray, cancelled=red
- Use existing shadcn/ui components: Table, Badge, Button, Dialog, Select, Tabs, Card
- Material selection in RFQ create: searchable dropdown, fetch from /api/materials
- Comparison view can reuse VendorComparison component from Task 04 or create dedicated RFQ-specific one
- Consider URL state for filters (status, search) in RFQ list
- Optimistic updates for status transitions for better UX
