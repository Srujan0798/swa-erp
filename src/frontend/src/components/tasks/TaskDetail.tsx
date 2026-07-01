import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/useToast";
import { Trash2, Send, MessageSquare } from "lucide-react";
import type { Task, TaskStatus, TaskPriority } from "@/types/api";
import { taskKeys } from "@/lib/queryKeys";

const STATUS_OPTIONS: { value: TaskStatus; label: string }[] = [
  { value: "todo", label: "Todo" },
  { value: "in_progress", label: "In Progress" },
  { value: "done", label: "Done" },
];

const PRIORITY_OPTIONS: { value: TaskPriority; label: string; className: string }[] = [
  { value: "low", label: "Low", className: "bg-gray-100 text-gray-700" },
  { value: "medium", label: "Medium", className: "bg-blue-100 text-blue-700" },
  { value: "high", label: "High", className: "bg-orange-100 text-orange-700" },
  { value: "critical", label: "Critical", className: "bg-red-100 text-red-700" },
];

const STATUS_TRANSITIONS: Record<TaskStatus, TaskStatus[]> = {
  todo: ["in_progress"],
  in_progress: ["done"],
  done: [],
};

interface TaskDetailProps {
  task: Task;
  open: boolean;
  onClose: () => void;
}

export function TaskDetail({ task, open, onClose }: TaskDetailProps) {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description ?? "");
  const [status, setStatus] = useState<TaskStatus>(task.status);
  const [priority, setPriority] = useState<TaskPriority>(task.priority);
  const [dueDate, setDueDate] = useState(task.due_date ?? "");
  const [commentText, setCommentText] = useState("");
  const [isEditing, setIsEditing] = useState(false);

  const { data: comments = [] } = useQuery({
    queryKey: taskKeys.comments(task.id),
    queryFn: () => api.listComments(task.id),
    enabled: open,
  });

  const updateMutation = useMutation({
    mutationFn: (data: { title?: string; description?: string; priority?: TaskPriority; due_date?: string }) =>
      api.updateTask(task.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(task.id) });
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.myTasks() });
      setIsEditing(false);
      toast({ title: "Task updated" });
    },
    onError: () => {
      toast({ title: "Failed to update task", variant: "destructive" });
    },
  });

  const transitionMutation = useMutation({
    mutationFn: (toStatus: TaskStatus) => api.transitionTask(task.id, toStatus),
    onSuccess: (data) => {
      setStatus(data.status);
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(task.id) });
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.myTasks() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats(data.project_id) });
      toast({ title: `Task moved to ${data.status.replace("_", " ")}` });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.deleteTask(task.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
      onClose();
      toast({ title: "Task deleted" });
    },
  });

  const commentMutation = useMutation({
    mutationFn: (content: string) => api.addComment(task.id, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.comments(task.id) });
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(task.id) });
      setCommentText("");
      toast({ title: "Comment added" });
    },
  });

  const handleSave = () => {
    updateMutation.mutate({ title, description: description || undefined, priority, due_date: dueDate || undefined });
  };

  const handleTransition = (toStatus: TaskStatus) => {
    transitionMutation.mutate(toStatus);
  };

  const handleAddComment = () => {
    if (commentText.trim()) {
      commentMutation.mutate(commentText.trim());
    }
  };

  const allowedTransitions = STATUS_TRANSITIONS[status];
  const priorityOption = PRIORITY_OPTIONS.find((p) => p.value === priority);

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="pr-8">{isEditing ? "Edit Task" : task.title}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {isEditing ? (
            <>
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Priority</Label>
                  <Select value={priority} onValueChange={(v) => setPriority(v as TaskPriority)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PRIORITY_OPTIONS.map((p) => (
                        <SelectItem key={p.value} value={p.value}>
                          {p.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="dueDate">Due Date</Label>
                  <Input
                    id="dueDate"
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                  />
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="space-y-1">
                  <span className="text-muted-foreground">Status</span>
                  <Badge variant="outline" className="capitalize">
                    {status.replace("_", " ")}
                  </Badge>
                </div>
                <div className="space-y-1">
                  <span className="text-muted-foreground">Priority</span>
                  <Badge variant="outline" className={priorityOption?.className}>
                    {priorityOption?.label}
                  </Badge>
                </div>
                <div className="space-y-1">
                  <span className="text-muted-foreground">Assignee</span>
                  <p>{task.assignee_name ?? "Unassigned"}</p>
                </div>
                <div className="space-y-1">
                  <span className="text-muted-foreground">Due Date</span>
                  <p>{task.due_date ?? "No due date"}</p>
                </div>
              </div>
              {description && (
                <div className="space-y-1 text-sm">
                  <span className="text-muted-foreground">Description</span>
                  <p className="whitespace-pre-wrap">{description}</p>
                </div>
              )}
            </>
          )}

          {allowedTransitions.length > 0 && (
            <div className="border-t pt-4">
              <Label className="text-sm text-muted-foreground mb-2 block">Move to</Label>
              <div className="flex gap-2">
                {allowedTransitions.map((s) => (
                  <Button
                    key={s}
                    variant="outline"
                    size="sm"
                    onClick={() => handleTransition(s)}
                    disabled={transitionMutation.isPending}
                  >
                    {s === "in_progress" ? "Start" : "Complete"}
                  </Button>
                ))}
              </div>
            </div>
          )}

          <div className="border-t pt-4">
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare className="h-4 w-4" />
              <span className="text-sm font-medium">
                Comments ({comments.length})
              </span>
            </div>
            <div className="space-y-3 max-h-48 overflow-y-auto">
              {comments.map((comment) => (
                <div key={comment.id} className="bg-muted rounded-md p-3 text-sm">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">{comment.user_name}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(comment.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="whitespace-pre-wrap">{comment.content}</p>
                </div>
              ))}
              {comments.length === 0 && (
                <p className="text-sm text-muted-foreground">No comments yet</p>
              )}
            </div>
            <div className="flex gap-2 mt-3">
              <Input
                placeholder="Add a comment..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleAddComment()}
              />
              <Button
                size="icon"
                variant="outline"
                onClick={handleAddComment}
                disabled={!commentText.trim() || commentMutation.isPending}
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        <DialogFooter className="flex-row justify-between">
          <Button variant="destructive" size="sm" onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending}>
            <Trash2 className="h-4 w-4 mr-1" />
            Delete
          </Button>
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <Button variant="outline" size="sm" onClick={() => setIsEditing(false)}>
                  Cancel
                </Button>
                <Button size="sm" onClick={handleSave} disabled={updateMutation.isPending || !title.trim()}>
                  Save
                </Button>
              </>
            ) : (
              <Button size="sm" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
