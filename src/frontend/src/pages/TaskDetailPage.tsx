import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { TaskDetail } from "@/components/tasks/TaskDetail";
import type { Task } from "@/types/api";
import { Skeleton } from "@/components/ui/skeleton";

export function TaskDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [open, setOpen] = useState(true);
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!id) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    fetch(`/api/tasks/${id}`)
      .then(async (r) => {
        if (!r.ok) {
          const body = await r.json().catch(() => null);
          throw new Error(body?.detail ?? `Failed to load task: ${r.status}`);
        }
        return r.json();
      })
      .then((data) => {
        if (!cancelled) setTask(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message ?? "Failed to load task");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (!id) {
    return null;
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-destructive">{error ?? "Task not found"}</p>
        <button
          className="text-sm underline"
          onClick={() => window.history.back()}
        >
          Back
        </button>
      </div>
    );
  }

  return <TaskDetail task={task} open={open} onClose={() => setOpen(false)} />;
}
