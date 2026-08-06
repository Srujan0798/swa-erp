# Wave-4 Task 4: Frontend Kanban Board

**Skill:** `tdd`, `code-review`, `react-dnd`, `tailwind`, `tanstack-query`
**Estimated:** 45 min

---

## Goal
Drag-drop Kanban board per project with columns: `todo`, `in_progress`, `review`, `done`.

---

## Files to Create/Modify

### 1. Types (`src/frontend/src/types/task.ts`)
```typescript
export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done';

export interface Task {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: number;
  assignee_id?: string;
  assignee_name?: string;
  due_date?: string;
  started_at?: string;
  completed_at?: string;
  estimated_hours?: number;
  actual_hours: number;
  position: number;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: number;
  assignee_id?: string;
  due_date?: string;
  estimated_hours?: number;
  dependencies?: string[];
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: number;
  assignee_id?: string;
  due_date?: string;
  estimated_hours?: number;
  version: number;
}

export interface TaskDependency {
  task_id: string;
  depends_on_task_id: string;
  depends_on_task_title?: string;
  created_at: string;
}

export interface TaskComment {
  id: string;
  task_id: string;
  author_id: string;
  author_name?: string;
  parent_comment_id?: string;
  content: string;
  created_at: string;
  updated_at?: string;
  replies_count: number;
}

export interface KanbanBoard {
  todo: Task[];
  in_progress: Task[];
  review: Task[];
  done: Task[];
}

export interface TaskReorder {
  status: TaskStatus;
  position: number;
}
```

### 2. API Hooks (`src/frontend/src/hooks/useTasks.ts`)
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Task, TaskCreate, TaskUpdate, TaskReorder, KanbanBoard } from '@/types/task';

const taskKeys = {
  all: ['tasks'] as const,
  project: (projectId: string) => [...taskKeys.all, 'project', projectId] as const,
  kanban: (projectId: string) => [...taskKeys.project(projectId), 'kanban'] as const,
  detail: (taskId: string) => [...taskKeys.all, 'detail', taskId] as const,
};

export function useTasks(projectId: string, filters?: {
  status?: string;
  assignee_id?: string;
  due_before?: string;
  due_after?: string;
  search?: string;
}) {
  return useQuery({
    queryKey: [...taskKeys.project(projectId), 'list', filters],
    queryFn: () => api.get<Task[]>(`/projects/${projectId}/tasks`, { params: filters }),
    enabled: !!projectId,
  });
}

export function useKanbanBoard(projectId: string) {
  return useQuery({
    queryKey: taskKeys.kanban(projectId),
    queryFn: () => api.get<KanbanBoard>(`/projects/${projectId}/tasks/kanban`),
    enabled: !!projectId,
  });
}

export function useTask(taskId: string) {
  return useQuery({
    queryKey: taskKeys.detail(taskId),
    queryFn: () => api.get<Task>(`/tasks/${taskId}`),
    enabled: !!taskId,
  });
}

export function useCreateTask(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: TaskCreate) => api.post<Task>(`/projects/${projectId}/tasks`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: taskKeys.project(projectId) });
    },
  });
}

export function useUpdateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, data }: { taskId: string; data: TaskUpdate }) =>
      api.patch<Task>(`/tasks/${taskId}`, data),
    onSuccess: (updatedTask) => {
      qc.invalidateQueries({ queryKey: taskKeys.project(updatedTask.project_id) });
      qc.invalidateQueries({ queryKey: taskKeys.detail(updatedTask.id) });
    },
  });
}

export function useReorderTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, data }: { taskId: string; data: { status: string; position: number } }) =>
      api.patch<Task>(`/tasks/${taskId}/reorder`, data),
    onSuccess: (updatedTask) => {
      qc.invalidateQueries({ queryKey: taskKeys.project(updatedTask.project_id) });
    },
  });
}

