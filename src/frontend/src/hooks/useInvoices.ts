import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { InvoiceCreate } from "@/types/financial";

export function useProjectInvoices(projectId: string, status?: string) {
  return useQuery({
    queryKey: ["invoices", projectId, status],
    queryFn: () => api.listProjectInvoices(projectId, { status }),
    enabled: !!projectId,
  });
}

export function useInvoice(id: string) {
  return useQuery({
    queryKey: ["invoice", id],
    queryFn: () => api.getInvoice(id),
    enabled: !!id,
  });
}

export function useCreateInvoice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: InvoiceCreate }) =>
      api.createInvoice(projectId, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["invoices", variables.projectId] });
    },
  });
}

export function useGenerateInvoiceFromTime() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      startDate,
      endDate,
    }: {
      projectId: string;
      startDate: string;
      endDate: string;
    }) => api.generateInvoiceFromTime(projectId, startDate, endDate),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["invoices", variables.projectId] });
    },
  });
}

export function useUpdateInvoiceStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: "draft" | "sent" | "paid" }) =>
      api.updateInvoiceStatus(id, status),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["invoice", data.id] });
      queryClient.invalidateQueries({ queryKey: ["invoices", data.project_id] });
    },
  });
}

export function useDeleteInvoice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteInvoice(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
    },
  });
}
