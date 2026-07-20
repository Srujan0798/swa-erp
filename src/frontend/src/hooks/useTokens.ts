import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { TokenCreate, TokenUpdate } from "@/types/api";

export function useTokens(params?: { page?: number; page_size?: number; agreement_id?: string; project_id?: string; status?: string; q?: string }) {
  return useQuery({
    queryKey: ["tokens", params],
    queryFn: () => api.listTokens(params),
  });
}

export function useToken(id: string | undefined) {
  return useQuery({
    queryKey: ["token", id],
    queryFn: () => api.getToken(id!),
    enabled: !!id,
  });
}

export function useCreateToken() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TokenCreate) => api.createToken(data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tokens"] });
      queryClient.invalidateQueries({ queryKey: ["agreement-tokens", variables.agreement_id] });
    },
  });
}

export function useUpdateToken() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TokenUpdate }) =>
      api.updateToken(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tokens"] });
      queryClient.invalidateQueries({ queryKey: ["token", variables.id] });
    },
  });
}

export function useDeleteToken() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteToken(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tokens"] });
    },
  });
}
