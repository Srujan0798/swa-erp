import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { clearTokens, setTokens } from "@/lib/auth";
import type { LoginRequest } from "@/types/api";
import { useNavigate } from "react-router-dom";

export function useAuth() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data: user, isLoading } = useQuery({
    queryKey: ["currentUser"],
    queryFn: api.me,
    retry: false,
    staleTime: Infinity,
  });

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginRequest) => api.login(credentials),
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      queryClient.setQueryData(["currentUser"], data.user);
      navigate("/dashboard");
    },
  });

  const logoutMutation = useMutation({
    mutationFn: api.logout,
    onSettled: () => {
      clearTokens();
      queryClient.clear();
      navigate("/login");
    },
  });

  return {
    isAuthenticated: !!user,
    user,
    isLoading,
    login: loginMutation.mutateAsync,
    logout: logoutMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
  };
}

export function useCurrentUser() {
  return useQuery({
    queryKey: ["currentUser"],
    queryFn: api.me,
    retry: false,
    staleTime: Infinity,
  });
}

export function useUsers(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["users", page, pageSize],
    queryFn: () => api.listUsers({ page, page_size: pageSize }),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof api.updateUser>[1] }) =>
      api.updateUser(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deleteUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
}