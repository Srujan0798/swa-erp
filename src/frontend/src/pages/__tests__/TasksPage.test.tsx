import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import React from "react";
import { api } from "@/lib/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());
const useToastMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/hooks/useToast", () => ({
  useToast: () => useToastMock(),
}));

vi.mock("@/lib/api", () => ({
  api: {
    listProjects: vi.fn(),
    listAssignees: vi.fn(),
    listTasks: vi.fn(),
    getMyTasks: vi.fn(),
    createTask: vi.fn(),
    deleteTask: vi.fn(),
    transitionTask: vi.fn(),
  },
}));

vi.mock("@/components/tasks/KanbanBoard", () => ({
  KanbanBoard: ({ tasks, isLoading, onTaskClick, onStatusChange }: any) => (
    <div data-testid="kanban-board">
      <span data-testid="kanban-loading">{String(isLoading)}</span>
      <span data-testid="kanban-count">{tasks.length}</span>
      {tasks.map((t: any) => (
        <button key={t.id} data-testid={`task-${t.id}`} onClick={() => onTaskClick?.(t)}>
          {t.title}
        </button>
      ))}
      {onStatusChange && (
        <button data-testid="transition-btn" onClick={() => onStatusChange("t1", "in_progress")}>
          Transition
        </button>
      )}
    </div>
  ),
}));

vi.mock("@/components/tasks/TaskDetail", () => ({
  TaskDetail: ({ task, onClose }: any) => (
    <div data-testid="task-detail">
      <span data-testid="detail-title">{task?.title}</span>
      <button onClick={onClose}>Close Detail</button>
    </div>
  ),
}));

const project = { id: "p1", code: "PRJ-001", name: "Test Project" };
const assignee = { id: "u1", name: "Alice Smith", role: "pm" };
const task = {
  id: "t1",
  title: "Design review",
  status: "todo",
  priority: "high",
  assignee_name: "Alice",
  due_date: "2026-12-31",
  description: "Review designs",
  comment_count: 3,
  sort_order: 0,
  project_id: "p1",
};
const myTask = {
  id: "mt1",
  title: "My task",
  status: "todo",
  priority: "medium",
  assignee_name: "Bob",
  due_date: null,
  description: "",
  comment_count: 0,
  sort_order: 0,
  project_id: "p1",
};

async function renderPage(initialEntries: string[] = ["/"]) {
  const { TasksPage } = await import("@/pages/TasksPage");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <QueryClientProvider client={queryClient}>
        <TasksPage />
      </QueryClientProvider>
    </MemoryRouter>
  );
}

describe("TasksPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    useToastMock.mockReturnValue({ toast: vi.fn() });
    vi.mocked(api.listProjects).mockResolvedValue({ items: [project], total: 1 } as never);
    vi.mocked(api.listAssignees).mockResolvedValue({ items: [assignee], total: 1 } as never);
    vi.mocked(api.listTasks).mockResolvedValue({ items: [], total: 0 } as never);
    vi.mocked(api.getMyTasks).mockResolvedValue({ items: [], total: 0 } as never);
  });

  it("renders header and tabs", async () => {
    await renderPage();
    expect(screen.getByText("Tasks")).toBeInTheDocument();
    expect(screen.getByText("Board")).toBeInTheDocument();
    expect(screen.getByText("My Tasks")).toBeInTheDocument();
    expect(screen.getByText("Activity")).toBeInTheDocument();
  });

  it("shows placeholder when no project selected", async () => {
    await renderPage();
    expect(screen.getByText(/Select a project to load the board/)).toBeInTheDocument();
  });

  it("shows New Task button for write users", async () => {
    await renderPage();
    expect(screen.getByText("New Task")).toBeInTheDocument();
  });

  it("hides New Task for viewer users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    await renderPage();
    expect(screen.queryByText("New Task")).not.toBeInTheDocument();
  });

  it("shows empty board message when no tasks", async () => {
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText(/No tasks on this project yet/)).toBeInTheDocument();
  });

  it("loads and displays tasks on board", async () => {
    vi.mocked(api.listTasks).mockResolvedValue({ items: [task], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByTestId("kanban-board")).toBeInTheDocument();
    expect(screen.getByTestId("task-t1")).toHaveTextContent("Design review");
  });

  it("opens task detail dialog", async () => {
    vi.mocked(api.listTasks).mockResolvedValue({ items: [task], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    await screen.findByTestId("task-t1");
    await userEvent.click(screen.getByTestId("task-t1"));
    expect(screen.getByTestId("task-detail")).toBeInTheDocument();
    expect(screen.getByTestId("detail-title")).toHaveTextContent("Design review");
  });

  it("closes task detail dialog", async () => {
    vi.mocked(api.listTasks).mockResolvedValue({ items: [task], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    await screen.findByTestId("task-t1");
    await userEvent.click(screen.getByTestId("task-t1"));
    await userEvent.click(screen.getByText("Close Detail"));
    expect(screen.queryByTestId("task-detail")).not.toBeInTheDocument();
  });

  it("opens Create Task dialog", async () => {
    await renderPage();
    await userEvent.click(screen.getByText("New Task"));
    expect(await screen.findByText("Create Task")).toBeInTheDocument();
    expect(screen.getByText("Title")).toBeInTheDocument();
    expect(screen.getByText("Description")).toBeInTheDocument();
    expect(screen.getByText("Priority")).toBeInTheDocument();
  });

  it("shows task search filtering", async () => {
    vi.mocked(api.listTasks).mockResolvedValue({ items: [task], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    await screen.findByTestId("task-t1");
    const searchInput = screen.getByPlaceholderText("Search tasks...");
    await userEvent.type(searchInput, "nonexistent");
    expect(screen.getByTestId("kanban-count")).toHaveTextContent("0");
  });

  it("shows my tasks tab", async () => {
    vi.mocked(api.getMyTasks).mockResolvedValue({ items: [myTask], total: 1 } as never);
    await renderPage();
    await userEvent.click(screen.getByText("My Tasks"));
    expect(await screen.findByText("My task")).toBeInTheDocument();
  });

  it("shows activity tab content", async () => {
    await renderPage();
    await userEvent.click(screen.getByText("Activity"));
    expect(screen.getByText(/Task comments and assignment activity/)).toBeInTheDocument();
  });

  it("shows no tasks match search message", async () => {
    vi.mocked(api.listTasks).mockResolvedValue({ items: [task], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    await screen.findByTestId("task-t1");
    const searchInput = screen.getByPlaceholderText("Search tasks...");
    await userEvent.type(searchInput, "xyz");
    expect(screen.getByText("No tasks match your search.")).toBeInTheDocument();
  });

  it("can trigger status transition", async () => {
    vi.mocked(api.listTasks).mockResolvedValue({ items: [task], total: 1 } as never);
    vi.mocked(api.transitionTask).mockResolvedValue(undefined as never);
    await renderPage(["/?project=p1"]);
    await screen.findByTestId("transition-btn");
    await userEvent.click(screen.getByTestId("transition-btn"));
    expect(api.transitionTask).toHaveBeenCalledWith("t1", "in_progress");
  });

  it("opens create dialog from board empty state", async () => {
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText(/No tasks on this project yet/)).toBeInTheDocument();
    await userEvent.click(screen.getByText("Create the first task"));
    expect(await screen.findByText("Create Task")).toBeInTheDocument();
  });

  it("reads project from search params", async () => {
    vi.mocked(api.listTasks).mockResolvedValue({ items: [task], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByTestId("task-t1")).toBeInTheDocument();
  });
});
