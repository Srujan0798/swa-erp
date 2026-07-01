# Task 04 — Compliance Frontend UI

## Goal
Build the compliance tracking UI: a dashboard per project showing progress per standard, a checklist view with status toggles, evidence upload linking to documents, a review workflow for auditors, and a compliance summary report.

## Files to Create / Modify

### 1. Types
Create `src/frontend/src/types/compliance.ts`:
```typescript
export interface ComplianceStandard {
  id: string;
  name: string;
  version: string;
  description: string | null;
}

export interface ComplianceChecklistItem {
  id: string;
  standard_id: string;
  category: string;
  requirement: string;
  description: string | null;
  is_mandatory: boolean;
}

export type ComplianceStatus = 'pending' | 'compliant' | 'non_compliant' | 'na';

export interface ProjectComplianceItem {
  id: string;
  project_id: string;
  checklist_item_id: string;
  status: ComplianceStatus;
  evidence_document_id: string | null;
  notes: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  standard_name: string;
  category: string;
  requirement: string;
  is_mandatory: boolean;
}

export interface ComplianceDashboardStandard {
  standard_name: string;
  total_items: number;
  compliant_count: number;
  non_compliant_count: number;
  pending_count: number;
  na_count: number;
  compliance_percentage: number;
}

export interface ComplianceSummary {
  project_id: string;
  standards: ComplianceDashboardStandard[];
  overall_percentage: number;
}
```

### 2. API hook
Create `src/frontend/src/hooks/useCompliance.ts`:
```typescript
// Uses TanStack Query
export function useComplianceSummary(projectId: string) — GET /api/projects/{projectId}/compliance/summary
export function useComplianceItems(projectId: string, standardId?: string) — GET /api/projects/{projectId}/compliance/items?standard_id=...
export function useUpdateComplianceItem() — mutation: PATCH /api/compliance/items/{itemId}
export function useReviewComplianceItem() — mutation: POST /api/compliance/items/{itemId}/review
export function useStandards() — GET /api/compliance/standards
export function useChecklistItems(standardId: string) — GET /api/compliance/standards/{standardId}/checklist
export function useBulkCreateItems(projectId: string) — mutation: POST /api/projects/{projectId}/compliance/items/bulk/{standardId}
```

### 3. Components
Create the following in `src/frontend/src/components/compliance/`:

**ComplianceDashboard.tsx** — Main dashboard component for a project
- 4 cards (one per standard: NBC, ECBC, IGBC, IS) showing:
  - Standard name and version
  - Progress bar (compliant_count / total_items)
  - Breakdown: green (compliant), red (non-compliant), yellow (pending), gray (N/A)
  - Click to expand into checklist view
- Overall compliance percentage at top
- "Initialize Compliance" button (if not yet initialized)

**ComplianceChecklist.tsx** — Checklist view for a single standard
- Table with columns: Requirement, Category, Mandatory, Status, Evidence, Actions
- Status column: toggle buttons or dropdown (Pending / Compliant / Non-Compliant / N/A)
- Evidence column: link to document (opens document picker or shows linked doc name)
- Notes column: inline editable text
- Review column: shows reviewer name + date if reviewed, "Review" button for auditors
- Filter by status (All, Pending, Compliant, Non-Compliant, N/A)

**ComplianceStatusToggle.tsx** — Reusable status toggle component
- 4-state toggle: Pending (gray), Compliant (green), Non-Compliant (red), N/A (blue)
- Calls useUpdateComplianceItem on change

**ComplianceEvidenceLink.tsx** — Evidence document picker
- Shows current evidence document name (if linked)
- "Link Document" button opens a modal listing project documents
- Select a document to link as evidence
- "Unlink" button to remove evidence

**ComplianceReviewButton.tsx** — Review action for auditors
- Only visible to users with auditor role
- Shows "Reviewed by [name] on [date]" if already reviewed
- "Approve" / "Mark Reviewed" button
- Optional review notes input

**ComplianceSummaryReport.tsx** — Printable summary
- Table of all standards with counts
- Overall percentage
- List of non-compliant items (flagged)
- Print-friendly styling

### 4. Page
Create `src/frontend/src/pages/CompliancePage.tsx`:
- Route: `/projects/:projectId/compliance`
- Renders `ComplianceDashboard` inside project layout
- Includes breadcrumb: Projects > [Project Name] > Compliance

### 5. Navigation
Modify `src/frontend/src/components/Layout.tsx` or sidebar to add:
- "Compliance" link in project detail navigation (alongside Documents, BOQ, Tasks)

### 6. Router
Modify `src/frontend/src/App.tsx` to add:
- Route for `/projects/:projectId/compliance` → `CompliancePage`

## Files you must NOT touch
- `src/backend/` — no backend changes
- `src/frontend/src/pages/DashboardPage.tsx` — no changes
- `tests/wave-6/` — backend tests

## Skills to use
- `code-review` — self-review before declaring done

## The core problem (inline — no external context needed)
The compliance UI reads from the compliance API (task 03 backend) and displays progress per building code standard. Users update status inline, link evidence documents, and auditors review items. The dashboard is the entry point; clicking a standard shows its checklist.

### Edge cases to handle
- No compliance initialized yet → show "Initialize" button with explanation
- Empty checklist items → show "No items. Run initialization."
- Document picker shows empty if no documents uploaded yet
- Non-auditor users see review status but not the review button
- Status changes should optimistic-update then rollback on error

## Acceptance criteria (executable, not prose)
- [ ] CompliancePage renders at `/projects/:projectId/compliance`
- [ ] Dashboard shows 4 standard cards with progress bars
- [ ] Clicking a standard opens checklist view
- [ ] Status can be toggled inline (Pending → Compliant → Non-Compliant → N/A)
- [ ] Evidence can be linked to a document
- [ ] Auditor can review items (button visible only for auditor role)
- [ ] Summary report shows overall compliance percentage
- [ ] `npx tsc --noEmit` passes (TypeScript strict)
- [ ] `npx eslint src/` clean

## How to deliver
1. Create types, hooks, components, page
2. Update router and navigation
3. Run `npx tsc --noEmit`
4. Run `npx eslint src/`
5. Write report to `work/reports/wave-6/04-compliance-frontend.report.md`
6. Use `work/REPORT_TEMPLATE.md`
7. Stop

## Constraints
- Time budget: 25 min
- No new dependencies without flagging
- Match existing patterns (see `src/frontend/src/pages/ProjectDetailPage.tsx`, `src/frontend/src/hooks/`)
- Use shadcn/ui components (Button, Card, Table, Badge, Dialog, Progress)
- Use TanStack Query for data fetching
- Allowed tools: Read, Edit, Write, Bash, Glob, Grep
