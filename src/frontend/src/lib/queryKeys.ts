import type { TaskFilters } from "@/hooks/useTasks";

export const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const,
  list: (projectId: string, filters?: TaskFilters) => [...taskKeys.lists(), projectId, filters] as const,
  details: () => [...taskKeys.all, "detail"] as const,
  detail: (taskId: string) => [...taskKeys.details(), taskId] as const,
  myTasks: (filters?: TaskFilters) => [...taskKeys.all, "my", filters] as const,
  stats: (projectId: string) => [...taskKeys.all, "stats", projectId] as const,
  comments: (taskId: string) => [...taskKeys.all, "comments", taskId] as const,
};
