# Task 05 — Clients + Projects UI (Frontend)

## What to do
Build the list pages, detail pages, and create/edit forms for Clients and Projects. Include search, pagination, and status filters.

## Files to create
- CREATE: `src/frontend/src/components/ui/dialog.tsx` (shadcn dialog for modals)
- CREATE: `src/frontend/src/components/ui/select.tsx` (shadcn select for dropdowns)
- CREATE: `src/frontend/src/components/ui/textarea.tsx` (shadcn textarea)
- CREATE: `src/frontend/src/components/clients/ClientForm.tsx` (create/edit client form)
- CREATE: `src/frontend/src/components/clients/ClientList.tsx` (table with search/pagination)
- CREATE: `src/frontend/src/components/clients/ContactForm.tsx` (add/edit contact inline)
- CREATE: `src/frontend/src/components/projects/ProjectForm.tsx` (create/edit project form)
- CREATE: `src/frontend/src/components/projects/ProjectList.tsx` (table with search/status filter/pagination)
- CREATE: `src/frontend/src/components/projects/ProjectDetail.tsx` (detail view with lifecycle actions)
- CREATE: `src/frontend/src/pages/ClientsPage.tsx`
- CREATE: `src/frontend/src/pages/ClientDetailPage.tsx`
- CREATE: `src/frontend/src/pages/ProjectsPage.tsx`
- CREATE: `src/frontend/src/pages/ProjectDetailPage.tsx`
- CREATE: `src/frontend/src/pages/NewProjectPage.tsx`
- CREATE: `src/frontend/src/pages/NewClientPage.tsx`
- CREATE: `tests/e2e/test_clients_projects.spec.ts`

## Files to modify
- MODIFY: `src/frontend/src/App.tsx` — add routes for new pages
- MODIFY: `src/frontend/src/components/layout/Sidebar.tsx` — ensure /clients and /projects links exist
- MODIFY: `src/frontend/src/types/api.ts` — add Client, Contact, Project, ProjectStatus types

## Files you must NOT touch
- `src/backend/` (other tasks)
- `src/frontend/src/pages/LoginPage.tsx`, `DashboardPage.tsx` (existing)

## The core problem (inline)

### Routes to add (`App.tsx`)
```tsx
<Route path="/clients" element={<ClientsPage />} />
<Route path="/clients/:id" element={<ClientDetailPage />} />
<Route path="/clients/new" element={<NewClientPage />} />
<Route path="/projects" element={<ProjectsPage />} />
<Route path="/projects/:id" element={<ProjectDetailPage />} />
<Route path="/projects/new" element={<NewProjectPage />} />
```

### API types to add (`types/api.ts`)
```typescript
export type ProjectStatus =
  | "Lead" | "Quote" | "Awarded" | "Design"
  | "Vendor" | "Execution" | "Validation" | "Closed";

export interface Client {
  id: string;
  name: string;
  code: string;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
  country: string;
  gst_number?: string;
  primary_email: string;
  primary_phone?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  contacts: Contact[];
}

export interface Contact {
  id: string;
  client_id: string;
  name: string;
  email: string;
  phone?: string;
  designation?: string;
  is_primary: boolean;
}

export interface Project {
  id: string;
  client_id: string;
  name: string;
  code: string;
  description?: string;
  status: ProjectStatus;
  pm_id?: string;
  designer_id?: string;
  auditor_id?: string;
  location?: string;
  estimated_value?: number;
  actual_value?: number;
  start_date?: string;
  target_end_date?: string;
  actual_end_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  client_name?: string;
  pm_name?: string;
  designer_name?: string;
  auditor_name?: string;
}
```

### ClientsPage
- Search input (debounced, 300ms)
- Table: Code, Name, City, Primary Email, Actions (View)
- Pagination: page numbers + prev/next
- "New Client" button → /clients/new

