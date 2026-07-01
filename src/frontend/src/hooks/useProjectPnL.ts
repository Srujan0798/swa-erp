import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ProjectCostCreate } from "@/types/financial";

export function useProjectPnL(projectId: string) {
  return useQuery({
    queryKey: ["projectPnL", projectId],
    queryFn: () => api.getProjectPnL(projectId),
    enabled: !!projectId,
  });
}

export function useProjectCosts(projectId: string, category?: string) {
  return useQuery({
    queryKey: ["projectCosts", projectId, category],
    queryFn: () => api.listProjectCosts(projectId, { category }),
    enabled: !!projectId,
  });
}

export function useAddProjectCost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: ProjectCostCreate }) =>
      api.addProjectCost(projectId, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["projectCosts", variables.projectId] });
      queryClient.invalidateQueries({ queryKey: ["projectPnL", variables.projectId] });
    },
  });
}

export function useDeleteProjectCost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, costId }: { projectId: string; costId: string }) =>
      api.deleteProjectCost(projectId, costId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["projectCosts", variables.projectId] });
      queryClient.invalidateQueries({ queryKey: ["projectPnL", variables.projectId] });
    },
  });
}
