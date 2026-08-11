"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { KanbanBoard } from "@/components/tasks/KanbanBoard";
import { TaskDetail } from "@/components/tasks/TaskDetail";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/useToast";
import { useCurrentUser } from "@/hooks/useAuth";
import { canWrite } from "@/lib/permissions";
import {
  Plus,
  UserRoundPlus,
  LayoutDashboard,
  MessageSquare,
  Trash2,
} from "lucide-react";
import type { TaskStatus, TaskPriority } from "@/types/api";

export function TasksPage(): JSX.Element {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { data: user } = useCurrentUser();
  const write = canWrite(user);
  const [searchParams, setSearchParams] = useSearchParams();
  const [projectId, setProjectId] = useState<string | null>(
    searchParams.get("project"),
  );
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createProjectId, setCreateProjectId] = useState<string>("");
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newPriority, setNewPriority] = useState<TaskPriority>("medium");
  const [newDueDate, setNewDueDate] = useState<string>("");
  const [newAssigneeId, setNewAssigneeId] = useState<string>("");
  const [searchText, setSearchText] = useState("");

  useEffect(() => {
    const fromUrl = searchParams.get("project");
    if (fromUrl && fromUrl !== projectId) setProjectId(fromUrl);
  }, [searchParams, projectId]);

  const selectProject = (id: string): void => {
    setProjectId(id);
    setSearchParams(id ? { project: id } : {});
  };

  const { data: projectsData } = useQuery({
    queryKey: ["projects-for-tasks"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];

  const { data: assigneesData } = useQuery({
    queryKey: ["assignees"],
    queryFn: () => api.listAssignees({ page_size: 100 }),
  });
  const assignees = assigneesData?.items ?? [];

  const tasksQuery = useQuery({
    queryKey: ["tasks", "list", projectId],
    enabled: !!projectId,
    queryFn: async () => {
      const data = await api.listTasks(projectId!, {
        page: 1,
        page_size: 50,
      });
      return data;
    },
  });

  const { data: myTasks } = useQuery({
    queryKey: ["my-tasks"],
    queryFn: () => api.getMyTasks({ page: 1, page_size: 50 }),
  });

  const selectedTask = selectedTaskId ? tasksQuery.data?.items.find((t) => t.id === selectedTaskId) : null;

  const createMutation = useMutation({
    mutationFn: async () => {
      const pid = createProjectId || projectId;
      if (!pid) throw new Error("Select a project first");
      return api.createTask(pid, {
        title: newTitle,
        description: newDescription || undefined,
        priority: newPriority,
        due_date: newDueDate || undefined,
        assignee_id: newAssigneeId || undefined,
      });
    },
    onSuccess: () => {
      toast({ title: "Task created" });
      setIsCreateOpen(false);
      setNewTitle("");
      setNewDescription("");
      setNewPriority("medium");
      setNewDueDate("");
      setNewAssigneeId("");
      queryClient.invalidateQueries({ queryKey: ["tasks", "list"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.deleteTask(selectedTaskId as string),
    onSuccess: () => {
      toast({ title: "Task deleted" });
      setSelectedTaskId(null);
      queryClient.invalidateQueries({ queryKey: ["tasks", "list"] });
    },
  });

  const transitionMutation = useMutation({
    mutationFn: ({ taskId, status }: { taskId: string; status: TaskStatus }) =>
      api.transitionTask(taskId, status),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["tasks", "list"] });
      void queryClient.invalidateQueries({ queryKey: ["my-tasks"] });
    },
    onError: () => {
      toast({
        title: "Could not update task status",
        variant: "destructive",
      });
    },
  });

  const boardTasks = (tasksQuery.data?.items ?? []).filter((t) => {
    if (!searchText.trim()) return true;
    const q = searchText.toLowerCase();
    return (
      t.title.toLowerCase().includes(q) ||
      (t.description ?? "").toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Tasks</h1>
          <p className="text-sm text-muted-foreground">Create, assign, and track tasks across projects.</p>
        </div>
        {write ? (
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Task
          </Button>
        ) : null}
      </div>

      <Tabs defaultValue="board" className="space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <TabsList>
            <TabsTrigger value="board" className="gap-2">
              <LayoutDashboard className="h-4 w-4" /> Board
            </TabsTrigger>
            <TabsTrigger value="my-tasks" className="gap-2">
              <UserRoundPlus className="h-4 w-4" /> My Tasks
            </TabsTrigger>
            <TabsTrigger value="comments" className="gap-2">
              <MessageSquare className="h-4 w-4" /> Activity
            </TabsTrigger>
          </TabsList>

          <div className="ml-auto flex items-center gap-2">
            <Select
              value={projectId ?? undefined}
              onValueChange={(v) => selectProject(v)}
            >
              <SelectTrigger className="w-72">
                <SelectValue placeholder="Select project" />
              </SelectTrigger>
              <SelectContent>
                {projects.length === 0 ? (
                  <SelectItem value="none" disabled>
                    No projects — run make bootstrap-real
                  </SelectItem>
                ) : (
                  projects.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.code} — {p.name}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
            <Input
              value={searchText}
              placeholder="Search tasks..."
              onChange={(e) => setSearchText(e.target.value)}
              className="w-48"
            />
          </div>
        </div>

        <TabsContent value="board" className="space-y-4">
          {!projectId && (
            <div className="rounded-md border border-dashed p-8 text-center text-sm text-muted-foreground">
              Select a project to load the board, or open a project and use the Tasks quick link.
            </div>
          )}
          {projectId && tasksQuery.isError && (
            <QueryErrorBanner
              message="Failed to load tasks"
              error={tasksQuery.error}
              onRetry={() => void tasksQuery.refetch()}
            />
          )}
          {projectId && !tasksQuery.isError && (
            <>
              <KanbanBoard
                tasks={boardTasks}
                isLoading={tasksQuery.isLoading}
                onTaskClick={(t) => setSelectedTaskId(t.id)}
                onStatusChange={
                  write
                    ? (taskId, newStatus) =>
                        transitionMutation.mutate({ taskId, status: newStatus })
                    : undefined
                }
              />
              {!tasksQuery.isLoading && boardTasks.length === 0 && (
                <p className="text-sm text-muted-foreground text-center">
                  {searchText.trim()
                    ? "No tasks match your search."
                    : "No tasks on this project yet. "}
                  {!searchText.trim() && write ? (
                    <button
                      type="button"
                      className="underline font-medium text-foreground"
                      onClick={() => {
                        setCreateProjectId(projectId);
                        setIsCreateOpen(true);
                      }}
                    >
                      Create the first task
                    </button>
                  ) : null}
                </p>
              )}
            </>
          )}
        </TabsContent>

        <TabsContent value="my-tasks">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(["todo", "in_progress", "done"] as TaskStatus[]).map((status) => (
              <div key={status} className="space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium capitalize">{status.replace("_", " ")}</h3>
                  <Badge variant="outline">{myTasks?.items.filter((t) => t.status === status).length ?? 0}</Badge>
                </div>
                <div className="space-y-2">
                  {(myTasks?.items ?? []).filter((t) => t.status === status).map((t) => (
                    <button
                      key={t.id}
                      onClick={() => setSelectedTaskId(t.id)}
                      className="w-full rounded-md border bg-white p-3 text-left text-sm shadow-sm hover:shadow"
                    >
                      <p className="font-medium truncate">{t.title}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{t.assignee_name ?? "Unassigned"} • {t.due_date ?? "No due date"}</p>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="comments">
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">Task comments and assignment activity will stream here.</p>
            <Separator />
          </div>
        </TabsContent>
      </Tabs>

      <Dialog open={!!selectedTaskId} onOpenChange={(o) => !o && setSelectedTaskId(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="pr-8">Task Detail</DialogTitle>
          </DialogHeader>
          {selectedTask && (
            <TaskDetail task={selectedTask} open onClose={() => setSelectedTaskId(null)} />
          )}
          <Separator />
          <DialogFooter className="justify-between">
            {write ? (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => deleteMutation.mutate()}
                disabled={deleteMutation.isPending || !selectedTaskId}
              >
                <Trash2 className="mr-2 h-4 w-4" /> Delete
              </Button>
            ) : (
              <span />
            )}
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => setSelectedTaskId(null)}>Close</Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Task</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Project</Label>
              <Select value={createProjectId} onValueChange={setCreateProjectId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select project" />
                </SelectTrigger>
                <SelectContent>
                  {projects.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.code} — {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Title</Label>
              <Input value={newTitle} onChange={(e) => setNewTitle(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea value={newDescription} onChange={(e) => setNewDescription(e.target.value)} rows={3} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Priority</Label>
                <Select value={newPriority} onValueChange={(v) => setNewPriority(v as TaskPriority)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Due Date</Label>
                <Input type="date" value={newDueDate} onChange={(e) => setNewDueDate(e.target.value)} />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Assignee</Label>
              <Select
                value={newAssigneeId || "none"}
                onValueChange={(v) => setNewAssigneeId(v === "none" ? "" : v)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Unassigned" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Unassigned</SelectItem>
                  {assignees.map((u) => (
                    <SelectItem key={u.id} value={u.id}>
                      {u.name} ({u.role})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
            <Button onClick={() => createMutation.mutate()} disabled={createMutation.isPending || !newTitle.trim()}>
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
