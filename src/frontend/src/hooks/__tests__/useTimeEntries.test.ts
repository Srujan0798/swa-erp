import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { useTimeEntries, useCreateTimeEntry, useUpdateTimeEntry, useDeleteTimeEntry } from "../useTimeEntries";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listTimeEntries: vi.fn(),
    createTimeEntry: vi.fn(),
    updateTimeEntry: vi.fn(),
    deleteTimeEntry: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockTimeEntry = {
  id: "te-1",
  project_id: "proj-1",
  task_id: null,
  user_id: "user-1",
  description: "Design review",
  hours: 2.5,
  is_billable: true,
  entry_date: "2025-01-15",
  created_at: "2025-01-15T10:00:00Z",
  updated_at: "2025-01-15T10:00:00Z",
};

describe("useTimeEntries", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches time entries with filters", async () => {
    const response = { items: [mockTimeEntry], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listTimeEntries).mockResolvedValue(response);

    const { result } = renderHook(() => useTimeEntries({ project_id: "proj-1" }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listTimeEntries).toHaveBeenCalledWith({ project_id: "proj-1" });
  });

  it("fetches without filters", async () => {
    const response = { items: [mockTimeEntry], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listTimeEntries).mockResolvedValue(response);

    const { result } = renderHook(() => useTimeEntries(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.listTimeEntries).toHaveBeenCalledWith(undefined);
  });
});

describe("useCreateTimeEntry", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates time entry and invalidates list", async () => {
    vi.mocked(api.createTimeEntry).mockResolvedValue(mockTimeEntry);

    const { result } = renderHook(() => useCreateTimeEntry(), { wrapper: createWrapper() });

    result.current.mutate({
      project_id: "proj-1",
      description: "Design review",
      hours: 2.5,
      entry_date: "2025-01-15",
      is_billable: true,
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createTimeEntry).toHaveBeenCalledWith({
      project_id: "proj-1",
      description: "Design review",
      hours: 2.5,
      entry_date: "2025-01-15",
      is_billable: true,
    });
  });
});

describe("useUpdateTimeEntry", () => {
  beforeEach(() => vi.clearAllMocks());

  it("updates time entry by id", async () => {
    vi.mocked(api.updateTimeEntry).mockResolvedValue({ ...mockTimeEntry, hours: 3 });

    const { result } = renderHook(() => useUpdateTimeEntry(), { wrapper: createWrapper() });

    result.current.mutate({ id: "te-1", data: { hours: 3 } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateTimeEntry).toHaveBeenCalledWith("te-1", { hours: 3 });
  });
});

describe("useDeleteTimeEntry", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes time entry by id", async () => {
    vi.mocked(api.deleteTimeEntry).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteTimeEntry(), { wrapper: createWrapper() });

    result.current.mutate("te-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteTimeEntry).toHaveBeenCalledWith("te-1");
  });
});
