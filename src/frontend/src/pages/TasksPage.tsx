"use client";

import { useState } from "react";
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
import { api } from "@/lib/api";
import { useToast } from "@/hooks/useToast";
import {
  Plus,
  Filter,
  UserRoundPlus,
  LayoutDashboard,
  MessageSquare,
  Trash2,
} from "lucide-react";
import type { TaskStatus, TaskPriority } from "@/types/api";

export function TasksPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [projectId, setProjectId] = useState<string | null>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createProjectId, setCreateProjectId] = useState<string>("");
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newPriority, setNewPriority] = useState<TaskPriority>("medium");
  const [newDueDate, setNewDueDate] = useState<string>("");
  const [newAssigneeId, setNewAssigneeId] = useState<string>("");

  const { data: projectsData } = useQuery({
    queryKey: ["projects-for-tasks"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];

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

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Tasks</h1>
          <p className="text-sm text-muted-foreground">Create, assign, and track tasks across projects.</p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Task
        </Button>
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
              onValueChange={(v) => setProjectId(v)}
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
              value={newTitle}
              placeholder="Search..."
              onChange={(e) => setNewTitle(e.target.value)}
            />
            <Button variant="outline" onClick={() => {}}>
              <Filter className="mr-2 h-4 w-4" /> Filter
            </Button>
          </div>
        </div>

        <TabsContent value="board" className="space-y-4">
          {!projectId && (
            <p className="text-sm text-muted-foreground">Select a project to load the board.</p>
          )}
          {projectId && (
            <KanbanBoard
              tasks={tasksQuery.data?.items ?? []}
              isLoading={tasksQuery.isLoading}
              onTaskClick={(t) => setSelectedTaskId(t.id)}
            />
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
            <Button
              variant="destructive"
              size="sm"
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending || !selectedTaskId}
            >
              <Trash2 className="mr-2 h-4 w-4" /> Delete
            </Button>
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
