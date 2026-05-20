import type {
  LoginRequest,
  TokenResponse,
  AccessTokenResponse,
  MessageResponse,
  UserListResponse,
  UserCreate,
  UserUpdate,
  User,
  ProjectListResponse,
  ProjectStats,
  ClientListResponse,
  Project,
  Client,
  Contact,
  ProjectStatus,
} from "@/types/api";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./auth";

class ApiError extends Error {
  constructor(public status: number, public body: unknown) {
    super(`API Error: ${status}`);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response = await fetch(path, { ...options, headers });

  if (response.status === 401) {
    const refresh = getRefreshToken();
    if (refresh) {
      try {
        const refreshResponse = await fetch("/api/auth/refresh", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refresh }),
        });
        if (refreshResponse.ok) {
          const tokens: AccessTokenResponse = await refreshResponse.json();
          setTokens(tokens.access_token, refresh);
          headers["Authorization"] = `Bearer ${tokens.access_token}`;
          response = await fetch(path, { ...options, headers });
        } else {
          clearTokens();
          window.location.href = "/login";
          throw new ApiError(401, null);
        }
      } catch {
        clearTokens();
        window.location.href = "/login";
        throw new ApiError(401, null);
      }
    }
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body);
  }

  return response.json();
}

export const api = {
  login: (data: LoginRequest) =>
    request<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  refresh: (refreshToken: string) =>
    request<AccessTokenResponse>("/api/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),

  logout: () =>
    request<MessageResponse>("/api/auth/logout", { method: "POST" }),

  me: () => request<User>("/api/auth/me"),

  listUsers: (params?: { page?: number; page_size?: number; q?: string; role?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.q) searchParams.set("q", params.q);
    if (params?.role) searchParams.set("role", params.role);
    const query = searchParams.toString();
    return request<UserListResponse>(`/api/users${query ? `?${query}` : ""}`);
  },

  createUser: (data: UserCreate) =>
    request<User>("/api/users", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getUser: (id: string) => request<User>(`/api/users/${id}`),

  updateUser: (id: string, data: UserUpdate) =>
    request<User>(`/api/users/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteUser: (id: string) =>
    request<void>(`/api/users/${id}`, { method: "DELETE" }),

  getProjectStats: () => request<ProjectStats>("/api/projects/stats"),

  listProjects: (params?: { page?: number; page_size?: number; q?: string; status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.q) searchParams.set("q", params.q);
    if (params?.status) searchParams.set("status", params.status);
    const query = searchParams.toString();
    return request<ProjectListResponse>(`/api/projects${query ? `?${query}` : ""}`);
  },

  getProject: (id: string) => request<Project>(`/api/projects/${id}`),

  createProject: (data: Partial<Project>) =>
    request<Project>("/api/projects", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateProject: (id: string, data: Partial<Project>) =>
    request<Project>(`/api/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  transitionProject: (id: string, status: ProjectStatus) =>
    request<Project>(`/api/projects/${id}/transition`, {
      method: "POST",
      body: JSON.stringify({ to_status: status }),
    }),

  listClients: (params?: { page?: number; page_size?: number; q?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.q) searchParams.set("q", params.q);
    const query = searchParams.toString();
    return request<ClientListResponse>(`/api/clients${query ? `?${query}` : ""}`);
  },

  getClient: (id: string) => request<Client>(`/api/clients/${id}`),

  createClient: (data: Partial<Client>) =>
    request<Client>("/api/clients", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateClient: (id: string, data: Partial<Client>) =>
    request<Client>(`/api/clients/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteContact: (clientId: string, contactId: string) =>
    request<void>(`/api/clients/${clientId}/contacts/${contactId}`, { method: "DELETE" }),

  addContact: (clientId: string, data: Partial<Contact>) =>
    request<Contact>(`/api/clients/${clientId}/contacts`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

export { ApiError };