import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import React from "react";
import { DocumentsPage } from "@/pages/DocumentsPage";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: { listProjects: vi.fn() },
}));

vi.mock("@/components/documents/FileBrowser", () => ({
  FileBrowser: ({ projectId }: { projectId: string }) => (
    <div data-testid="file-browser">{projectId}</div>
  ),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter>
      <DocumentsPage />
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
  page_size: 100,
};

describe("DocumentsPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and project picker", async () => {
    vi.mocked(api.listProjects).mockResolvedValue(projects);
    renderPage();
    expect(screen.getByRole("heading", { name: /file documents/i })).toBeInTheDocument();
    await waitFor(() => expect(api.listProjects).toHaveBeenCalled());
    expect(await screen.findByRole("option", { name: /acme office/i })).toBeInTheDocument();
  });

  it("shows error banner when projects fail to load", async () => {
    vi.mocked(api.listProjects).mockRejectedValue(new Error("down"));
    renderPage();
    expect(await screen.findByText(/failed to load projects/i)).toBeInTheDocument();
  });
});
