import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useBoqs(projectId: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["boqs", projectId, page, pageSize],
    queryFn: () => api.listBoqs(projectId, { page, page_size: pageSize }),
    enabled: !!projectId,
  });
}

export function useBoq(boqId: string) {
  return useQuery({
    queryKey: ["boq", boqId],
    queryFn: () => api.getBoq(boqId),
    enabled: !!boqId,
  });
}

export function useBoqItems(boqId: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["boqItems", boqId, page, pageSize],
    queryFn: () => api.getBoqItems(boqId, { page, page_size: pageSize }),
    enabled: !!boqId,
  });
}

export function useUploadBoq() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, file, notes }: { projectId: string; file: File; notes?: string }) =>
      api.uploadBoq(projectId, file, notes),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["boqs", variables.projectId] });
    },
  });
}

export function useDeleteBoq() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deleteBoq,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["boqs"] });
    },
  });
}
