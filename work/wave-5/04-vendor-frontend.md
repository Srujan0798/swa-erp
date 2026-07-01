# Task 04 — Vendor & Materials UI Pages

## Goal
Build frontend pages for the vendor directory and materials catalog. Vendor list with search/pagination, vendor detail with contacts, create/edit forms, material catalog page, and a vendor comparison view for RFQs.

## Files to Create/Modify

### 1. Types
Create `src/frontend/src/types/vendor.ts`:
```typescript
export interface Vendor {
  id: string;
  name: string;
  code: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  gst_number?: string;
  pan_number?: string;
  is_active: boolean;
  created_at: string;
  contacts: VendorContact[];
}

export interface VendorContact {
  id: string;
  name: string;
  designation?: string;
  email?: string;
  phone?: string;
  is_primary: boolean;
}

export interface Material {
  id: string;
  name: string;
  code: string;
  description?: string;
  category_id?: string;
  category_name?: string;
  unit: string;
  is_active: boolean;
  created_at: string;
}

export interface MaterialCategory {
  id: string;
  name: string;
  parent_id?: string;
  children?: MaterialCategory[];
}
```

### 2. API Hooks
Create `src/frontend/src/hooks/use-vendors.ts`:
- `useVendors(params)` — query GET /api/vendors with search, pagination
- `useVendor(id)` — query GET /api/vendors/{id}
- `useCreateVendor()` — mutation POST /api/vendors
- `useUpdateVendor()` — mutation PUT /api/vendors/{id}
- `useDeleteVendor()` — mutation DELETE /api/vendors/{id}

Create `src/frontend/src/hooks/use-materials.ts`:
- `useMaterials(params)` — query GET /api/materials with search, category, pagination
- `useMaterial(id)` — query GET /api/materials/{id}
- `useMaterialCategories()` — query GET /api/material-categories (tree)
- `useCreateMaterial()` — mutation POST /api/materials
- `useUpdateMaterial()` — mutation PUT /api/materials/{id}
- `useDeleteMaterial()` — mutation DELETE /api/materials/{id}
- `useCreateCategory()` — mutation POST /api/material-categories

### 3. Vendor Pages
Create `src/frontend/src/pages/vendors/vendor-list.tsx`:
- Table with columns: Code, Name, City, State, Phone, Status, Actions
- Search bar (name/code/city)
- Pagination controls
- "Add Vendor" button → opens create dialog/page
- Click row → navigate to detail

Create `src/frontend/src/pages/vendors/vendor-detail.tsx`:
- Vendor info card (name, code, GST, PAN, address, contact details)
- Contacts table (Name, Designation, Email, Phone, Primary badge)
- "Add Contact" button
- Edit/Delete buttons
- Status indicator (Active/Inactive)

Create `src/frontend/src/pages/vendors/vendor-form.tsx`:
- Reusable create/edit form
- Fields: name, code*, email, phone, address, city, state, GST number, PAN number
- Validation: name required, code required (unique)
- Submit handler with loading state

Create `src/frontend/src/pages/vendors/contact-form.tsx`:
- Add/edit contact dialog
- Fields: name*, designation, email, phone, is_primary checkbox
- If setting is_primary, unset others

### 4. Materials Pages
Create `src/frontend/src/pages/materials/material-list.tsx`:
- Table: Code, Name, Category, Unit, Status, Actions
- Search bar
- Category filter dropdown (from tree)
- Pagination

Create `src/frontend/src/pages/materials/material-form.tsx`:
- Fields: name, code*, description, category (tree select), unit
- Unit dropdown: nos, kg, sqm, cum, rmt, ls, etc.

Create `src/frontend/src/pages/materials/category-tree.tsx`:
- Tree view of categories
- Add/edit/delete category
- Nested expand/collapse

### 5. Vendor Comparison View
Create `src/frontend/src/pages/vendors/vendor-comparison.tsx`:
- Used when comparing RFQ responses
- Table: Material Name | Unit | Qty | Vendor A Rate | Vendor B Rate | ... | Best Price
- Highlight lowest rate per material
- Summary row with totals
- "Award" button per vendor column

### 6. Navigation
Modify `src/frontend/src/components/layout/sidebar.tsx`:
- Add "Vendors" nav item under Procurement section
- Add "Materials" nav item under Procurement section

### 7. Router
Modify `src/frontend/src/App.tsx` or router config:
- `/vendors` → VendorList
- `/vendors/new` → VendorForm (create)
- `/vendors/:id` → VendorDetail
- `/vendors/:id/edit` → VendorForm (edit)
- `/materials` → MaterialList
- `/materials/new` → MaterialForm (create)
- `/materials/:id/edit` → MaterialForm (edit)
- `/vendors/compare` → VendorComparison

## Files you must NOT touch
- `src/frontend/src/pages/projects/` (wave-2)
- `src/frontend/src/pages/clients/` (wave-2)
- `src/frontend/src/hooks/use-projects.ts`, `use-clients.ts` (wave-2)

## Acceptance Criteria
- [ ] Vendor list loads with search and pagination
- [ ] Can create, edit, and soft-delete vendors
- [ ] Vendor detail shows contacts with primary badge
- [ ] Can add/edit/delete contacts on vendor detail
- [ ] Material list loads with search and category filter
- [ ] Category tree renders nested structure
- [ ] Can create/edit materials with category assignment
- [ ] Vendor comparison view shows rates side-by-side
- [ ] Navigation sidebar updated with new sections
- [ ] All forms have validation and loading states
- [ ] `npm run lint` clean
- [ ] `npm run typecheck` passes

## Test File
Create `tests/wave-5/test_vendor_frontend.test.tsx` with at least:
- `test_vendor_list_renders` — renders table with columns
- `test_vendor_search_filters` — search input filters results
- `test_vendor_form_validation` — submit empty shows errors
- `test_material_list_renders` — renders material table
- `test_category_tree_renders` — nested categories display
- `test_vendor_comparison_shows_rates` — comparison table renders

## Notes
- Use shadcn/ui components: Table, Button, Input, Dialog, Select, Card, Badge
- Use TanStack Query for all data fetching
- Form state: React Hook Form + Zod validation
- Navigation: use react-router-dom
- Responsive: table should scroll horizontally on mobile
- Category tree can be recursive component or use a tree lib (keep simple)
