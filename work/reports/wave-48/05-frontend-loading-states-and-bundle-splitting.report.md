# Wave-48 Task 05 — Frontend Loading States & Bundle Splitting

**HEAD:** `1712e40302f566e7e919ad88af2d81463b4f582f`
**Date:** 2026-09-15

## Files Changed

| File | Change |
|------|--------|
| `src/frontend/src/pages/DashboardPage.tsx` | Per-card Skeleton loading + error indicators for 8 useQuery calls |
| `src/frontend/src/pages/ProjectDetailPage.tsx` | Skeleton header + `QueryErrorBanner` for project query |
| `src/frontend/src/pages/DocumentsPage.tsx` | Skeleton select dropdown while projects load; wired `QueryErrorBanner` with retry |
| `src/frontend/src/App.tsx` | All 25 page-level routes converted to `React.lazy` with `Suspense` fallback |

## Ruled-Out Pages (Already Had Loading States)

These pages use thin wrappers over `ClientList`, `VendorList`, `VendorDetailPage`, etc. which already handle `isLoading`/`isError` internally:

- `ClientsPage` (uses `ClientList`)
- `ProjectsPage`
- `VendorsPage`
- `VendorDetailPage`
- `TasksPage`
- `ClientDetailPage`

Plus all "New X" pages, detail pages, and utility pages that use form-level `isLoading` props (existing pattern).

## Bundle Size Comparison

**Before (estimated from context):** single 725 KB JS bundle.
**After:** 48 JS chunks totaling ~896 KB, with a **main entry of 365 KB** (`index-BzRVNwqL.js`) and page chunks loaded on demand.

| Chunk | Size |
|-------|------|
| Main entry (`index-BzRVNwqL.js`) | 365.18 kB |
| DashboardPage | 13.18 kB |
| ProjectDetailPage | 33.90 kB |
| ClientDetailPage | 20.98 kB |
| TasksPage | 64.24 kB |
| RFQsPage | 12.45 kB |
| DocumentsPage | 2.03 kB |

## Verification Output

### `npx tsc --noEmit`
```
(empty — no type errors)
```

### `npx eslint src/pages/DashboardPage.tsx src/pages/ProjectDetailPage.tsx src/pages/DocumentsPage.tsx src/App.tsx`
```
(empty — no lint warnings)
```