export function useDeleteTask(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) => api.delete(`/tasks/${taskId}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: taskKeys.project(projectId) });
    },
  });
}
```

### 3. Kanban Board Component (`src/frontend/src/pages/KanbanBoard.tsx`)
```tsx
import { useState } from 'react';
import { useKanbanBoard, useCreateTask, useReorderTask } from '@/hooks/useTasks';
import { KanbanColumn } from '@/components/tasks/KanbanColumn';
import { TaskCreateForm } from '@/components/tasks/TaskCreateForm';
import { TaskStatus } from '@/types/task';
import { Plus } from 'lucide-react';

const STATUSES: { id: TaskStatus; label: string }[] = [
  { id: 'todo', label: 'To Do' },
  { id: 'in_progress', label: 'In Progress' },
  { id: 'review', label: 'Review' },
  { id: 'done', label: 'Done' },
];

export function KanbanBoard({ projectId }: { projectId: string }) {
  const { data: board, isLoading, error } = useKanbanBoard(projectId);
  const createTask = useCreateTask(projectId);
  const reorderTask = useReorderTask();
  const [showForm, setShowForm] = useState<TaskStatus | null>(null);

  const handleReorder = async (taskId: string, status: string, position: number) => {
    await reorderTask.mutateAsync({ taskId, data: { status, position } });
  };

  if (isLoading) return <div className="animate-pulse">Loading board...</div>;
  if (error) return <div className="text-red-500">Failed to load board</div>;

  return (
    <div className="flex gap-4 overflow-x-auto pb-4 h-[calc(100vh-200px)]">
      {STATUSES.map(({ id, label }) => (
        <KanbanColumn
          key={id}
          status={id}
          label={label}
          tasks={board?.[id] || []}
          onReorder={handleReorder}
          onAddTask={() => setShowForm(id)}
        />
      ))}
      {showForm && (
        <TaskCreateForm
          projectId={projectId}
          defaultStatus={showForm}
          onClose={() => setShowForm(null)}
          onSuccess={() => setShowForm(null)}
        />
      )}
    </div>
  );
}
```

### 4. Kanban Column (`src/frontend/src/components/tasks/KanbanColumn.tsx`)
```tsx
import { useDroppable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { Task } from '@/types/task';
import { TaskCard } from './TaskCard';
import { TaskCreateForm } from './TaskCreateForm';
import { Plus } from 'lucide-react';

interface KanbanColumnProps {
  status: string;
  label: string;
  tasks: Task[];
  onReorder: (taskId: string, status: string, position: number) => void;
  onAddTask: () => void;
}

export function KanbanColumn({ status, label, tasks, onReorder, onAddTask }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id: status });

  return (
    <div
      ref={setNodeRef}
      className={`
        flex flex-col min-w-[280px] max-w-[280px] bg-gray-50 rounded-lg border
        ${isOver ? 'border-blue-300 bg-blue-50' : 'border-gray-200'}
      `}
      style={{ minHeight: '400px' }}
    >
      <div className="flex items-center justify-between p-3 border-b">
        <h3 className="font-medium text-gray-700">{label}</h3>
        <span className="text-sm text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
          {tasks.length}
        </span>
      </div>

      <div
        className="flex-1 overflow-y-auto p-2 space-y-2"
        role="list"
        aria-label={`${label} tasks`}
      >
        {tasks.map((task, index) => (
          <TaskCard
            key={task.id}
            task={task}
            index={index}
            onReorder={(position) => onReorder(task.id, task.status, position)}
          />
        ))}
        {tasks.length === 0 && (
          <div className="text-center text-gray-400 py-8 text-sm">
            Drop tasks here
          </div>
        )}
      </div>

      <button
        onClick={onAddTask}
        className="w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 border-t flex items-center justify-center gap-2"
      >
        <Plus className="w-4 h-4" />
        Add task
      </button>
    </div>
  );
}
```

### 5. Task Card (`src/frontend/src/components/tasks/TaskCard.tsx`)
```tsx
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { Task } from '@/types/task';
import { Calendar, User, AlertTriangle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface TaskCardProps {
  task: Task;
  index: number;
  onReorder: (position: number) => void;
}

export function TaskCard({ task, index, onReorder }: TaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useDraggable({
    id: task.id,
    data: { currentStatus: task.status },
  });

  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'done';

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      style={style}
      className={`
        bg-white border rounded-lg p-3 shadow-sm cursor-grab
        ${isDragging ? 'shadow-lg ring-2 ring-blue-500' : 'hover:shadow-md'}
        transition-shadow
      `}
      role="listitem"
      aria-grabbed={isDragging}
    >
      <div className="flex items-start justify-between gap-2">
        <h4 className="font-medium text-gray-900 text-sm flex-1 pr-2">
          {task.title}
        </h4>
        {task.priority > 1 && (
          <span className="flex-shrink-0 text-red-500" title="High priority">⚡</span>
        )}
      </div>

      {task.due_date && (
        <div className="mt-2 flex items-center gap-1 text-xs text-gray-500">
          <Calendar className="w-3 h-3" />
          <span className={isOverdue ? 'text-red-500 font-medium' : ''}>
            {isOverdue ? 'Overdue' : 'Due'}
            {formatDistanceToNow(new Date(task.due_date), { addSuffix: true })}
          </span>
        </div>
      )}

      <div className="mt-2 flex items-center justify-between">
        {task.assignee_name && (
          <div className="flex items-center gap-1 text-xs text-gray-600">
            <User className="w-3 h-3" />
            <span>{task.assignee_name}</span>
          </div>
        )}
        {task.estimated_hours && (
          <span className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
            {task.estimated_hours}h
          </span>
        )}
      </div>

      {task.description && (
        <p className="mt-2 text-sm text-gray-600 line-clamp-2">{task.description}</p>
      )}
    </div>
  );
}
```

### 6. Task Create Form (`src/frontend/src/components/tasks/TaskCreateForm.tsx`)
```tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCreateTask } from '@/hooks/useTasks';
import { TaskCreate, TaskStatus } from '@/types/task';
import { X, Calendar, User, AlertTriangle } from 'lucide-react';

const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255),
  description: z.string().optional(),
  status: z.enum(['todo', 'in_progress', 'review', 'done']).default('todo'),
  priority: z.number().min(0).max(3).default(0),
  assignee_id: z.string().uuid().optional(),
  due_date: z.string().optional(),
  estimated_hours: z.number().min(0).optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskCreateFormProps {
  projectId: string;
  defaultStatus: TaskStatus;
  onClose: () => void;
  onSuccess: () => void;
}

export function TaskCreateForm({ projectId, defaultStatus, onClose, onSuccess }: TaskCreateFormProps) {
  const createTask = useCreateTask(projectId);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: { status: defaultStatus, priority: 0 },
  });

  const handleSubmitForm = async (data: TaskFormData) => {
    setIsSubmitting(true);
    try {
      await createTask.mutateAsync(data);
      onSuccess();
    } catch (error) {
      console.error('Failed to create task:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold">Create Task</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit(handleSubmitForm)} className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input {...register('title')} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea {...register('description')} rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select {...register('status')} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="review">Review</option>
                <option value="done">Done</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select {...register('priority', { valueAsNumber: true })} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <option value={0}>Low</option>
                <option value={1}>Medium</option>
                <option value={2}>High</option>
                <option value={3}>Urgent</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Assignee</label>
            <select {...register('assignee_id')} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="">Unassigned</option>
              {/* Options from useUsers hook */}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              <input type="date" {...register('due_date')} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Est. Hours</label>
              <input type="number" step="0.5" min="0" {...register('estimated_hours', { valueAsNumber: true })} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200">
              Cancel
            </button>
            <button type="submit" disabled={isSubmitting} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
              {isSubmitting ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

## Acceptance Criteria
- [ ] Kanban board loads with 4 columns grouped by status
- [ ] Drag-drop between columns updates status optimistically
- [ ] Reorder within column persists position
- [ ] "Add Task" per column opens form with correct default status
- [ ] Task card shows: title, assignee, due date (red if overdue), priority, estimated hours
- [ ] Form validation works (title required, valid dates, numeric hours)
- [ ] Real-time updates via React Query invalidation
- [ ] Keyboard accessible (ARIA roles, focus management)

---

## Test Command
```bash
pytest .specify/specs/wave-4/contracts/test_wave4_contracts.py::TestKanban -v
```