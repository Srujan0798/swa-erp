import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { useTokens, useToken, useCreateToken, useUpdateToken, useDeleteToken } from "../useTokens";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listTokens: vi.fn(),
    getToken: vi.fn(),
    createToken: vi.fn(),
    updateToken: vi.fn(),
    deleteToken: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockToken = {
  id: "tok-1",
  reference_id: "SWA-2025-TOK-001",
  agreement_id: "agr-1",
  token_date: "2025-01-15",
  token_type: "Design",
  description: "Architectural drawings",
  token_status: "In Progress",
  tokens_used: 5,
  swa_employee_id: null,
  project_owner_id: null,
  client_employee_name: "John Doe",
  project_id: "proj-1",
  created_at: "2025-01-15T00:00:00Z",
  updated_at: "2025-01-15T00:00:00Z",
};

describe("useTokens", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches paginated tokens", async () => {
    const response = { items: [mockToken], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listTokens).mockResolvedValue(response);

    const { result } = renderHook(() => useTokens({ page: 1, page_size: 20 }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listTokens).toHaveBeenCalledWith({ page: 1, page_size: 20 });
  });
});

describe("useToken", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single token by id", async () => {
    vi.mocked(api.getToken).mockResolvedValue(mockToken);

    const { result } = renderHook(() => useToken("tok-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockToken);
    expect(api.getToken).toHaveBeenCalledWith("tok-1");
  });

  it("does not fetch when id is undefined", () => {
    renderHook(() => useToken(undefined), { wrapper: createWrapper() });
    expect(api.getToken).not.toHaveBeenCalled();
  });
});

describe("useCreateToken", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates token and invalidates lists", async () => {
    vi.mocked(api.createToken).mockResolvedValue(mockToken);

    const { result } = renderHook(() => useCreateToken(), { wrapper: createWrapper() });

    result.current.mutate({ agreement_id: "agr-1", token_date: "2025-01-15" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createToken).toHaveBeenCalledWith({ agreement_id: "agr-1", token_date: "2025-01-15" });
  });
});

describe("useUpdateToken", () => {
  beforeEach(() => vi.clearAllMocks());

  it("updates token by id", async () => {
    vi.mocked(api.updateToken).mockResolvedValue({ ...mockToken, tokens_used: 10 });

    const { result } = renderHook(() => useUpdateToken(), { wrapper: createWrapper() });

    result.current.mutate({ id: "tok-1", data: { tokens_used: 10 } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateToken).toHaveBeenCalledWith("tok-1", { tokens_used: 10 });
  });
});

describe("useDeleteToken", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes token by id", async () => {
    vi.mocked(api.deleteToken).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteToken(), { wrapper: createWrapper() });

    result.current.mutate("tok-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteToken).toHaveBeenCalledWith("tok-1");
  });
});
