# TypeScript rules

- TS strict mode, no `any` (use `unknown` if truly unknown)
- Functional React components; no class components
- Hooks at top level; never conditional
- Server state via TanStack Query; React Context only for auth/theme
- Forms: react-hook-form + zod resolver
- Components ≤ 200 lines (refactor if larger)
- Explicit return types on exported functions
- shadcn/ui primitives over custom; only build custom when shadcn doesn't cover
- Tests: Vitest + React Testing Library for components; Playwright for E2E
- API client: typed (shared types from `types/api.ts`)
- No inline styles; Tailwind classes via `cn()` helper
- Date display: `date-fns` with explicit Asia/Kolkata zone
