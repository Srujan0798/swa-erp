import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { InquiryCreate, InquiryUpdate, InquiryConvertPayload } from "@/types/api";

export function useInquiries(params?: { page?: number; page_size?: number; q?: string; status?: string }) {
  return useQuery({
    queryKey: ["inquiries", params],
    queryFn: () => api.listInquiries(params),
  });
}

export function useInquiry(id: string | undefined) {
  return useQuery({
    queryKey: ["inquiry", id],
    queryFn: () => api.getInquiry(id!),
    enabled: !!id,
  });
}

export function useCreateInquiry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: InquiryCreate) => api.createInquiry(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inquiries"] });
    },
  });
}

export function useUpdateInquiry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: InquiryUpdate }) =>
      api.updateInquiry(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["inquiries"] });
      queryClient.invalidateQueries({ queryKey: ["inquiry", variables.id] });
    },
  });
}

export function useDeleteInquiry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteInquiry(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inquiries"] });
    },
  });
}

export function useConvertInquiry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: InquiryConvertPayload }) =>
      api.convertInquiry(id, payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["inquiries"] });
      queryClient.invalidateQueries({ queryKey: ["inquiry", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}
