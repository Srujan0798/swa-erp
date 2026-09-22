import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { api } from "@/lib/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/lib/api", () => ({
  api: {
    listProjects: vi.fn(),
    listVendors: vi.fn(),
    listProjectRfqs: vi.fn(),
    getRfq: vi.fn(),
    sendRfq: vi.fn(),
    awardRfq: vi.fn(),
    createRfq: vi.fn(),
    respondRfq: vi.fn(),
    listMaterials: vi.fn(),
  },
}));

const project = { id: "p1", code: "PRJ-001", name: "Test Project" };
const vendor = { id: "v1", name: "Acme Vendor" };
const rfq = {
  id: "rfq1",
  rfq_number: "RFQ-001",
  vendor_name: "Acme Vendor",
  status: "draft",
  created_at: "2026-01-15T00:00:00Z",
  notes: "Test notes",
  project_id: "p1",
};
const rfqItems = [
  { id: "item1", material_name: "Steel", material_unit: "kg", quantity: 100, vendor_rate: 50 },
];

async function renderPage() {
  const { RFQsPage } = await import("@/pages/RFQsPage");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <RFQsPage />
      </QueryClientProvider>
    </MemoryRouter>
  );
}

async function selectProject() {
  const select = screen.getAllByRole("combobox")[0];
  await userEvent.click(select);
  await userEvent.click(screen.getByText("PRJ-001 — Test Project"));
}

describe("RFQsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    vi.mocked(api.listProjects).mockResolvedValue({ items: [project], total: 1 } as never);
    vi.mocked(api.listVendors).mockResolvedValue({ items: [vendor], total: 1 } as never);
  });

  it("renders header and select prompt when no project selected", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [], total: 0 } as never);
    await renderPage();
    expect(screen.getByText("RFQs")).toBeInTheDocument();
    expect(screen.getByText("Select a project to view RFQs.")).toBeInTheDocument();
  });

  it("loads and displays RFQs when project selected", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [rfq], total: 1 } as never);
    await renderPage();
    await selectProject();
    expect(await screen.findByText("RFQ-001")).toBeInTheDocument();
    expect(screen.getByText("Acme Vendor")).toBeInTheDocument();
    expect(screen.getByText("Draft")).toBeInTheDocument();
  });

  it("shows empty state for project with no RFQs", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [], total: 0 } as never);
    await renderPage();
    await selectProject();
    expect(await screen.findByText(/No RFQs for this project yet/)).toBeInTheDocument();
  });

  it("opens View dialog and shows RFQ detail", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [rfq], total: 1 } as never);
    vi.mocked(api.getRfq).mockResolvedValue({ ...rfq, items: rfqItems } as never);
    await renderPage();
    await selectProject();
    await screen.findByText("RFQ-001");
    await userEvent.click(screen.getByText("View"));
    expect(await screen.findByText("RFQ Detail")).toBeInTheDocument();
    expect(screen.getByText("Steel (kg) × 100")).toBeInTheDocument();
    expect(screen.getByText("₹50")).toBeInTheDocument();
  });

  it("handles send mutation error", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [rfq], total: 1 } as never);
    vi.mocked(api.sendRfq).mockRejectedValue(new Error("Send failed"));
    await renderPage();
    await selectProject();
    await screen.findByText("Send");
    await userEvent.click(screen.getByText("Send"));
    expect(await screen.findByRole("alert")).toHaveTextContent("Send failed");
  });

  it("dismisses action error", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [rfq], total: 1 } as never);
    vi.mocked(api.sendRfq).mockRejectedValue(new Error("Send failed"));
    await renderPage();
    await selectProject();
    await screen.findByText("Send");
    await userEvent.click(screen.getByText("Send"));
    await screen.findByRole("alert");
    await userEvent.click(screen.getByText("Dismiss"));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("shows Respond button for sent RFQs", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [{ ...rfq, status: "sent" }], total: 1 } as never);
    await renderPage();
    await selectProject();
    expect(await screen.findByText("Respond")).toBeInTheDocument();
  });

  it("shows Award button for responded RFQs", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [{ ...rfq, status: "responded" }], total: 1 } as never);
    await renderPage();
    await selectProject();
    expect(await screen.findByText("Award")).toBeInTheDocument();
  });

  it("hides action buttons for non-commercial users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [rfq], total: 1 } as never);
    await renderPage();
    await selectProject();
    await screen.findByText("RFQ-001");
    expect(screen.queryByText("Send")).not.toBeInTheDocument();
    expect(screen.queryByText("Respond")).not.toBeInTheDocument();
    expect(screen.queryByText("Award")).not.toBeInTheDocument();
  });

  it("hides New RFQ for non-commercial users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [], total: 0 } as never);
    await renderPage();
    expect(screen.queryByText("New RFQ")).not.toBeInTheDocument();
  });

  it("handles RFQ with no vendor name", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [{ ...rfq, vendor_name: null }], total: 1 } as never);
    await renderPage();
    await selectProject();
    expect(await screen.findByText("RFQ-001")).toBeInTheDocument();
  });

  it("handles RFQ with no rfq_number", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [{ ...rfq, rfq_number: null }], total: 1 } as never);
    await renderPage();
    await selectProject();
    expect(await screen.findByText("rfq1".slice(0, 8))).toBeInTheDocument();
  });

  it("shows RFQ detail loading state", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [rfq], total: 1 } as never);
    vi.mocked(api.getRfq).mockReturnValue(new Promise(() => {}));
    await renderPage();
    await selectProject();
    await screen.findByText("RFQ-001");
    await userEvent.click(screen.getByText("View"));
    expect(await screen.findByText("Loading...")).toBeInTheDocument();
  });

  it("shows empty notes in detail", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [rfq], total: 1 } as never);
    vi.mocked(api.getRfq).mockResolvedValue({ ...rfq, items: [], notes: null } as never);
    await renderPage();
    await selectProject();
    await screen.findByText("RFQ-001");
    await userEvent.click(screen.getByText("View"));
    expect(await screen.findByText("RFQ Detail")).toBeInTheDocument();
  });

  it("opens Create RFQ dialog", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [], total: 0 } as never);
    vi.mocked(api.listMaterials).mockResolvedValue({ items: [], total: 0 } as never);
    await renderPage();
    await selectProject();
    await screen.findByText("New RFQ");
    await userEvent.click(screen.getByText("New RFQ"));
    expect(await screen.findByText("Cancel")).toBeInTheDocument();
    expect(screen.getByText("Create RFQ")).toBeInTheDocument();
  });

  it("handles empty status filter message", async () => {
    vi.mocked(api.listProjectRfqs).mockResolvedValue({ items: [], total: 0 } as never);
    await renderPage();
    await selectProject();
    const statusSelect = screen.getAllByRole("combobox")[1];
    await userEvent.click(statusSelect);
    await userEvent.click(screen.getByText("Draft"));
    expect(await screen.findByText(/No RFQs match this status filter/)).toBeInTheDocument();
  });
});
