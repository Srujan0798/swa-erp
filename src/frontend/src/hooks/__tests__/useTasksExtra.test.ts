import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useTaskComments,
  useDeleteTask,
  useReorderTask,
  useBulkUpdateStatus,
  useAssignTask,
  useUnassignTask,
  useAddComment,
} from "../useTasks";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listComments: vi.fn(),
    deleteTask: vi.fn(),
    reorderTask: vi.fn(),
    bulkUpdateStatus: vi.fn(),
    assignTask: vi.fn(),
    unassignTask: vi.fn(),
    addComment: vi.fn(),
  },
}));

vi.mock("@/lib/queryKeys", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/queryKeys")>();
  return {
    ...actual,
    taskKeys: {
      all: ["tasks"],
      lists: () => ["tasks", "list"] as const,
      list: () => ["tasks", "list"] as const,
      details: () => ["tasks", "detail"] as const,
      detail: (taskId: string) => ["tasks", "detail", taskId] as const,
      myTasks: () => ["tasks", "my"] as const,
      stats: (projectId: string) => ["tasks", "stats", projectId] as const,
      comments: (taskId: string) => ["tasks", "comments", taskId] as const,
    },
  };
});

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockComment = {
  id: "comment-1",
  task_id: "task-1",
  user_id: "user-1",
  content: "This looks good",
  created_at: "2025-01-15T00:00:00Z",
  user_name: "Alice",
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

describe("useTaskComments", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches comments for a task", async () => {
    vi.mocked(api.listComments).mockResolvedValue([mockComment]);

    const { result } = renderHook(() => useTaskComments("task-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([mockComment]);
    expect(api.listComments).toHaveBeenCalledWith("task-1");
  });

  it("does not fetch when taskId is empty", () => {
    renderHook(() => useTaskComments(""), { wrapper: createWrapper() });
    expect(api.listComments).not.toHaveBeenCalled();
  });
});

describe("useDeleteTask", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes task by id and invalidates all", async () => {
    vi.mocked(api.deleteTask).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteTask(), { wrapper: createWrapper() });

    result.current.mutate("task-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteTask).toHaveBeenCalledWith("task-1", expect.anything());
  });
});

describe("useReorderTask", () => {
  beforeEach(() => vi.clearAllMocks());

  it("reorders task and invalidates lists", async () => {
    vi.mocked(api.reorderTask).mockResolvedValue(mockTask);

    const { result } = renderHook(() => useReorderTask(), { wrapper: createWrapper() });

    result.current.mutate({ taskId: "task-1", status: "todo", sortOrder: 5 });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.reorderTask).toHaveBeenCalledWith("task-1", "todo", 5);
  });
});

describe("useBulkUpdateStatus", () => {
  beforeEach(() => vi.clearAllMocks());

  it("bulk updates task statuses", async () => {
    const response = { message: "Updated 3 tasks" };
    vi.mocked(api.bulkUpdateStatus).mockResolvedValue(response);

    const { result } = renderHook(() => useBulkUpdateStatus(), { wrapper: createWrapper() });

    result.current.mutate({ task_ids: ["t1", "t2", "t3"], new_status: "done" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.bulkUpdateStatus).toHaveBeenCalledWith(
      { task_ids: ["t1", "t2", "t3"], new_status: "done" },
      expect.anything()
    );
  });
});

describe("useAssignTask", () => {
  beforeEach(() => vi.clearAllMocks());

  it("assigns task and invalidates caches", async () => {
    vi.mocked(api.assignTask).mockResolvedValue(mockTask);

    const { result } = renderHook(() => useAssignTask(), { wrapper: createWrapper() });

    result.current.mutate({ taskId: "task-1", assigneeId: "user-2" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.assignTask).toHaveBeenCalledWith("task-1", "user-2");
  });
});

describe("useUnassignTask", () => {
  beforeEach(() => vi.clearAllMocks());

  it("unassigns task and invalidates caches", async () => {
    vi.mocked(api.unassignTask).mockResolvedValue(mockTask);

    const { result } = renderHook(() => useUnassignTask(), { wrapper: createWrapper() });

    result.current.mutate("task-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.unassignTask).toHaveBeenCalledWith("task-1", expect.anything());
  });
});

describe("useAddComment", () => {
  beforeEach(() => vi.clearAllMocks());

  it("adds comment to task", async () => {
    vi.mocked(api.addComment).mockResolvedValue(mockComment);

    const { result } = renderHook(() => useAddComment(), { wrapper: createWrapper() });

    result.current.mutate({ taskId: "task-1", content: "Looks good" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.addComment).toHaveBeenCalledWith("task-1", "Looks good");
  });
});
