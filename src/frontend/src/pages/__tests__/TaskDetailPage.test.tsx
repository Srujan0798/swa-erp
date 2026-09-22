import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import React from "react";
import { TaskDetailPage } from "@/pages/TaskDetailPage";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: { getTask: vi.fn() },
}));

vi.mock("@/components/tasks/TaskDetail", () => ({
  TaskDetail: ({ task }: { task: { title: string } }) => (
    <div data-testid="task-detail">{task.title}</div>
  ),
}));

function renderPage(taskId = "t1") {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter initialEntries={[`/tasks/${taskId}`]}>
      <Routes>
        <Route path="/tasks/:id" element={<TaskDetailPage />} />
      </Routes>
    </MemoryRouter>,
    {
      wrapper: ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children),
    }
  );
}

const task = {
  id: "t1",
  project_id: "p1",
  title: "Design review",
  description: null,
  status: "todo" as const,
  priority: "medium" as const,
  assignee_id: null,
  reporter_id: "u1",
  due_date: null,
  sort_order: 0,
  created_by: "u1",
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
  assignee_name: null,
  created_by_name: "PM",
  comment_count: 0,
};

describe("TaskDetailPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders task detail once loaded", async () => {
    vi.mocked(api.getTask).mockResolvedValue(task);
    renderPage();
    expect(await screen.findByTestId("task-detail")).toHaveTextContent("Design review");
    await waitFor(() => expect(api.getTask).toHaveBeenCalledWith("t1"));
  });

  it("shows error state when load fails", async () => {
    vi.mocked(api.getTask).mockRejectedValue(new Error("gone"));
    renderPage();
    expect(await screen.findByText("gone")).toBeInTheDocument();
  });
});
