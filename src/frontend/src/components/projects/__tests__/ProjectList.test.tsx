import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { MemoryRouter } from "react-router-dom";
import { ProjectList } from "../ProjectList";
import { api } from "@/lib/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/lib/api", () => ({
  api: { listProjects: vi.fn() },
}));

function createWrapper() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

const project = {
  id: "p1",
  code: "PRJ-001",
  name: "Acme Office",
  client_name: "Acme Corp",
  status: "Execution",
  pm_name: "Bob",
  location: "Mumbai",
};

describe("ProjectList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
  });

  it("renders projects in a table", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    vi.mocked(api.listProjects).mockResolvedValue({ items: [project], total: 1 } as never);
    render(
      <MemoryRouter>
        <ProjectList />
      </MemoryRouter>,
      { wrapper: createWrapper() }
    );

    expect(await screen.findByText("PRJ-001")).toBeInTheDocument();
    expect(screen.getByText("Acme Office")).toBeInTheDocument();
    expect(screen.getByText("Acme Corp")).toBeInTheDocument();
    expect(screen.getByText("Execution")).toBeInTheDocument();
    expect(screen.getByText("1 project")).toBeInTheDocument();
  });

  it("shows the New Project button for users with manage permission", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "admin" } });
    vi.mocked(api.listProjects).mockResolvedValue({ items: [], total: 0 } as never);
    render(
      <MemoryRouter>
        <ProjectList />
      </MemoryRouter>,
      { wrapper: createWrapper() }
    );

    expect(await screen.findByRole("link", { name: /new project/i })).toBeInTheDocument();
  });

  it("hides New Project for viewers", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    vi.mocked(api.listProjects).mockResolvedValue({ items: [], total: 0 } as never);
    render(
      <MemoryRouter>
        <ProjectList />
      </MemoryRouter>,
      { wrapper: createWrapper() }
    );

    await screen.findByText(/No projects yet/);
    expect(screen.queryByRole("link", { name: /new project/i })).not.toBeInTheDocument();
  });

  it("shows error banner and retries", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    vi.mocked(api.listProjects).mockRejectedValue(new Error("boom"));
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ProjectList />
      </MemoryRouter>,
      { wrapper: createWrapper() }
    );

    expect(await screen.findByRole("alert")).toHaveTextContent("Failed to load projects");
    vi.mocked(api.listProjects).mockResolvedValue({ items: [project], total: 1 } as never);
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(await screen.findByText("PRJ-001")).toBeInTheDocument();
  });
});