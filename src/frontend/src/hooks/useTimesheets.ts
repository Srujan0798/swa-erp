import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useTimesheets(filters?: { status?: string }) {
  return useQuery({
    queryKey: ["timesheets", filters],
    queryFn: () => api.listTimesheets(filters),
  });
}

export function useTimesheet(id: string) {
  return useQuery({
    queryKey: ["timesheet", id],
    queryFn: () => api.getTimesheet(id),
    enabled: !!id,
  });
}

export function useGenerateTimesheet() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (weekStart: string) => api.generateTimesheet(weekStart),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timesheets"] });
    },
  });
}

export function useSubmitTimesheet() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.submitTimesheet(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timesheets"] });
    },
  });
}

export function useApproveTimesheet() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.approveTimesheet(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timesheets"] });
    },
  });
}

export function useRejectTimesheet() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.rejectTimesheet(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timesheets"] });
    },
  });
}
