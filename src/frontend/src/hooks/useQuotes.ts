import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useQuotes(projectId: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["quotes", projectId, page, pageSize],
    queryFn: () => api.listQuotes(projectId, { page, page_size: pageSize }),
  });
}

export function useQuote(quoteId: string) {
  return useQuery({
    queryKey: ["quote", quoteId],
    queryFn: () => api.getQuote(quoteId),
    enabled: !!quoteId,
  });
}

export function useCreateQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      data,
    }: {
      projectId: string;
      data: {
        boq_id: string;
        markup_percent?: number;
        tax_percent?: number;
        terms?: string;
        validity_days?: number;
      };
    }) => api.createQuote(projectId, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["quotes", variables.projectId] });
    },
  });
}

export function useUpdateQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<import("@/types/api").Quote> }) =>
      api.updateQuote(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["quote", variables.id] });
    },
  });
}

export function useDeleteQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, projectId }: { id: string; projectId: string }) =>
      api.deleteQuote(id).then(() => ({ projectId })),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["quotes", variables.projectId] });
    },
  });
}

export function useSubmitQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.submitQuote,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["quote", data.id] });
      queryClient.invalidateQueries({ queryKey: ["quotes", data.project_id] });
    },
  });
}

export function useApproveQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.approveQuote,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["quote", data.id] });
      queryClient.invalidateQueries({ queryKey: ["quotes", data.project_id] });
    },
  });
}

export function useSendQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.sendQuote,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["quote", data.id] });
      queryClient.invalidateQueries({ queryKey: ["quotes", data.project_id] });
    },
  });
}

export function useRespondQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { response: "accepted" | "rejected"; notes?: string };
    }) => api.respondQuote(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["quote", data.id] });
      queryClient.invalidateQueries({ queryKey: ["quotes", data.project_id] });
    },
  });
}

export function useCloneQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, projectId }: { id: string; projectId: string }) =>
      api.cloneQuote(id).then((quote) => ({ quote, projectId })),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["quotes", variables.projectId] });
    },
  });
}
