import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import React from "react";
import { SustainabilityPage } from "@/pages/SustainabilityPage";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: { listProjects: vi.fn(), listSustainabilityMetrics: vi.fn() },
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter>
      <SustainabilityPage />
    </MemoryRouter>,
    {
      wrapper: ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children),
    }
  );
}

const projects = {
  items: [
    {
      id: "p1",
      client_id: "c1",
      code: "PRJ-001",
      name: "Acme Office",
      description: null,
      status: "Execution" as const,
      pm_id: null,
      designer_id: null,
      auditor_id: null,
      location: null,
      estimated_value: null,
      actual_value: null,
      start_date: null,
      target_end_date: null,
      actual_end_date: null,
      is_active: true,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
      client_name: "Acme Corp",
      pm_name: null,
      designer_name: null,
      auditor_name: null,
    },
  ],
  total: 1,
  page: 1,
  page_size: 200,
};

describe("SustainabilityPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading state when no projects yet", () => {
    vi.mocked(api.listProjects).mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading projects/i)).toBeInTheDocument();
  });

  it("renders heading once projects load", async () => {
    vi.mocked(api.listProjects).mockResolvedValue(projects);
    renderPage();
    expect(
      await screen.findByRole("heading", { name: /sustainability metrics/i })
    ).toBeInTheDocument();
    await waitFor(() => expect(api.listProjects).toHaveBeenCalled());
  });
});
