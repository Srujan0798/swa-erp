# Task 03 — Reports UI (Frontend)

## Goal
Build the reports frontend pages: a Project Health dashboard, Utilization report, Revenue report, and Client Summary table. Include date range filters and export buttons.

## Files to Create/Modify

### 1. API Client
Create `src/frontend/src/lib/api/reports.ts`:
```typescript
export interface ProjectHealthReport {
  total_projects: number;
  by_status: Record<string, number>;
  overdue_tasks: number;
  budget_variance_total: number;
  at_risk_projects: { id: string; name: string; status: string; variance: number }[];
}

export interface MemberUtilization {
  user_id: string;
  name: string;
  billable_hours: number;
  non_billable_hours: number;
  utilization_pct: number;
}

export interface UtilizationReport {
  period_start: string;
  period_end: string;
  members: MemberUtilization[];
}

export interface MonthlyRevenue { month: string; revenue: number; }
export interface ForecastEntry { project_id: string; project_name: string; pipeline_value: number; probability: number; expected_value: number; }

export interface RevenueForecast {
  monthly_revenue: MonthlyRevenue[];
  forecast: ForecastEntry[];
}

export interface ClientSummary { client_id: string; client_name: string; project_count: number; total_revenue: number; }

export interface ExecutiveKPIs {
  active_projects: number;
  total_revenue_mtd: number;
  avg_utilization: number;
  overdue_tasks: number;
  pipeline_value: number;
}

export function fetchProjectHealth(): Promise<ProjectHealthReport>
export function fetchUtilization(start?: string, end?: string): Promise<UtilizationReport>
export function fetchRevenue(): Promise<RevenueForecast>
export function fetchClientSummary(): Promise<ClientSummaryReport>
export function fetchExecutiveKPIs(): Promise<ExecutiveKPIs>
```
Use the existing `apiClient` from `src/frontend/src/lib/api.ts` (or `api.ts` — check existing pattern).

### 2. Pages
Create `src/frontend/src/pages/ReportsPage.tsx`:
- Tabbed layout with 4 tabs: **Project Health**, **Utilization**, **Revenue**, **Client Summary**
- Tab component: use shadcn `Tabs` component (check if already installed; if not, use simple button-toggle)
- Date range picker on Utilization tab (default: current month)

Create `src/frontend/src/pages/ExecutiveDashboardPage.tsx`:
- KPI cards row (5 cards): Active Projects, Revenue MTD, Avg Utilization, Overdue Tasks, Pipeline Value
- Quick links to detailed report pages

### 3. Components
Create `src/frontend/src/components/reports/`:
- `ProjectHealthChart.tsx` — pie chart of status distribution + bar chart of at-risk projects (use `recharts` — check if in package.json; if not, install `recharts`)
- `UtilizationChart.tsx` — horizontal bar chart per team member (billable green, non-billable gray)
- `RevenueChart.tsx` — line chart of monthly revenue + forecast entries as dotted line
- `ClientSummaryTable.tsx` — sortable table of clients with project count and revenue columns
- `DateRangeFilter.tsx` — two date inputs (start, end) with apply button
- `ExportButton.tsx` — dropdown with "Export JSON" option; calls report endpoint and triggers download

### 4. Routing
Modify `src/frontend/src/App.tsx` (or router config) to add:
- `/reports` → `ReportsPage`
- `/dashboard/executive` → `ExecutiveDashboardPage`

### 5. Sidebar Navigation
Modify sidebar component to add "Reports" and "Executive Dashboard" nav items (check existing sidebar in `src/frontend/src/components/layout/`).

## Files you must NOT touch
- `src/backend/` — backend is Task 01/02
- `src/frontend/src/pages/DashboardPage.tsx` — existing dashboard, don't modify

## Acceptance criteria
- [ ] Reports page loads with 4 tabs, each showing correct data
- [ ] Utilization tab has date range filter that updates the chart
- [ ] Export button downloads a JSON file
- [ ] Executive dashboard shows 5 KPI cards with real data
- [ ] Charts render without errors (no blank screens)
- [ ] Navigation sidebar includes Reports and Executive Dashboard links
- [ ] `npm run lint` clean
- [ ] `npm run typecheck` clean (or `tsc --noEmit`)

## Test File
Create `src/frontend/src/__tests__/reports.test.tsx`:
- `test_reports_page_renders` — snapshot/render test
- `test_tab_switching` — click each tab, verify content changes
- `test_export_button` — verify button exists and triggers download (mock fetch)
- `test_executive_dashboard_renders` — KPI cards appear

## Constraints
- Time budget: 45 min
- Use shadcn/ui components where available (Card, Tabs, Table, Button)
- If `recharts` is not installed, run `npm install recharts`
- Follow existing patterns from `DashboardPage.tsx` and `ClientsPage.tsx`
- Strict TypeScript — no `any` types
- Allowed tools: Read, Write, Edit, Bash, Glob, Grep

## Notes
- Check `package.json` for existing chart libraries before adding recharts
- Export JSON: create a Blob from JSON.stringify, create object URL, trigger `<a>` download
- Date format for API params: ISO 8601 date strings (`YYYY-MM-DD`)
- If shadcn Tabs not available, use a simple div with button toggles styled with Tailwind
