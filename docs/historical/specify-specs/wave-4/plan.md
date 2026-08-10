# Wave-4 Plan — Task Management

## Dependencies
- Wave-1: Foundation (Auth, RBAC, Users) ✅
- Wave-2: Clients + Projects ✅
- Wave-3: Quotation/BOQ ✅

## Timeline
| Phase | Duration |
|-------|----------|
| Spec review | 0.5h |
| Task dispatch | 0.5h |
| Implementation | 2h |
| Test + lint | 0.5h |
| Ship | 0.5h |

---

## Technical Approach

### Backend (5 tasks)
1. **Models & CRUD API** — SQLAlchemy models, repos, FastAPI router, RBAC
2. **Dependencies** — DAG validation, cycle detection, API
3. **Comments & Notifications** — Threaded comments, Celery email tasks
4. **Frontend Kanban** — React DnD, columns, cards, optimistic updates
5. **Frontend Detail** — Modal, comments, deps, time-log link

### Database
- 3 new tables: `tasks`, `task_dependencies`, `task_comments`
- Migration via Alembic (auto-generated)
- Indexes on FKs, status, assignee

### Frontend
- `@dnd-kit` for drag-drop (already in package.json)
- TanStack Query for caching/invalidation
- shadcn/ui Dialog, Dropdown, Badge, Avatar
- Zod validation for forms

---

## Acceptance Checklist (per ship.md)

- [ ] All 5 tasks marked merged in EXECUTION.md
- [ ] `pytest .specify/specs/wave-4/contracts/` passes
- [ ] E2E tests pass (Playwright)
- [ ] Perf budget: Kanban load < 500ms for 200 tasks
- [ ] Version bump in pyproject.toml + package.json
- [ ] CHANGELOG.md updated
- [ ] HANDOFF.md updated (active wave → 5)
- [ ] Git tag `wave-4-complete`
- [ ] PR opened (or direct commit to main)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Cycle detection bugs | Property-based testing (hypothesis) |
| Drag-drop race conditions | Optimistic lock + server reconciliation |
| Notification spam | Debounce + user preferences (later) |
| Large project task count | Pagination + virtualized list |

---

## Files to Create

```
.specify/specs/wave-4/
├── spec.md          ← done
├── plan.md          ← this file
├── tasks.md         ← task definitions
└── contracts/
    ├── test_tasks_api.py
    ├── test_task_dependencies.py
    ├── test_task_comments.py
    ├── test_kanban.py
    └── test_task_notifications.py

work/wave-4/
├── 01-task-models-api.md
├── 02-task-dependencies-api.md
├── 03-task-comments-notifications.md
├── 04-frontend-kanban-board.md
└── 05-frontend-task-detail.md
```