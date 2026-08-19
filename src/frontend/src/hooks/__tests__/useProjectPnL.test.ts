import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useProjectPnL,
  useProjectCosts,
  useAddProjectCost,
  useDeleteProjectCost,
} from "../useProjectPnL";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    getProjectPnL: vi.fn(),
    listProjectCosts: vi.fn(),
    addProjectCost: vi.fn(),
    deleteProjectCost: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockPnL = {
  revenue: 5000000,
  costs: 3000000,
  profit: 2000000,
  margin: 40,
  breakdown: {
    materials: 1000000,
    labor: 1500000,
    other: 500000,
  },
};

const mockCost = {
  id: "cost-1",
  project_id: "proj-1",
  category: "Materials",
  description: "Steel purchase",
  amount: 100000,
  incurred_at: "2025-01-15",
  created_at: "2025-01-15T00:00:00Z",
  updated_at: "2025-01-15T00:00:00Z",
};

const mockCostListResponse = { items: [mockCost], total: 1, page: 1, page_size: 20 };

describe("useProjectPnL", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches project PnL by id", async () => {
    vi.mocked(api.getProjectPnL).mockResolvedValue(mockPnL);

    const { result } = renderHook(() => useProjectPnL("proj-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockPnL);
    expect(api.getProjectPnL).toHaveBeenCalledWith("proj-1");
  });

  it("does not fetch when projectId is empty", () => {
    renderHook(() => useProjectPnL(""), { wrapper: createWrapper() });
    expect(api.getProjectPnL).not.toHaveBeenCalled();
  });
});

describe("useProjectCosts", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches costs for project with category", async () => {
    vi.mocked(api.listProjectCosts).mockResolvedValue(mockCostListResponse);

    const { result } = renderHook(() => useProjectCosts("proj-1", "Materials"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.listProjectCosts).toHaveBeenCalledWith("proj-1", { category: "Materials" });
  });

  it("does not fetch when projectId is empty", () => {
    renderHook(() => useProjectCosts("", undefined), { wrapper: createWrapper() });
    expect(api.listProjectCosts).not.toHaveBeenCalled();
  });
});

describe("useAddProjectCost", () => {
  beforeEach(() => vi.clearAllMocks());

  it("adds project cost and invalidates cache", async () => {
    vi.mocked(api.addProjectCost).mockResolvedValue(mockCost);

    const { result } = renderHook(() => useAddProjectCost(), { wrapper: createWrapper() });

    result.current.mutate({
      projectId: "proj-1",
      data: { category: "Materials", description: "Steel", amount: 100000, incurred_at: "2025-01-15" },
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.addProjectCost).toHaveBeenCalledWith("proj-1", {
      category: "Materials",
      description: "Steel",
      amount: 100000,
      incurred_at: "2025-01-15",
    });
  });
});

describe("useDeleteProjectCost", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes project cost", async () => {
    vi.mocked(api.deleteProjectCost).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteProjectCost(), { wrapper: createWrapper() });

    result.current.mutate({ projectId: "proj-1", costId: "cost-1" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteProjectCost).toHaveBeenCalledWith("proj-1", "cost-1");
  });
});
