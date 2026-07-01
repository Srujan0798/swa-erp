import { useState, useMemo } from "react";
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
  type DragOverEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
  arrayMove,
  sortableKeyboardCoordinates,
} from "@dnd-kit/sortable";
import { useDroppable } from "@dnd-kit/core";
import { TaskCard } from "./TaskCard";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import type { Task, TaskStatus } from "@/types/api";

interface ColumnDef {
  id: TaskStatus;
  label: string;
  color: string;
  headerBg: string;
}

const COLUMNS: ColumnDef[] = [
  { id: "todo", label: "Todo", color: "border-gray-300", headerBg: "bg-gray-50" },
  { id: "in_progress", label: "In Progress", color: "border-blue-300", headerBg: "bg-blue-50" },
  { id: "done", label: "Done", color: "border-green-300", headerBg: "bg-green-50" },
];

interface TaskColumnProps {
  column: ColumnDef;
  tasks: Task[];
  onTaskClick: (task: Task) => void;
  showProject?: boolean;
  projectNames?: Record<string, string>;
}

function TaskColumn({ column, tasks, onTaskClick, showProject, projectNames }: TaskColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id: column.id });

  return (
    <div className="flex flex-col min-w-[300px] w-[300px] flex-shrink-0">
      <div
        className={cn(
          "flex items-center justify-between px-3 py-2 rounded-t-lg border-t-2 border-x-2",
          column.color,
          column.headerBg
        )}
      >
        <h3 className="text-sm font-semibold">{column.label}</h3>
        <span className="text-xs text-muted-foreground bg-background rounded-full px-2 py-0.5 font-medium">
          {tasks.length}
        </span>
      </div>
      <div
        ref={setNodeRef}
        className={cn(
          "flex-1 rounded-b-lg border border-t-0 p-2 space-y-2 min-h-[200px] transition-colors",
          isOver ? "bg-accent/50" : "bg-muted/30",
          column.color
        )}
      >
        <SortableContext items={tasks.map((t) => t.id)} strategy={verticalListSortingStrategy}>
          {tasks.length === 0 ? (
            <div className="flex items-center justify-center h-24 text-sm text-muted-foreground">
              No tasks
            </div>
          ) : (
            tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onClick={onTaskClick}
                showProject={showProject}
                projectName={projectNames?.[task.project_id]}
              />
            ))
          )}
        </SortableContext>
      </div>
    </div>
  );
}

function BoardSkeleton() {
  return (
    <div className="flex gap-4">
      {COLUMNS.map((col) => (
        <div key={col.id} className="flex-1 min-w-[300px]">
          <Skeleton className="h-10 rounded-t-lg mb-2" />
          <div className="space-y-2">
            <Skeleton className="h-28 rounded-lg" />
            <Skeleton className="h-28 rounded-lg" />
          </div>
        </div>
      ))}
    </div>
  );
}

interface KanbanBoardProps {
  tasks: Task[];
  isLoading?: boolean;
  onTaskClick: (task: Task) => void;
  onStatusChange?: (taskId: string, newStatus: TaskStatus) => void;
  onReorder?: (taskId: string, newStatus: TaskStatus, newOrder: number) => void;
  showProject?: boolean;
  projectNames?: Record<string, string>;
}

export function KanbanBoard({
  tasks,
  isLoading,
  onTaskClick,
  onStatusChange,
  onReorder,
  showProject,
  projectNames,
}: KanbanBoardProps) {
  const [activeTask, setActiveTask] = useState<Task | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const tasksByStatus = useMemo(() => {
    const grouped: Record<TaskStatus, Task[]> = {
      todo: [],
      in_progress: [],
      done: [],
    };
    for (const task of tasks) {
      if (grouped[task.status]) {
        grouped[task.status].push(task);
      }
    }
    for (const status of Object.keys(grouped) as TaskStatus[]) {
      grouped[status].sort((a, b) => a.sort_order - b.sort_order);
    }
    return grouped;
  }, [tasks]);

  function handleDragStart(event: DragStartEvent) {
    const task = tasks.find((t) => t.id === event.active.id);
    if (task) setActiveTask(task);
  }

  function handleDragEnd(event: DragEndEvent) {
    setActiveTask(null);
    const { active, over } = event;
    if (!over) return;

    const activeTask = tasks.find((t) => t.id === active.id);
    if (!activeTask) return;

    let newStatus: TaskStatus = activeTask.status;
    let newOrder = activeTask.sort_order;

    const overColumn = COLUMNS.find((c) => c.id === over.id);
    if (overColumn) {
      newStatus = overColumn.id;
      newOrder = tasksByStatus[newStatus].length;
    } else {
      const overTask = tasks.find((t) => t.id === over.id);
      if (overTask) {
        newStatus = overTask.status;
        const colTasks = tasksByStatus[newStatus];
        const overIndex = colTasks.findIndex((t) => t.id === over.id);
        newOrder = overIndex >= 0 ? overIndex : colTasks.length;
      }
    }

    if (newStatus !== activeTask.status) {
      onStatusChange?.(activeTask.id, newStatus);
    }
    onReorder?.(activeTask.id, newStatus, newOrder);
  }

  function handleDragOver(event: DragOverEvent) {
    const { active, over } = event;
    if (!over) return;

    const activeTask = tasks.find((t) => t.id === active.id);
    if (!activeTask) return;

    const overColumn = COLUMNS.find((c) => c.id === over.id);
    if (overColumn && activeTask.status !== overColumn.id) {
      onStatusChange?.(activeTask.id, overColumn.id);
    }
  }

  if (isLoading) return <BoardSkeleton />;

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragOver={handleDragOver}
    >
      <div className="flex gap-4 overflow-x-auto pb-4">
        {COLUMNS.map((column) => (
          <TaskColumn
            key={column.id}
            column={column}
            tasks={tasksByStatus[column.id]}
            onTaskClick={onTaskClick}
            showProject={showProject}
            projectNames={projectNames}
          />
        ))}
      </div>
      <DragOverlay>
        {activeTask ? (
          <div className="opacity-90 rotate-2">
            <TaskCard task={activeTask} onClick={() => {}} />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
