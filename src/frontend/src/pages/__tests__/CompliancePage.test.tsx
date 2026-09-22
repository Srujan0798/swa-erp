import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import React from "react";
import { CompliancePage } from "@/pages/CompliancePage";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: { listProjects: vi.fn(), listStandards: vi.fn() },
}));

vi.mock("@/components/compliance/ComplianceDashboard", () => ({
  ComplianceDashboard: () => <div data-testid="compliance-dashboard" />,
}));

vi.mock("@/components/compliance/ComplianceChecklist", () => ({
  ComplianceChecklist: () => <div data-testid="compliance-checklist" />,
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter>
      <CompliancePage />
    </MemoryRouter>,
    {
      wrapper: ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children),
    }
  );
}

describe("CompliancePage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and loads standards", async () => {
    vi.mocked(api.listProjects).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 100 });
    vi.mocked(api.listStandards).mockResolvedValue([
      { id: "s1", name: "NBC 2016", version: "2016", description: null },
    ]);
    renderPage();
    expect(screen.getByRole("heading", { name: /^compliance$/i })).toBeInTheDocument();
    await waitFor(() => expect(api.listStandards).toHaveBeenCalled());
  });

  it("shows error state when projects fail to load", async () => {
    vi.mocked(api.listProjects).mockRejectedValue(new Error("down"));
    vi.mocked(api.listStandards).mockResolvedValue([]);
    renderPage();
    expect(await screen.findByText(/failed to load projects/i)).toBeInTheDocument();
  });
});
