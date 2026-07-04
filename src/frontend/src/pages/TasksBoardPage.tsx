import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

type Status = "todo" | "in_progress" | "done";
type Task = {
  id: string;
  title: string;
  status: Status;
  priority: string;
  assignee_name: string | null;
  due_date: string | null;
};

async function fetchTasks() {
  const res = await fetch("/api/projects/tasks");
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Failed to load tasks: ${res.status}`);
  }
  return res.json() as Promise<{ items: Task[] }>;
}

export function TasksBoardPage() {
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["tasks"], queryFn: fetchTasks });
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [priorityFilter, setPriorityFilter] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<Status | null>(null);

  const columns: { key: Status; label: string }[] = [
    { key: "todo", label: "Todo" },
    { key: "in_progress", label: "In Progress" },
    { key: "done", label: "Done" },
  ];

  const items = data?.items ?? [];
  const filtered = items.filter((task) => {
    if (statusFilter !== "all" && task.status !== statusFilter) return false;
    if (priorityFilter !== "all" && task.priority !== priorityFilter) return false;
    return true;
  });

  const errorMessage = error ? (error instanceof Error ? error.message : "Failed to load tasks") : null;

  if (isLoading) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-muted-foreground">Loading board...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="font-semibold">Task Board</div>
        <select
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
          className="rounded-md border px-2 py-1 text-sm"
        >
          <option value="all">All statuses</option>
          {columns.map((col) => (
            <option key={col.key} value={col.key}>
              {col.label}
            </option>
          ))}
        </select>
        <select
          value={priorityFilter}
          onChange={(event) => setPriorityFilter(event.target.value)}
          className="rounded-md border px-2 py-1 text-sm"
        >
          <option value="all">All priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
        <button
          className="rounded-md bg-primary px-3 py-1 text-sm text-primary-foreground"
          onClick={() => {
            const next = prompt("New task title");
            if (next?.trim()) {
              fetch("/api/projects/tasks", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title: next.trim() }),
              })
                .then(async (r) => {
                  if (!r.ok) throw new Error("Failed to create task");
                  return r.json();
                })
                .then(() => refetch())
                .catch((err) => alert(err.message));
            }
          }}
        >
          Create Task
        </button>
      </div>

      {errorMessage ? (
        <div className="rounded-md border border-destructive/40 bg-destructive/5 p-4 text-sm text-destructive">
          <div className="font-semibold">Could not load the board</div>
          <div className="mt-1">{errorMessage}</div>
          <button className="mt-2 text-sm underline" onClick={() => refetch()}>
            Retry
          </button>
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-3">
        {columns.map((column) => {
          const columnTasks = filtered.filter((task) => task.status === column.key);
          return (
            <div key={column.key} className="rounded-lg border bg-muted/30 p-3">
              <div className="flex items-center justify-between text-sm font-medium">
                <span>{column.label}</span>
                <span className="text-xs text-muted-foreground">{columnTasks.length}</span>
              </div>
              {columnTasks.length === 0 ? (
                <p className="mt-4 text-center text-xs text-muted-foreground">No tasks</p>
              ) : (
                <div className="mt-3 space-y-2">
                  {columnTasks.map((task) => (
                    <button
                      key={task.id}
                      onClick={() => setSelectedStatus(task.status)}
                      className="w-full rounded-md border bg-white p-3 text-left shadow-sm transition hover:shadow"
                    >
                      <div className="text-sm font-medium">{task.title}</div>
                      <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                        <span>{task.assignee_name ?? "Unassigned"}</span>
                        <span>{task.due_date ?? "No due date"}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {selectedStatus ? (
        <div className="text-xs text-muted-foreground">
          Selected column context: {selectedStatus}
        </div>
      ) : null}
    </div>
  );
}
