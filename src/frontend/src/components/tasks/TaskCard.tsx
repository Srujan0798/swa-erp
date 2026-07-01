import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Calendar, MessageSquare, GripVertical } from "lucide-react";
import type { Task, TaskPriority } from "@/types/api";

const PRIORITY_CONFIG: Record<TaskPriority, { label: string; className: string }> = {
  low: { label: "Low", className: "bg-gray-100 text-gray-700 border-gray-200" },
  medium: { label: "Medium", className: "bg-blue-100 text-blue-700 border-blue-200" },
  high: { label: "High", className: "bg-orange-100 text-orange-700 border-orange-200" },
  critical: { label: "Critical", className: "bg-red-100 text-red-700 border-red-200" },
};

function getDueDateInfo(dueDate: string | null): { text: string; className: string } | null {
  if (!dueDate) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(dueDate + "T00:00:00");
  due.setHours(0, 0, 0, 0);
  const diffDays = Math.ceil((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return { text: `${Math.abs(diffDays)}d overdue`, className: "text-red-600" };
  }
  if (diffDays === 0) {
    return { text: "Due today", className: "text-orange-600" };
  }
  if (diffDays === 1) {
    return { text: "Due tomorrow", className: "text-orange-500" };
  }
  return { text: `Due in ${diffDays}d`, className: "text-muted-foreground" };
}

function getInitials(name: string | null): string {
  if (!name) return "?";
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

interface TaskCardProps {
  task: Task;
  onClick: (task: Task) => void;
  showProject?: boolean;
  projectName?: string;
}

export function TaskCard({ task, onClick, showProject, projectName }: TaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const priorityConfig = PRIORITY_CONFIG[task.priority];
  const dueDateInfo = getDueDateInfo(task.due_date);

  return (
    <div ref={setNodeRef} style={style} {...attributes}>
      <Card
        className={cn(
          "p-3 cursor-pointer hover:shadow-md transition-shadow group",
          isDragging && "shadow-lg opacity-90 ring-2 ring-primary/20"
        )}
        onClick={() => onClick(task)}
      >
        <div className="flex items-start gap-2">
          <button
            className="mt-0.5 cursor-grab active:cursor-grabbing text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 transition-opacity"
            {...listeners}
            aria-label="Drag to reorder"
          >
            <GripVertical className="h-4 w-4" />
          </button>
          <div className="flex-1 min-w-0 space-y-2">
            {showProject && projectName && (
              <p className="text-xs text-muted-foreground truncate">{projectName}</p>
            )}
            <p className="text-sm font-medium leading-snug line-clamp-2">{task.title}</p>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="outline" className={cn("text-xs", priorityConfig.className)}>
                {priorityConfig.label}
              </Badge>
              {task.comment_count > 0 && (
                <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                  <MessageSquare className="h-3 w-3" />
                  {task.comment_count}
                </span>
              )}
            </div>
            <div className="flex items-center justify-between">
              {task.assignee_name ? (
                <div className="flex items-center gap-1.5">
                  <div className="h-5 w-5 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-[10px] font-medium text-primary">
                      {getInitials(task.assignee_name)}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground truncate max-w-[100px]">
                    {task.assignee_name}
                  </span>
                </div>
              ) : (
                <span className="text-xs text-muted-foreground italic">Unassigned</span>
              )}
              {dueDateInfo && (
                <span className={cn("inline-flex items-center gap-1 text-xs", dueDateInfo.className)}>
                  <Calendar className="h-3 w-3" />
                  {dueDateInfo.text}
                </span>
              )}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
