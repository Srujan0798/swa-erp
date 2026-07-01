# Task 05 — Kanban Board UI

## Goal
Build the Kanban board interface for task management: three columns (Todo, In Progress, Done), task cards with priority badges and assignee info, drag-and-drop between columns, task detail modal, create task form, and a My Tasks page.

## Files to Create/Modify

### 1. Dependencies
Install `@dnd-kit/core` and `@dnd-kit/sortable`:
```bash
cd src/frontend && npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

### 2. Board Components
Create `src/frontend/src/components/tasks/TaskBoard.tsx`:
- Main Kanban board component
- Three columns: Todo, In Progress, Done
- Uses `DndContext` from @dnd-kit/core
- Handles `onDragEnd` to transition task status + reorder
- Uses `useTasks` hook to fetch tasks, groups by status
- Loading skeleton state
- Empty state message per column

Create `src/frontend/src/components/tasks/TaskColumn.tsx`:
- Single column component (Todo | In Progress | Done)
- Uses `useDroppable` from @dnd-kit
- Renders column header with task count
- Renders `SortableContext` with task cards
- Column color coding: Todo=gray, InProgress=blue, Done=green

Create `src/frontend/src/components/tasks/TaskCard.tsx`:
- Individual task card within a column
- Uses `useSortable` from @dnd-kit
- Displays: title, priority badge (color-coded), assignee avatar/initials, due date (with overdue warning)
- Click handler opens task detail modal
- Priority badge colors: low=gray, medium=blue, high=orange, critical=red
- Due date: show in red if overdue, orange if due today

### 3. Task Detail Modal
Create `src/frontend/src/components/tasks/TaskDetailModal.tsx`:
- Dialog/modal showing full task details
- Fields: title, description (editable), status dropdown, priority dropdown, assignee dropdown, due date
- Comment section: list existing comments, add new comment form
- Action buttons: Transition (based on current status), Delete, Assign/Unassign
- Uses `useTask` hook for data, mutations for actions
- shadcn/ui Dialog component

### 4. Create Task Form
Create `src/frontend/src/components/tasks/CreateTaskForm.tsx`:
- Form with fields: title (required), description, priority, assignee, due date
- Uses shadcn/ui form components (Input, Textarea, Select, Button)
- Submit calls `useCreateTask` mutation
- Success: close form, refetch task list
- Validation: title required, max 255 chars

### 5. Board Page
Create `src/frontend/src/pages/TasksBoardPage.tsx`:
- Full page layout with project selector dropdown (if on project context)
- Renders `TaskBoard`
- Header with "Create Task" button (opens CreateTaskForm in modal)
- Filter bar: filter by assignee, priority
- Uses `useProjectTaskStats` for summary stats

### 6. My Tasks Page
Create `src/frontend/src/pages/MyTasksPage.tsx`:
- Page showing all tasks assigned to current user across projects
- Same Kanban board layout (Todo, In Progress, Done columns)
- Group tasks by status
- Show project name on each card
- Filter by priority
- Uses `useMyTasks` hook
- Summary stats at top: total tasks, overdue count, due today count

### 7. Navigation
Update `src/frontend/src/components/layout/Sidebar.tsx` (or equivalent):
- Add "Tasks" nav item (links to /tasks/board)
- Add "My Tasks" nav item (links to /tasks/my)

### 8. Routing
Update `src/frontend/src/App.tsx` (or router config):
- Add route `/tasks/board` → TasksBoardPage
- Add route `/tasks/my` → MyTasksPage
- Both routes require authentication

### 9. Styles
- Use TailwindCSS classes consistently
- Follow existing shadcn/ui patterns in the project
- Responsive: board should scroll horizontally on mobile
- Use the project's color theme

## Files you must NOT touch
- `src/backend/` — backend is complete
- `src/frontend/src/types/api.ts` — types defined in task 04
- `src/frontend/src/lib/api.ts` — API methods defined in task 04
- `src/frontend/src/hooks/useTasks.ts` — hooks defined in task 04

## Acceptance criteria
- [ ] Kanban board displays three columns with correct headers
- [ ] Task cards show title, priority badge, assignee, due date
- [ ] Drag-and-drop moves task between columns and updates status
- [ ] Drag-and-drop reorders tasks within same column
- [ ] Task detail modal opens on card click
- [ ] Task detail modal shows all fields and comments
- [ ] Create task form works with validation
- [ ] Create task appears in correct column after submission
- [ ] Priority badges are color-coded correctly
- [ ] Due date shows red for overdue, orange for today
- [ ] My Tasks page shows only current user's tasks
- [ ] My Tasks groups by status with project name on cards
- [ ] Filter by assignee works on board view
- [ ] Filter by priority works on board view
- [ ] Empty state shown when no tasks in column
- [ ] Loading skeleton shown while fetching
- [ ] Navigation includes Tasks and My Tasks links
- [ ] Routes are protected (redirect to login if unauthenticated)
- [ ] `npm run lint` clean
- [ ] `npx tsc --noEmit` passes
- [ ] `npm run build` succeeds

## Test file
Create `src/frontend/src/components/tasks/__tests__/TaskBoard.test.tsx` with at least:
- `test renders three columns` — verify Todo, In Progress, Done headings
- `test renders task cards` — mock tasks, verify cards rendered
- `test empty state` — verify empty column message
- `test loading state` — verify skeleton rendered

Create `src/frontend/src/pages/__tests__/TasksBoardPage.test.tsx` with at least:
- `test renders board page` — verify heading and create button
- `test filter by priority` — select priority filter, verify filtered results
- `test create task button opens form` — click button, verify form visible

Create `src/frontend/src/pages/__tests__/MyTasksPage.test.tsx` with at least:
- `test renders my tasks page` — verify heading
- `test shows tasks assigned to user` — mock API, verify cards

## Notes
- Use shadcn/ui components: Dialog, Button, Input, Textarea, Select, Badge, Avatar, Skeleton
- @dnd-kit provides accessible drag-and-drop — use `aria` attributes
- Task cards should have subtle shadow and hover effect
- Consider using `react-hook-form` for create task form if already in project
- Board should be performant with up to 100 tasks per column
- My Tasks is a personal dashboard — make it visually distinct from board view
- Follow existing page patterns in `src/frontend/src/pages/`
