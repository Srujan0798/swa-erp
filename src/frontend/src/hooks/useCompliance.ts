import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ComplianceStatus } from "@/types/compliance";

export function useStandards() {
  return useQuery({
    queryKey: ["compliance-standards"],
    queryFn: api.listStandards,
  });
}

export function useChecklistItems(standardId: string) {
  return useQuery({
    queryKey: ["compliance-checklist", standardId],
    queryFn: () => api.getChecklistItems(standardId),
    enabled: !!standardId,
  });
}

export function useComplianceSummary(projectId: string) {
  return useQuery({
    queryKey: ["compliance-summary", projectId],
    queryFn: () => api.getComplianceSummary(projectId),
    enabled: !!projectId,
  });
}

export function useComplianceItems(projectId: string, standardId?: string) {
  return useQuery({
    queryKey: ["compliance-items", projectId, standardId],
    queryFn: () => api.listComplianceItems(projectId, standardId),
    enabled: !!projectId,
  });
}

export function useUpdateComplianceItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      itemId,
      data,
    }: {
      itemId: string;
      data: { status?: ComplianceStatus; notes?: string; evidence_document_id?: string | null };
    }) => api.updateComplianceItem(itemId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance-items"] });
      queryClient.invalidateQueries({ queryKey: ["compliance-summary"] });
    },
  });
}

export function useReviewComplianceItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ itemId, notes }: { itemId: string; notes?: string }) =>
      api.reviewComplianceItem(itemId, notes ? { notes } : undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance-items"] });
      queryClient.invalidateQueries({ queryKey: ["compliance-summary"] });
    },
  });
}

export function useBulkCreateItems(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (standardId: string) =>
      api.bulkCreateComplianceItems(projectId, standardId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance-items", projectId] });
      queryClient.invalidateQueries({ queryKey: ["compliance-summary", projectId] });
    },
  });
}
