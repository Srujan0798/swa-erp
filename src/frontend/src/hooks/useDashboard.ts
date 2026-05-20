import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useDashboard() {
  return useQuery({
    queryKey: ["projectStats"],
    queryFn: api.getProjectStats,
  });
}

export function useProjects(page = 1, pageSize = 5) {
  return useQuery({
    queryKey: ["projects", page, pageSize],
    queryFn: () => api.listProjects({ page, page_size: pageSize }),
  });
}

export function useClients(page = 1, pageSize = 5) {
  return useQuery({
    queryKey: ["clients", page, pageSize],
    queryFn: () => api.listClients({ page, page_size: pageSize }),
  });
}