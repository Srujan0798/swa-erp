# Task 04 — Frontend Shell + Auth Flow

## What to do
Scaffold the React + Vite + TypeScript frontend with TailwindCSS, shadcn/ui, React Router, TanStack Query, and an auth flow integrating with the backend `/api/auth/*` and `/api/users/*` endpoints.

Reference spec: `.specify/specs/wave-1/spec.md` — US-1.1, US-1.3.

## Files to create
- CREATE: `src/frontend/package.json` (deps per plan.md)
- CREATE: `src/frontend/vite.config.ts`
- CREATE: `src/frontend/tsconfig.json` (strict mode)
- CREATE: `src/frontend/tsconfig.node.json`
- CREATE: `src/frontend/tailwind.config.ts`
- CREATE: `src/frontend/postcss.config.js`
- CREATE: `src/frontend/index.html`
- CREATE: `src/frontend/src/main.tsx`
- CREATE: `src/frontend/src/App.tsx`
- CREATE: `src/frontend/src/index.css` (Tailwind directives)
- CREATE: `src/frontend/src/lib/api.ts` (fetch wrapper + auto-refresh)
- CREATE: `src/frontend/src/lib/auth.ts` (token storage)
- CREATE: `src/frontend/src/lib/utils.ts` (cn helper)
- CREATE: `src/frontend/src/types/api.ts` (API types)
- CREATE: `src/frontend/src/types/domain.ts` (User, Role)
- CREATE: `src/frontend/src/hooks/useAuth.ts`
- CREATE: `src/frontend/src/hooks/useCurrentUser.ts`
- CREATE: `src/frontend/src/hooks/useUsers.ts`
- CREATE: `src/frontend/src/components/ui/button.tsx` (shadcn primitive)
- CREATE: `src/frontend/src/components/ui/input.tsx` (shadcn primitive)
- CREATE: `src/frontend/src/components/ui/card.tsx` (shadcn primitive)
- CREATE: `src/frontend/src/components/auth/ProtectedRoute.tsx`
- CREATE: `src/frontend/src/components/layout/AppShell.tsx`
- CREATE: `src/frontend/src/components/layout/Sidebar.tsx`
- CREATE: `src/frontend/src/components/layout/Topbar.tsx`
- CREATE: `src/frontend/src/pages/LoginPage.tsx`
- CREATE: `src/frontend/src/pages/DashboardPage.tsx`
- CREATE: `src/frontend/src/pages/UsersPage.tsx`
- CREATE: `tests/e2e/test_login_flow.spec.ts` (Playwright)
- CREATE: `playwright.config.ts`

## Files you must NOT touch
- `src/backend/` (Tasks 01-03)
- `Dockerfile`, `docker-compose.yml`, `.github/workflows/` (Task 05)
- Other workers' in-flight files

## Skills to use
- `tdd` (Playwright test FIRST, then implement to pass)
- `react-hooks`
- `tanstack-query` (v5 — `useQuery` + `useMutation`)
- `tailwind-shadcn` (init + add components)
- `vite-config` (proxy `/api` → http://localhost:8000)
- `code-review`

## The core problem (inline)

### Tech versions (FIXED)
- React 18.3.x
- Vite 5.4.x
- TypeScript 5.5.x (strict mode)
- TailwindCSS 3.4.x
- @tanstack/react-query 5.51.x
- react-router-dom 6.26.x
- react-hook-form 7.52.x + zod 3.23.x
- lucide-react (icons)
- shadcn/ui components: button, input, card, label, form, toast (init via `npx shadcn-ui@latest init`)

### Vite config (`vite.config.ts`)
```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": "http://localhost:8000",
      "/healthz": "http://localhost:8000",
    },
  },
});
```

### API client (`lib/api.ts`)
- Wrapper around `fetch` that:
  - Reads access token from `localStorage`
  - Adds `Authorization: Bearer <token>` header
  - On 401: calls `/api/auth/refresh` with refresh token; retries original request once
  - On second 401: clears tokens, redirects to `/login`
  - Throws `ApiError` with status + body on non-2xx

### Auth flow
1. `/login` page: email + password form (react-hook-form + zod schema)
2. Submit → POST `/api/auth/login` → store tokens in localStorage → redirect to `/dashboard`
3. `/dashboard` (protected): shows current user's name, email, role; "Welcome to SWA ERP" placeholder card
4. `/users` (admin only, protected): list users with pagination; "New User" button → modal form
5. Top bar: shows user name + logout button

### Routes (`App.tsx`)
```typescript
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route element={<ProtectedRoute />}>
    <Route element={<AppShell />}>
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/users" element={<ProtectedRoute requiredRole="admin"><UsersPage /></ProtectedRoute>} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Route>
  </Route>
  <Route path="*" element={<Navigate to="/dashboard" replace />} />
</Routes>
```

### useAuth hook
```typescript
export function useAuth() {
  // Returns: { isAuthenticated, user, login, logout, refresh }
  // Uses TanStack Query for /api/auth/me
  // Provides login mutation that stores tokens + invalidates user query
  // Provides logout mutation that calls /api/auth/logout + clears tokens
}
```

### Tailwind + shadcn setup
- Init shadcn with default theme (slate)
- Add only 4 components for wave-1: button, input, card, label
- Custom theme: minimal — keep defaults; we'll customize in wave-2

### E2E test (`tests/e2e/test_login_flow.spec.ts`)
```typescript
import { test, expect } from "@playwright/test";

test("admin can log in and reach dashboard", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("admin@swa.local");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText(/welcome to swa erp/i)).toBeVisible();
});

test("invalid credentials show error", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("admin@swa.local");
  await page.getByLabel("Password").fill("wrong");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByText(/invalid/i)).toBeVisible();
});

test("non-admin gets blocked from /users", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("pm@swa.local");
  await page.getByLabel("Password").fill("pm123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.goto("http://localhost:3000/users");
  // Either redirected away or shown forbidden
  const url = page.url();
  expect(url.includes("/users")).toBe(false);
});

test("logout returns to login", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("admin@swa.local");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await page.getByRole("button", { name: /logout/i }).click();
  await expect(page).toHaveURL(/\/login/);
});
```

### Playwright config (`playwright.config.ts`)
- Base URL `http://localhost:3000`
- Webserver: start `pnpm dev` (or `npm run dev`) on port 3000 before tests
- Timeout 30s per test
- Reuse single context per test file

## Acceptance criteria (executable)
- [ ] `cd src/frontend && pnpm install && pnpm build` succeeds
- [ ] `cd src/frontend && pnpm dev` starts dev server on port 3000
- [ ] `cd src/frontend && pnpm tsc --noEmit` clean (TS strict mode)
- [ ] `cd src/frontend && pnpm lint` clean (eslint)
- [ ] `npx playwright test tests/e2e/test_login_flow.spec.ts` → all 4 tests pass
- [ ] Manual: login as admin → dashboard → click /users → list visible
- [ ] Manual: login as pm → /users blocked

## How to deliver
1. Implement files (TDD: write Playwright tests first if you prefer)
2. Run acceptance commands
3. Write report to `work/reports/wave-1/04-frontend-shell.report.md`
4. Stop

## Constraints
- Time budget: 2 hours
- Backend must be running on port 8000 for E2E (the Task 05 docker-compose handles this; for now, assume manual)
- No design system customization beyond shadcn defaults (we keep MVP minimal)
- No state library beyond TanStack Query + React state (no Zustand, no Redux)
- Forms: react-hook-form + zod resolver everywhere
