import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { TimeEntryCreate, TimeEntryUpdate } from "@/types/time";

export function useTimeEntries(filters?: { project_id?: string; start_date?: string; end_date?: string }) {
  return useQuery({
    queryKey: ["timeEntries", filters],
    queryFn: () => api.listTimeEntries(filters),
  });
}

export function useCreateTimeEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TimeEntryCreate) => api.createTimeEntry(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timeEntries"] });
    },
  });
}

export function useUpdateTimeEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TimeEntryUpdate }) => api.updateTimeEntry(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timeEntries"] });
    },
  });
}

export function useDeleteTimeEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteTimeEntry(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timeEntries"] });
    },
  });
}
