import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { TaskDetail } from "@/components/tasks/TaskDetail";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export function TaskDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: task, isLoading, isError, error } = useQuery({
    queryKey: ["task", id],
    queryFn: () => api.getTask(id!),
    enabled: !!id,
  });

  if (!id) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (isError || !task) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-destructive">
          {(error as Error)?.message ?? "Task not found"}
        </p>
        <Button variant="outline" asChild>
          <Link to="/tasks">Back to tasks</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <Button variant="ghost" size="sm" asChild>
        <Link to="/tasks">← Back to tasks</Link>
      </Button>
      <TaskDetail task={task} open onClose={() => undefined} />
    </div>
  );
}