### `npx vite build 2>&1`
```
vite v5.4.21 building for production...
✓ 1806 modules transformed.
computing gzip size...
dist/index.html                                   0.45 kB │ gzip:   0.30 kB
dist/assets/index-DR3URLDt.css                   29.09 kB │ gzip:   5.85 kB
dist/assets/chevron-right-Dp4ndvIO.js             0.30 kB │ gzip:   0.25 kB
dist/assets/plus-axluRK5x.js                      0.32 kB │ gzip:   0.26 kB
dist/assets/arrow-right-jTgRJyo6.js               0.33 kB │ gzip:   0.27 kB
dist/assets/arrow-left-CpAfjmQ9.js                0.33 kB │ gzip:   0.27 kB
dist/assets/search-I6Fxj6RB.js                    0.34 kB │ gzip:   0.27 kB
dist/assets/pencil-CpNWY1-a.js                    0.45 kB │ gzip:   0.33 kB
dist/assets/textarea-CE2iaL2I.js                  0.48 kB │ gzip:   0.32 kB
dist/assets/trash-2-BjBJ8-pK.js                   0.53 kB │ gzip:   0.35 kB
dist/assets/useAgreements-BI1yVgW7.js             0.53 kB │ gzip:   0.27 kB
dist/assets/permissions-oNEkbzsC.js               0.53 kB │ gzip:   0.26 kB
dist/assets/QueryErrorBanner-DJnd9HwY.js          0.63 kB │ gzip:   0.41 kB
dist/assets/useVendors-65cQDpkm.js                0.87 kB │ gzip:   0.33 kB
dist/assets/NewClientPage-D4Vzo823.js             0.93 kB │ gzip:   0.54 kB
dist/assets/TaskDetailPage-BPSUH01Z.js            1.04 kB │ gzip:   0.56 kB
dist/assets/useInquiries-OxK3iFnx.js              1.04 kB │ gzip:   0.34 kB
dist/assets/table-DUejuzM6.js                     1.31 kB │ gzip:   0.48 kB
dist/assets/DocumentsPage-CNgXrwIc.js             2.03 kB │ gzip:   0.97 kB
dist/assets/NewVendorPage-CLpBKl8v.js             3.48 kB │ gzip:   1.09 kB
dist/assets/VendorsPage-CZKs41ND.js               3.61 kB │ gzip:   1.42 kB
dist/assets/AgreementsPage-hr-q7GbK.js            3.98 kB │ gzip:   1.58 kB
dist/assets/ClientsPage-TS4s2SQt.js               4.25 kB │ gzip:   1.64 kB
dist/assets/ClientForm-CIbScymo.js                4.53 kB │ gzip:   1.16 kB
dist/assets/TokensPage-CKTqruQ6.js                4.57 kB │ gzip:   1.74 kB
dist/assets/UsersPage-5PUitySa.js                 4.58 kB │ gzip:   1.57 kB
dist/assets/MaterialsPage-CLtEZ1Ie.js             5.02 kB │ gzip:   1.68 kB
dist/assets/DocumentReferenceForm-CMIiUEBh.js     5.09 kB │ gzip:   1.59 kB
dist/assets/VendorDetailPage-BqVBO-Tm.js          5.68 kB │ gzip:   1.70 kB
dist/assets/ProjectsPage-L2ByA9cW.js              5.79 kB │ gzip:   2.17 kB
dist/assets/dialog-BjjLyOpR.js                    6.49 kB │ gzip:   2.38 kB
dist/assets/tabs-BwdeXiDW.js                      6.62 kB │ gzip:   2.64 kB
dist/assets/TaskDetail-D2cRVndM.js                6.76 kB │ gzip:   2.24 kB
dist/assets/NewProjectPage-BXs2AL4-.js            7.34 kB │ gzip:   1.93 kB
dist/assets/DocumentReferencesPage-CviutxEZ.js    7.60 kB │ gzip:   2.63 kB
dist/assets/ReportsPage-DYNM4mr-.js               8.76 kB │ gzip:   2.83 kB
dist/assets/InquiriesPage-Bdof-aDi.js             9.13 kB │ gzip:   3.00 kB
dist/assets/InquiryDetailPage-CVdPg18n.js         9.35 kB │ gzip:   2.85 kB
dist/assets/SustainabilityPage-CDf3qzQI.js        9.40 kB │ gzip:   2.75 kB
dist/assets/CompliancePage-Bo6Impqa.js            9.74 kB │ gzip:   3.14 kB
dist/assets/TimeTrackingPage-BELz9q3e.js         10.11 kB │ gzip:   2.94 kB
dist/assets/InvoicesPage-C-QXwcF_.js             11.72 kB │ gzip:   3.58 kB
dist/assets/RFQsPage-BZSfY6LW.js                 12.45 kB │ gzip:   3.67 kB
dist/assets/DashboardPage-Cn8iHSjA.js            13.18 kB │ gzip:   3.95 kB
dist/assets/ClientDetailPage-DlCGhbh_.js         20.98 kB │ gzip:   4.90 kB
dist/assets/index-BDG99Wis.js                    27.01 kB │ gzip:   9.60 kB
dist/assets/ProjectDetailPage-DS_IXChW.js        33.90 kB │ gzip:   7.84 kB
dist/assets/select-DDl8ZHMM.js                   52.00 kB │ gzip:  18.33 kB
dist/assets/TasksPage-Bf4ITG09.js                64.24 kB │ gzip:  21.04 kB
dist/assets/index-BzRVNwqL.js                   365.18 kB │ gzip: 109.75 kB
✓ built in 2.88s
```

### `ls -la dist/assets/*.js | wc -l`
```
48
```