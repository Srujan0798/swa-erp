import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { taskKeys } from "@/lib/queryKeys";
import type {
  Task,
  TaskComment,
  TaskCreateRequest,
  TaskUpdateRequest,
  TaskStatus,
  TaskListResponse,
  TaskStats,
} from "@/types/api";

export interface TaskFilters {
  page?: number;
  page_size?: number;
  status?: string;
  assignee_id?: string;
  priority?: string;
}

export function useTasks(projectId: string, filters?: TaskFilters) {
  return useQuery<TaskListResponse>({
    queryKey: taskKeys.list(projectId, filters),
    queryFn: () => api.listTasks(projectId, filters),
    enabled: !!projectId,
  });
}

export function useTask(taskId: string) {
  return useQuery<Task>({
    queryKey: taskKeys.detail(taskId),
    queryFn: () => api.getTask(taskId),
    enabled: !!taskId,
  });
}

export function useMyTasks(filters?: TaskFilters) {
  return useQuery<TaskListResponse>({
    queryKey: taskKeys.myTasks(filters),
    queryFn: () => api.getMyTasks(filters),
  });
}

export function useProjectTaskStats(projectId: string) {
  return useQuery<TaskStats>({
    queryKey: taskKeys.stats(projectId),
    queryFn: () => api.getProjectTaskStats(projectId),
    enabled: !!projectId,
  });
}

export function useTaskComments(taskId: string) {
  return useQuery<TaskComment[]>({
    queryKey: taskKeys.comments(taskId),
    queryFn: () => api.listComments(taskId),
    enabled: !!taskId,
  });
}

export function useCreateTask(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TaskCreateRequest) => api.createTask(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.myTasks() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats(projectId) });
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, data }: { taskId: string; data: TaskUpdateRequest }) =>
      api.updateTask(taskId, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(variables.taskId) });
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.myTasks() });
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deleteTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
    },
  });
}

export function useTransitionTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, toStatus }: { taskId: string; toStatus: TaskStatus }) =>
      api.transitionTask(taskId, toStatus),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.myTasks() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats(data.project_id) });
    },
  });
}

export function useReorderTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, status, sortOrder }: { taskId: string; status: TaskStatus; sortOrder: number }) =>
      api.reorderTask(taskId, status, sortOrder),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats(data.project_id) });
    },
  });
}

export function useBulkUpdateStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.bulkUpdateStatus,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
    },
  });
}

export function useAssignTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, assigneeId }: { taskId: string; assigneeId: string }) =>
      api.assignTask(taskId, assigneeId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.myTasks() });
    },
  });
}

export function useUnassignTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.unassignTask,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.myTasks() });
    },
  });
}

export function useAddComment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, content }: { taskId: string; content: string }) =>
      api.addComment(taskId, content),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.comments(variables.taskId) });
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(variables.taskId) });
    },
  });
}
