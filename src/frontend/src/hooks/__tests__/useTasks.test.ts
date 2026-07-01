import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { useTasks, useTask, useCreateTask, useUpdateTask, useTransitionTask, useMyTasks, useProjectTaskStats } from "../useTasks";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listTasks: vi.fn(),
    getTask: vi.fn(),
    createTask: vi.fn(),
    updateTask: vi.fn(),
    transitionTask: vi.fn(),
    getMyTasks: vi.fn(),
    getProjectTaskStats: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockTask = {
  id: "task-1",
  project_id: "proj-1",
  title: "Test Task",
  description: null,
  status: "todo" as const,
  priority: "medium" as const,
  assignee_id: null,
  due_date: null,
  sort_order: 0,
  created_by: "user-1",
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
  assignee_name: null,
  created_by_name: "Admin",
  comment_count: 0,
};

describe("useTasks", () => {
  beforeEach(() => vi.clearAllMocks());

  it("returns task list", async () => {
    const response = { items: [mockTask], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listTasks).mockResolvedValue(response);

    const { result } = renderHook(() => useTasks("proj-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listTasks).toHaveBeenCalledWith("proj-1", undefined);
  });
});

describe("useTask", () => {
  beforeEach(() => vi.clearAllMocks());

  it("returns single task", async () => {
    vi.mocked(api.getTask).mockResolvedValue(mockTask);

    const { result } = renderHook(() => useTask("task-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockTask);
  });
});

describe("useCreateTask", () => {
  beforeEach(() => vi.clearAllMocks());

  it("calls POST with correct body", async () => {
    vi.mocked(api.createTask).mockResolvedValue(mockTask);

    const { result } = renderHook(() => useCreateTask("proj-1"), { wrapper: createWrapper() });

    result.current.mutate({ title: "New Task" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createTask).toHaveBeenCalledWith("proj-1", { title: "New Task" });
  });
});

describe("useUpdateTask", () => {
  beforeEach(() => vi.clearAllMocks());

  it("calls PATCH with correct endpoint", async () => {
    vi.mocked(api.updateTask).mockResolvedValue(mockTask);

    const { result } = renderHook(() => useUpdateTask(), { wrapper: createWrapper() });

    result.current.mutate({ taskId: "task-1", data: { title: "Updated" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateTask).toHaveBeenCalledWith("task-1", { title: "Updated" });
  });
});

describe("useTransitionTask", () => {
  beforeEach(() => vi.clearAllMocks());

  it("calls POST /transition with correct body", async () => {
    const transitioned = { ...mockTask, status: "in_progress" as const };
    vi.mocked(api.transitionTask).mockResolvedValue(transitioned);

    const { result } = renderHook(() => useTransitionTask(), { wrapper: createWrapper() });

    result.current.mutate({ taskId: "task-1", toStatus: "in_progress" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.transitionTask).toHaveBeenCalledWith("task-1", "in_progress");
  });
});

describe("useMyTasks", () => {
  beforeEach(() => vi.clearAllMocks());

  it("calls correct endpoint", async () => {
    const response = { items: [mockTask], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.getMyTasks).mockResolvedValue(response);

    const { result } = renderHook(() => useMyTasks(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.getMyTasks).toHaveBeenCalled();
  });
});

describe("useProjectTaskStats", () => {
  beforeEach(() => vi.clearAllMocks());

  it("calls correct endpoint", async () => {
    const stats = { todo: 2, in_progress: 1, done: 3, total: 6 };
    vi.mocked(api.getProjectTaskStats).mockResolvedValue(stats);

    const { result } = renderHook(() => useProjectTaskStats("proj-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.getProjectTaskStats).toHaveBeenCalledWith("proj-1");
    expect(result.current.data).toEqual(stats);
  });
});
