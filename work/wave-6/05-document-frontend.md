# Task 05 — Document Management Frontend UI

## Goal
Build the document management UI: a file browser with folders, drag-and-drop upload, document preview, tag management, search and filter. This is the primary interface for users to manage project documents.

## Files to Create / Modify

### 1. Types
Create `src/frontend/src/types/document.ts`:
```typescript
export interface DocumentItem {
  id: string;
  project_id: string;
  folder_id: string | null;
  name: string;
  file_path: string;
  file_size: number;
  content_type: string;
  uploaded_by: string;
  uploaded_by_name: string | null;
  tags: string[];
  version: number;
  is_active: boolean;
  created_at: string;
}

export interface DocumentFolder {
  id: string;
  project_id: string;
  name: string;
  parent_id: string | null;
  created_at: string;
}

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  page_size: number;
}
```

### 2. API hooks
Create `src/frontend/src/hooks/useDocuments.ts`:
```typescript
export function useDocuments(projectId: string, folderId?: string, page?: number) — GET /api/projects/{projectId}/documents
export function useDocument(documentId: string) — GET /api/documents/{documentId}
export function useDownloadDocument() — returns download URL builder
export function useUploadDocument(projectId: string) — mutation: POST /api/projects/{projectId}/documents (multipart)
export function useDeleteDocument() — mutation: DELETE /api/documents/{documentId}
export function useFolders(projectId: string, parentId?: string) — GET /api/projects/{projectId}/folders
export function useCreateFolder(projectId: string) — mutation: POST /api/projects/{project_id}/folders
export function useDeleteFolder() — mutation: DELETE /api/folders/{folderId}
export function useSearchDocuments(projectId: string, query: string, tags?: string) — GET /api/projects/{projectId}/documents/search
export function useRenameDocument() — mutation: PUT /api/documents/{documentId}/rename
export function useMoveDocuments() — mutation: PUT /api/documents/move
```

### 3. Components
Create in `src/frontend/src/components/documents/`:

**DocumentBrowser.tsx** — Main file browser component
- Left sidebar: folder tree (recursive, expandable)
- Main area: file list (table or grid toggle)
- Breadcrumb navigation showing current folder path
- Top toolbar: search bar, upload button, new folder button, view toggle (list/grid)

**FolderTree.tsx** — Recursive folder tree
- Indented tree with expand/collapse chevrons
- Click to navigate into folder
- Right-click context menu: Rename, Delete
- "New Subfolder" button at each level
- Highlight current folder

**FileList.tsx** — File listing in table format
- Columns: Name, Type (icon), Size, Uploaded By, Date, Tags, Version, Actions
- Sortable columns (name, date, size)
- Select checkboxes for bulk operations
- Right-click context menu: Rename, Move, Delete, Download
- Click row to open preview

**FileGrid.tsx** — File listing in grid/card format
- Thumbnail for images, icon for others
- File name and size below
- Click to open preview

**UploadDialog.tsx** — File upload with drag-and-drop
- Drag-and-drop zone (full dialog or inline area)
- File picker button as fallback
- Shows selected files list with names and sizes
- Folder selector dropdown (which folder to upload into)
- Tags input (comma-separated, with autocomplete from existing tags)
- Upload progress bar per file
- "Upload" button, "Cancel" button
- After upload: success toast, refresh file list

**DocumentPreview.tsx** — Preview panel (modal or side panel)
- Images: inline preview with zoom
- PDFs: embedded viewer or link to open in new tab
- Other files: show metadata only (name, size, type, version, uploaded by, date)
- Action buttons: Download, Delete, Rename, Version History
- Tags display with add/remove
- Linked compliance items (if any)

**TagManager.tsx** — Tag management
- Display current tags as badges
- Add tag input with autocomplete from project's existing tags
- Remove tag (X button on badge)
- Used in upload dialog and document preview

**DocumentSearchBar.tsx** — Search and filter
- Text search input (searches by name)
- Tag filter (multi-select dropdown from project's tags)
- Folder filter (scope to current folder or all)
- Clear button

**BulkActions.tsx** — Bulk operations toolbar
- Appears when documents are selected
- Actions: Move (opens folder picker), Delete, Download (as zip?)
- Selected count display

**MoveDialog.tsx** — Move documents dialog
- Folder tree picker
- "Move Here" button
- Shows target folder path

### 4. Page
Create `src/frontend/src/pages/DocumentsPage.tsx`:
- Route: `/projects/:projectId/documents`
- Renders `DocumentBrowser` inside project layout
- Breadcrumb: Projects > [Project Name] > Documents

### 5. Navigation
Modify `src/frontend/src/components/Layout.tsx` or project detail navigation to add:
- "Documents" link in project detail sidebar

### 6. Router
Modify `src/frontend/src/App.tsx` to add:
- Route for `/projects/:projectId/documents` → `DocumentsPage`

## Files you must NOT touch
- `src/backend/` — no backend changes
- `src/frontend/src/pages/CompliancePage.tsx` — task 04
- `tests/wave-6/` — backend tests

## Skills to use
- `code-review` — self-review before declaring done

## The core problem (inline — no external context needed)
Documents are files uploaded to projects, organized in folders, and tagged for search. The UI provides a familiar file-browser experience: navigate folders, upload via drag-and-drop, preview files, search by name/tag, and manage documents with rename/move/delete.

### Edge cases to handle
- Empty project (no documents) → show empty state with upload prompt
- Empty folder → show "This folder is empty" with upload button
- Upload multiple files simultaneously → show progress for each
- Large file upload (near 50MB) → progress bar, handle timeout
- Delete folder with documents → confirm dialog showing document count
- Search returns no results → show "No documents found"
- Document preview not supported for file type → show metadata only
- Offline/error state → show error toast, retry button

## Acceptance criteria (executable, not prose)
- [ ] DocumentsPage renders at `/projects/:projectId/documents`
- [ ] File browser shows folders and documents
- [ ] Clicking folder navigates into it
- [ ] Upload dialog opens with drag-and-drop zone
- [ ] Files upload successfully and appear in list
- [ ] Document preview opens for images and PDFs
- [ ] Tags can be added/removed from documents
- [ ] Search by name returns matching documents
- [ ] Filter by tags works
- [ ] Delete with confirmation dialog works
- [ ] `npx tsc --noEmit` passes (TypeScript strict)
- [ ] `npx eslint src/` clean

## How to deliver
1. Create types, hooks, components, page
2. Update router and navigation
3. Run `npx tsc --noEmit`
4. Run `npx eslint src/`
5. Write report to `work/reports/wave-6/05-document-frontend.report.md`
6. Use `work/REPORT_TEMPLATE.md`
7. Stop

## Constraints
- Time budget: 30 min
- No new dependencies without flagging
- Match existing patterns (see `src/frontend/src/pages/ProjectDetailPage.tsx`, `src/frontend/src/hooks/`)
- Use shadcn/ui components (Button, Card, Table, Dialog, Badge, Input, DropdownMenu, Toast)
- Use TanStack Query for data fetching
- Use `react-dropzone` for drag-and-drop (install if not present, flag dependency)
- Allowed tools: Read, Edit, Write, Bash, Glob, Grep
