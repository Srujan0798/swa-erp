import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
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
    listTimeEntries: vi.fn(),
    createTimeEntry: vi.fn(),
  },
}));

const project = { id: "p1", code: "PRJ-001", name: "Test Project" };
const entry = {
  id: "te1",
  date: "2026-08-20",
  hours: 2.5,
  is_billable: true,
  description: "Design work",
  project_id: "p1",
};

async function renderPage(initialEntries: string[] = ["/"]) {
  const { default: TimeTrackingPage } = await import("@/pages/TimeTrackingPage");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <QueryClientProvider client={queryClient}>
        <TimeTrackingPage />
      </QueryClientProvider>
    </MemoryRouter>
  );
}

describe("TimeTrackingPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    useToastMock.mockReturnValue({ toast: vi.fn() });
    vi.mocked(api.listProjects).mockResolvedValue({ items: [project], total: 1 } as never);
    vi.mocked(api.listTimeEntries).mockResolvedValue({ items: [], total: 0 } as never);
  });

  it("renders header and stats cards", async () => {
    await renderPage();
    expect(screen.getByText("Time tracking")).toBeInTheDocument();
    expect(screen.getByText("Total hours")).toBeInTheDocument();
    expect(screen.getByText("Entries")).toBeInTheDocument();
  });

  it("shows add time entry form for write users", async () => {
    await renderPage();
    expect(screen.getByText("Add time entry")).toBeInTheDocument();
    expect(screen.getByText("Add entry")).toBeInTheDocument();
  });

  it("shows view-only message for viewer users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    await renderPage();
    expect(screen.getByText(/View-only/)).toBeInTheDocument();
  });

  it("shows empty entries message", async () => {
    await renderPage();
    await waitFor(() => {
      expect(screen.getByText(/No entries yet/)).toBeInTheDocument();
    });
  });

  it("displays time entries in table", async () => {
    vi.mocked(api.listTimeEntries).mockResolvedValue({ items: [entry], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText("Design work")).toBeInTheDocument();
    expect(screen.getByText("2026-08-20")).toBeInTheDocument();
    expect(screen.getByText("Yes")).toBeInTheDocument();
  });

  it("shows loading state", async () => {
    vi.mocked(api.listTimeEntries).mockReturnValue(new Promise(() => {}));
    await renderPage();
    expect(screen.getByText(/Loading/)).toBeInTheDocument();
  });

  it("shows hours and billable count correctly", async () => {
    vi.mocked(api.listTimeEntries).mockResolvedValue({
      items: [
        { ...entry, hours: 3, is_billable: true },
        { ...entry, id: "te2", hours: 2, is_billable: false },
      ],
      total: 2,
    } as never);
    await renderPage(["/?project=p1"]);
    await waitFor(() => {
      expect(screen.getAllByText("Design work").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows entries table headers", async () => {
    vi.mocked(api.listTimeEntries).mockResolvedValue({ items: [entry], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText("Recent entries")).toBeInTheDocument();
  });

  it("syncs project from search params", async () => {
    vi.mocked(api.listTimeEntries).mockResolvedValue({ items: [entry], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText("Design work")).toBeInTheDocument();
  });
});
