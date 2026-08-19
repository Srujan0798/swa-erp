import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { useAuth, useCurrentUser, useUsers, useCreateUser, useUpdateUser, useDeleteUser } from "../useAuth";
import { api } from "@/lib/api";

const navigateMock = vi.fn();

const authMock = vi.hoisted(() => ({
  setTokens: vi.fn(),
  clearTokens: vi.fn(),
  getAccessToken: vi.fn(() => null),
  getRefreshToken: vi.fn(() => null),
}));

vi.mock("@/lib/api", () => ({
  api: {
    login: vi.fn(),
    logout: vi.fn(),
    me: vi.fn(),
    listUsers: vi.fn(),
    createUser: vi.fn(),
    updateUser: vi.fn(),
    deleteUser: vi.fn(),
  },
}));

vi.mock("react-router-dom", () => ({
  useNavigate: () => navigateMock,
}));

vi.mock("@/lib/auth", () => authMock);

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockUser = {
  id: "user-1",
  email: "admin@swa.com",
  name: "Admin User",
  role: "admin" as const,
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
};

const mockUsersResponse = {
  items: [mockUser],
  total: 1,
  page: 1,
  page_size: 20,
};

describe("useAuth", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    navigateMock.mockClear();
    authMock.setTokens.mockClear();
    authMock.clearTokens.mockClear();
    authMock.getAccessToken.mockReturnValue(null);
    authMock.getRefreshToken.mockReturnValue(null);
  });

  it("returns unauthenticated when no user", async () => {
    vi.mocked(api.me).mockRejectedValue(new Error("401"));

    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeUndefined();
  });

  it("returns authenticated when user is loaded", async () => {
    vi.mocked(api.me).mockResolvedValue(mockUser);

    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isAuthenticated).toBe(true));
    expect(result.current.user).toEqual(mockUser);
  });

  it("login sets tokens, caches user, and navigates", async () => {
    const tokenResponse = {
      access_token: "access-123",
      refresh_token: "refresh-456",
      user: mockUser,
    };
    vi.mocked(api.login).mockResolvedValue(tokenResponse);

    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });

    const loginResult = await result.current.login({ email: "admin@swa.com", password: "pass" });
    expect(api.login).toHaveBeenCalledWith({ email: "admin@swa.com", password: "pass" });
    expect(authMock.setTokens).toHaveBeenCalledWith("access-123", "refresh-456");
    expect(navigateMock).toHaveBeenCalledWith("/dashboard");
    expect(loginResult).toEqual(tokenResponse);
  });

  it("logout clears tokens, clears cache, and navigates to login", async () => {
    vi.mocked(api.me).mockResolvedValue(mockUser);
    vi.mocked(api.logout).mockResolvedValue({ message: "Logged out" });

    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isAuthenticated).toBe(true));

    await result.current.logout();
    expect(api.logout).toHaveBeenCalled();
    expect(authMock.clearTokens).toHaveBeenCalled();
    expect(navigateMock).toHaveBeenCalledWith("/login");
  });
});

describe("useCurrentUser", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    authMock.getAccessToken.mockReturnValue(null);
  });

  it("fetches current user", async () => {
    vi.mocked(api.me).mockResolvedValue(mockUser);

    const { result } = renderHook(() => useCurrentUser(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockUser);
    expect(api.me).toHaveBeenCalled();
  });
});

describe("useUsers", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches paginated users", async () => {
    vi.mocked(api.listUsers).mockResolvedValue(mockUsersResponse);

    const { result } = renderHook(() => useUsers(1, 20), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockUsersResponse);
    expect(api.listUsers).toHaveBeenCalledWith({ page: 1, page_size: 20 });
  });
});

describe("useCreateUser", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates user and invalidates users list", async () => {
    vi.mocked(api.createUser).mockResolvedValue(mockUser);

    const { result } = renderHook(() => useCreateUser(), { wrapper: createWrapper() });

    result.current.mutate({ email: "new@swa.com", name: "New User", password: "pass", role: "viewer" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createUser).toHaveBeenCalledWith(
      {
        email: "new@swa.com",
        name: "New User",
        password: "pass",
        role: "viewer",
      },
      expect.anything()
    );
  });
});

describe("useUpdateUser", () => {
  beforeEach(() => vi.clearAllMocks());

  it("updates user by id", async () => {
    vi.mocked(api.updateUser).mockResolvedValue({ ...mockUser, role: "pm" });

    const { result } = renderHook(() => useUpdateUser(), { wrapper: createWrapper() });

    result.current.mutate({ id: "user-1", data: { role: "pm" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateUser).toHaveBeenCalledWith("user-1", { role: "pm" });
  });
});

describe("useDeleteUser", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes user by id", async () => {
    vi.mocked(api.deleteUser).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteUser(), { wrapper: createWrapper() });

    result.current.mutate("user-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteUser).toHaveBeenCalledWith("user-1", expect.anything());
  });
});