### ClientDetailPage
- Display all client fields
- Contacts table with "Add Contact" button
- Each contact row: Name, Email, Phone, Designation, Primary badge, Delete button
- "Edit" button (inline or modal)
- "Back to Clients" link

### NewClientPage / ClientForm
- Form fields: Name*, Code*, Primary Email*, Primary Phone, Address, City, State, Pincode, Country (default India), GST Number, Notes
- Contacts section: dynamic list of contacts (name, email, phone, designation, is_primary checkbox)
- Submit → POST /api/clients → redirect to client detail

### ProjectsPage
- Search input (debounced)
- Status filter dropdown: All, Lead, Quote, Awarded, Design, Vendor, Execution, Validation, Closed
- Table: Code, Name, Client, Status (Badge), PM, Location, Updated At, Actions
- Pagination
- "New Project" button → /projects/new

### ProjectDetailPage
- Display all project fields
- Status badge large
- "Transition Status" section: dropdown of allowed next statuses + "Transition" button
  - Calls POST /api/projects/{id}/transition
  - On success: refetch project data
- Assigned team: PM, Designer, Auditor (show names)
- Client card: link to client detail
- "Edit" button (modal)
- "Back to Projects" link

### NewProjectPage / ProjectForm
- Form fields: Name*, Code*, Client (select dropdown from /api/clients)*, Description, Location, Estimated Value, Start Date, Target End Date, PM (select from users), Designer (select), Auditor (select)
- Status defaults to "Lead" (read-only display)
- Submit → POST /api/projects → redirect to project detail

### User select dropdown
For PM/Designer/Auditor selects in ProjectForm, fetch users from `/api/users` and filter by role:
- PM select: show users with role "pm" or "admin"
- Designer select: show users with role "designer" or "admin"
- Auditor select: show users with role "auditor" or "admin"

### E2E test (`tests/e2e/test_clients_projects.spec.ts`)
```typescript
import { test, expect } from "@playwright/test";

test("admin can create a client", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.goto("http://localhost:3000/clients/new");
  await page.getByLabel("Name").fill("Test Client Corp");
  await page.getByLabel("Code").fill("TCC-001");
  await page.getByLabel("Primary Email").fill("test@client.com");
  await page.getByRole("button", { name: /save/i }).click();
  await expect(page.getByText("Test Client Corp")).toBeVisible();
});

test("admin can create a project and transition it", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.goto("http://localhost:3000/projects/new");
  await page.getByLabel("Name").fill("Test Project");
  await page.getByLabel("Code").fill("TP-001");
  // Select first client from dropdown
  await page.getByLabel("Client").selectOption({ index: 0 });
  await page.getByRole("button", { name: /save/i }).click();
  await expect(page.getByText("Test Project")).toBeVisible();
  await expect(page.getByText("Lead")).toBeVisible();
  // Transition
  await page.getByLabel("Next Status").selectOption("Quote");
  await page.getByRole("button", { name: /transition/i }).click();
  await expect(page.getByText("Quote")).toBeVisible();
});
```

## Acceptance criteria (executable)
- [ ] `cd src/frontend && npm run build` succeeds
- [ ] `cd src/frontend && npm run lint` clean
- [ ] `cd src/frontend && npx tsc --noEmit` clean
- [ ] Playwright `tests/e2e/test_clients_projects.spec.ts` passes
- [ ] Manual: login → /clients → create client → view client → add contact
- [ ] Manual: /projects → create project → view project → transition status
- [ ] Manual: search filters work on both list pages

## How to deliver
1. Implement all files
2. Run acceptance commands
3. Write report to `work/reports/wave-2/05-clients-projects-ui.report.md`
4. Stop

## Constraints
- Time budget: 2 hours
- Use react-hook-form + zod for all forms
- Use TanStack Query for all data fetching
- Use shadcn Dialog for modals, Select for dropdowns
- Backend must be running on :8000 for E2E
- Keep forms simple — no rich text, no file upload, no maps
