import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ServiceAgreementCreate, ServiceAgreementUpdate } from "@/types/api";

export function useAgreements(params?: { page?: number; page_size?: number; client_id?: string; inquiry_id?: string; status?: string; q?: string }) {
  return useQuery({
    queryKey: ["agreements", params],
    queryFn: () => api.listAgreements(params),
  });
}

export function useAgreement(id: string | undefined) {
  return useQuery({
    queryKey: ["agreement", id],
    queryFn: () => api.getAgreement(id!),
    enabled: !!id,
  });
}

export function useCreateAgreement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ServiceAgreementCreate) => api.createAgreement(data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["agreements"] });
      if (variables.client_id) {
        queryClient.invalidateQueries({ queryKey: ["client-agreements", variables.client_id] });
      }
    },
  });
}

export function useUpdateAgreement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ServiceAgreementUpdate }) =>
      api.updateAgreement(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["agreements"] });
      queryClient.invalidateQueries({ queryKey: ["agreement", variables.id] });
    },
  });
}

export function useDeleteAgreement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteAgreement(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agreements"] });
    },
  });
}
