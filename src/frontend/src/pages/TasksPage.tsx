import { useEffect, useState } from "react";
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
import { taskKeys } from "@/lib/queryKeys";
import { useToast } from "@/hooks/useToast";
import {
  Plus,
  Filter,
  UserRoundPlus,
  LayoutDashboard,
  MessageSquare,
  Trash2,
} from "lucide-react";
import type { Task, TaskStatus, TaskPriority, TaskListResponse, TaskComment } from "@/types/api";

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
  const [newStatus, setNewStatus] = useState<TaskStatus | null>(null);
  const [newSearch, setNewSearch] = useState("");
  const [newAssignee, setNewAssignee] = useState<string>("");

  const tasksQuery = useQuery({
    queryKey: taskKeys.listsForProject(projectId),
    enabled: !!projectId,
    queryFn: async () => {
      const data = await api.listTasks(projectId!, {
        page: 1,
        page_size: 50,
        status: newStatus || undefined,
        assignee_id: newAssignee || undefined,
        priority: undefined,
      });
      return data;
    },
  });

  const { data: myTasks } = useQuery({
    queryKey: ["my-tasks"],
    queryFn: () => api.getMyTasks({ page: 1, page_size: 50 }),
  });

  const { data: users = [] } = useQuery({
    queryKey: ["users-short"],
    queryFn: async () => {
      const data = await api.listUsers({ page: 1, page_size: 200 });
      return data.items;
    },
  });

  const projectOptions = [
    { value: "p1", label: "Project Alpha" },
    { value: "p2", label: "Project Beta" },
  ];

  const createMutation = useMutation({
    mutationFn: async () => {
      const pid = createProjectId || "p1";
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
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.deleteTask(selectedTaskId as string),
    onSuccess: () => {
      toast({ title: "Task deleted" });
      setSelectedTaskId(null);
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });

  const selectedTask = selectedTaskId ? tasksQuery.data?.items.find((t) => t.id === selectedTaskId) : null;

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
            <Select value={projectId ?? ""} onValueChange={setProjectId}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Select project" />
              </SelectTrigger>
              <SelectContent>
                {projectOptions.map((item) => (
                  <SelectItem key={item.value} value={item.value}>{item.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              value={newSearch}
              placeholder="Search..."
              onChange={(e) => setNewSearch(e.target.value)}
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
              projectId={projectId}
              tasks={tasksQuery.data?.items ?? []}
              loading={tasksQuery.isLoading}
              error={tasksQuery.isError ? (tasksQuery.error as Error)?.message ?? "Failed to load tasks" : undefined}
              onRetry={() => tasksQuery.refetch()}
              onSearch={newSearch}
              onAssigneeFilter={newAssignee}
              onStatusFilter={newStatus ?? undefined}
              onOpenTask={(task) => setSelectedTaskId(task.id)}
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
                  {projectOptions.map((item) => (
                    <SelectItem key={item.value} value={item.value}>{item.label}</SelectItem>
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
