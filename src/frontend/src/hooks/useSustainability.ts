import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  SustainabilityMetric,
  SustainabilityMetricCreate,
  SustainabilityMetricUpdate,
} from "@/types/api";

export function useSustainabilityMetrics(projectId: string, referenceId?: string) {
  return useQuery({
    queryKey: ["sustainability-metrics", projectId, referenceId],
    queryFn: () => api.listSustainabilityMetrics(projectId, referenceId),
    enabled: !!projectId,
  });
}

export function useCreateSustainabilityMetric(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SustainabilityMetricCreate) =>
      api.createSustainabilityMetric(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sustainability-metrics", projectId] });
    },
  });
}

export function useUpdateSustainabilityMetric(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ metricId, data }: { metricId: string; data: SustainabilityMetricUpdate }) =>
      api.updateSustainabilityMetric(projectId, metricId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sustainability-metrics", projectId] });
    },
  });
}

export function useDeleteSustainabilityMetric(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (metricId: string) => api.deleteSustainabilityMetric(projectId, metricId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sustainability-metrics", projectId] });
    },
  });
}

export type { SustainabilityMetric };
