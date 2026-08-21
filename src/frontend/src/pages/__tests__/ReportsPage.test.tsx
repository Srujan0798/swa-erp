/* eslint-disable @typescript-eslint/no-explicit-any */import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { api } from "@/lib/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());
const useProjectPnLMock = vi.hoisted(() => vi.fn());
const useProjectCostsMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/hooks/useProjectPnL", () => ({
  useProjectPnL: (id: string) => useProjectPnLMock(id),
  useProjectCosts: (id: string, cat?: string) => useProjectCostsMock(id, cat),
}));

vi.mock("@/lib/api", () => ({
  api: {
    listProjects: vi.fn(),
  },
}));

vi.mock("@/components/financials/PnlDashboard", () => ({
  PnlDashboard: ({ isLoading }: any) => (
    <div data-testid="pnl-dashboard">
      <span>PnL loaded: {String(!isLoading)}</span>
    </div>
  ),
}));

vi.mock("@/components/financials/CostEntryForm", () => ({
  CostEntryForm: (_props: any) => (
    <div data-testid="cost-entry-form">CostForm</div>
  ),
}));

const project = { id: "p1", code: "PRJ-001", name: "Test Project" };

async function renderPage(initialEntries: string[] = ["/"]) {
  const { ReportsPage } = await import("@/pages/ReportsPage");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <QueryClientProvider client={queryClient}>
        <ReportsPage />
      </QueryClientProvider>
    </MemoryRouter>
  );
}

describe("ReportsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    vi.mocked(api.listProjects).mockResolvedValue({ items: [project], total: 1 } as never);
    useProjectPnLMock.mockReturnValue({
      data: null,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    useProjectCostsMock.mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
  });

  it("renders header", async () => {
    await renderPage();
    expect(screen.getByText("Reports")).toBeInTheDocument();
    expect(screen.getByText(/Project profitability/)).toBeInTheDocument();
  });

  it("shows select project message", async () => {
    await renderPage();
    expect(screen.getByText(/Select a project to view/)).toBeInTheDocument();
  });

  it("shows tabs when project selected", async () => {
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText("P&L")).toBeInTheDocument();
    expect(screen.getByText("Costs")).toBeInTheDocument();
  });

  it("shows PnL dashboard", async () => {
    await renderPage(["/?project=p1"]);
    expect(await screen.findByTestId("pnl-dashboard")).toBeInTheDocument();
  });

  it("shows error banner on projects load failure", async () => {
    vi.mocked(api.listProjects).mockRejectedValue(new Error("boom"));
    await renderPage();
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });

  it("shows Add cost button for commercial users", async () => {
    await renderPage(["/?project=p1"]);
    const costsTab = await screen.findByRole("tab", { name: /Costs/i });
    await userEvent.click(costsTab);
    expect(await screen.findByText("Add cost")).toBeInTheDocument();
  });

  it("hides Add cost for viewer users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    await renderPage(["/?project=p1"]);
    const costsTab = await screen.findByRole("tab", { name: /Costs/i });
    await userEvent.click(costsTab);
    expect(screen.queryByText("Add cost")).not.toBeInTheDocument();
  });

  it("shows category filter input in costs tab", async () => {
    await renderPage(["/?project=p1"]);
    const costsTab = await screen.findByRole("tab", { name: /Costs/i });
    await userEvent.click(costsTab);
    expect(screen.getByPlaceholderText("Filter category")).toBeInTheDocument();
  });

  it("shows costs tab empty state", async () => {
    await renderPage(["/?project=p1"]);
    const costsTab = await screen.findByRole("tab", { name: /Costs/i });
    await userEvent.click(costsTab);
    expect(screen.getByText(/No costs found/)).toBeInTheDocument();
  });

  it("shows loading costs", async () => {
    useProjectCostsMock.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    await renderPage(["/?project=p1"]);
    const costsTab = await screen.findByRole("tab", { name: /Costs/i });
    await userEvent.click(costsTab);
    expect(screen.getByText(/Loading costs/)).toBeInTheDocument();
  });

  it("syncs project from search params", async () => {
    await renderPage(["/?project=p1"]);
    expect(await screen.findByTestId("pnl-dashboard")).toBeInTheDocument();
  });
});
