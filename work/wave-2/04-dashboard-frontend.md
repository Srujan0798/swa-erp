# Task 04 — Dashboard Page (Frontend)

## What to do
Build the dashboard page with real stats from the backend, recent projects, recent clients, and quick-action buttons. Replace the placeholder welcome card from wave-1.

## Files to create
- CREATE: `src/frontend/src/hooks/useDashboard.ts` (TanStack Query hook for /api/projects/stats)
- CREATE: `src/frontend/src/hooks/useProjects.ts` (list projects hook)
- CREATE: `src/frontend/src/hooks/useClients.ts` (list clients hook)
- CREATE: `src/frontend/src/components/dashboard/StatsCards.tsx` (grid of stat cards)
- CREATE: `src/frontend/src/components/dashboard/RecentProjects.tsx` (table/list of recent projects)
- CREATE: `src/frontend/src/components/dashboard/RecentClients.tsx` (table/list of recent clients)
- CREATE: `src/frontend/src/components/dashboard/QuickActions.tsx` (buttons: New Project, New Client)
- CREATE: `src/frontend/src/components/ui/badge.tsx` (shadcn badge for status)
- CREATE: `src/frontend/src/components/ui/table.tsx` (shadcn table primitive)
- CREATE: `src/frontend/src/components/ui/skeleton.tsx` (shadcn skeleton for loading)
- CREATE: `tests/e2e/test_dashboard.spec.ts` (Playwright: dashboard loads with stats)

## Files to modify
- MODIFY: `src/frontend/src/pages/DashboardPage.tsx` — replace placeholder with real dashboard
- MODIFY: `src/frontend/src/components/layout/Sidebar.tsx` — add links to /clients and /projects

## Files you must NOT touch
- `src/backend/` (other tasks)
- `src/frontend/src/pages/LoginPage.tsx` (existing)

## The core problem (inline)

### API integration
Use these existing backend endpoints:
- `GET /api/projects/stats` → `{total_active, by_status: {Lead: N, ...}, total_estimated_value}`
- `GET /api/projects?page=1&page_size=5` → recent projects
- `GET /api/clients?page=1&page_size=5` → recent clients

### StatsCards component
Show 4 cards in a grid (2x2 on mobile, 4 cols on desktop):
1. **Total Active Projects** — number
2. **Total Estimated Value** — INR formatted (₹ separator)
3. **In Quote Stage** — number
4. **In Execution** — number

### RecentProjects component
Table with columns: Code, Name, Client, Status, PM, Updated At
- Status rendered as a Badge component with color mapping:
  - Lead = gray, Quote = blue, Awarded = green, Design = purple,
  - Vendor = orange, Execution = yellow, Validation = indigo, Closed = slate

### RecentClients component
Table with columns: Code, Name, Primary Email, City, Projects (count)

### QuickActions component
Two buttons:
- "New Project" → navigates to /projects/new
- "New Client" → navigates to /clients/new

### DashboardPage layout
```tsx
<div className="space-y-6">
  <div>
    <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
    <p className="text-muted-foreground">Overview of your projects and clients</p>
  </div>
  <QuickActions />
  <StatsCards />
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <RecentProjects />
    <RecentClients />
  </div>
</div>
```

### Status badge colors
```ts
const statusColors: Record<string, string> = {
  Lead: "bg-gray-100 text-gray-800",
  Quote: "bg-blue-100 text-blue-800",
  Awarded: "bg-green-100 text-green-800",
  Design: "bg-purple-100 text-purple-800",
  Vendor: "bg-orange-100 text-orange-800",
  Execution: "bg-yellow-100 text-yellow-800",
  Validation: "bg-indigo-100 text-indigo-800",
  Closed: "bg-slate-100 text-slate-800",
};
```

### E2E test (`tests/e2e/test_dashboard.spec.ts`)
```typescript
import { test, expect } from "@playwright/test";

test("dashboard shows stats for admin", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText(/total active projects/i)).toBeVisible();
  await expect(page.getByText(/total estimated value/i)).toBeVisible();
  await expect(page.getByRole("heading", { name: /recent projects/i })).toBeVisible();
  await expect(page.getByRole("heading", { name: /recent clients/i })).toBeVisible();
});
```

## Acceptance criteria (executable)
- [ ] `cd src/frontend && npm run build` succeeds
- [ ] `cd src/frontend && npm run lint` clean
- [ ] `cd src/frontend && npx tsc --noEmit` clean
- [ ] Playwright `tests/e2e/test_dashboard.spec.ts` passes
- [ ] Manual: login → dashboard shows stats cards + recent lists + quick actions

## How to deliver
1. Implement all files
2. Run acceptance commands
3. Write report to `work/reports/wave-2/04-dashboard-frontend.report.md`
4. Stop

## Constraints
- Time budget: 90 min
- Use only existing shadcn components + badge/table/skeleton
- Use TanStack Query for all data fetching
- Format INR with `new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" })`
- Responsive: 1 column on mobile, 2 on tablet, 4 on desktop for stats cards
- Backend must be running on :8000 for E2E
