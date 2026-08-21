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
    listProjectInvoices: vi.fn(),
    getInvoice: vi.fn(),
  },
}));

vi.mock("@/components/financials/InvoiceCreateForm", () => ({
  InvoiceCreateForm: ({ projectId, onSuccess, onCancel }: any) => (
    <div data-testid="invoice-create-form">
      <span>Form for {projectId}</span>
      <button onClick={onSuccess}>Submit</button>
      <button onClick={onCancel}>Cancel</button>
    </div>
  ),
}));

const project = { id: "p1", code: "PRJ-001", name: "Test Project" };
const invoice = {
  id: "inv1",
  invoice_number: "INV-001",
  status: "draft",
  subtotal: "10000",
  tax_amount: "1800",
  total: "11800",
  due_date: "2026-03-01",
  notes: "Test invoice",
  project_id: "p1",
  items: [
    { id: "li1", description: "Design services", quantity: 1, rate: 10000, amount: 10000 },
  ],
};

async function renderPage(initialEntries: string[] = ["/"]) {
  const { InvoicesPage } = await import("@/pages/InvoicesPage");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <QueryClientProvider client={queryClient}>
        <InvoicesPage />
      </QueryClientProvider>
    </MemoryRouter>
  );
}

describe("InvoicesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    vi.mocked(api.listProjects).mockResolvedValue({ items: [project], total: 1 } as never);
  });

  it("renders header", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [], total: 0 } as never);
    await renderPage();
    expect(screen.getByText(/Billing per project/)).toBeInTheDocument();
  });

  it("shows select project message when no project selected", async () => {
    await renderPage();
    expect(screen.getByText(/Select a project to load invoices/)).toBeInTheDocument();
  });

  it("shows New Invoice button for commercial users", async () => {
    await renderPage();
    expect(screen.getByText("New Invoice")).toBeInTheDocument();
  });

  it("hides New Invoice for non-commercial users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    await renderPage();
    expect(screen.queryByText("New Invoice")).not.toBeInTheDocument();
  });

  it("loads and displays invoices", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText("INV-001")).toBeInTheDocument();
    expect(screen.getByText("Draft")).toBeInTheDocument();
  });

  it("shows empty state for project with no invoices", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [], total: 0 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText(/No invoices for this project yet/)).toBeInTheDocument();
  });

  it("opens invoice detail dialog", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    vi.mocked(api.getInvoice).mockResolvedValue(invoice as never);
    await renderPage(["/?project=p1"]);
    await screen.findByText("INV-001");
    await userEvent.click(screen.getByText("View"));
    expect(await screen.findByText("Invoice detail")).toBeInTheDocument();
  });

  it("shows invoice detail with line items", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    vi.mocked(api.getInvoice).mockResolvedValue(invoice as never);
    await renderPage(["/?project=p1"]);
    await screen.findByText("INV-001");
    await userEvent.click(screen.getByText("View"));
    expect(await screen.findByText("Design services")).toBeInTheDocument();
  });

  it("shows invoice detail loading state", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    vi.mocked(api.getInvoice).mockReturnValue(new Promise(() => {}));
    await renderPage(["/?project=p1"]);
    await screen.findByText("INV-001");
    await userEvent.click(screen.getByText("View"));
    expect(await screen.findByText(/Loading/)).toBeInTheDocument();
  });

  it("shows invoice notes and project link in detail", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    vi.mocked(api.getInvoice).mockResolvedValue(invoice as never);
    await renderPage(["/?project=p1"]);
    await screen.findByText("INV-001");
    await userEvent.click(screen.getByText("View"));
    expect(await screen.findByText(/Notes:/)).toBeInTheDocument();
    expect(screen.getByText("Open project")).toBeInTheDocument();
  });

  it("handles invoice without notes", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    vi.mocked(api.getInvoice).mockResolvedValue({ ...invoice, notes: null } as never);
    await renderPage(["/?project=p1"]);
    await screen.findByText("INV-001");
    await userEvent.click(screen.getByText("View"));
    expect(await screen.findByText("Invoice detail")).toBeInTheDocument();
    expect(screen.queryByText(/Notes:/)).not.toBeInTheDocument();
  });

  it("shows Refresh button", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText("Refresh")).toBeInTheDocument();
  });

  it("opens create invoice dialog", async () => {
    await renderPage();
    const select = screen.getAllByRole("combobox")[0];
    await userEvent.click(select);
    await userEvent.click(screen.getByText("PRJ-001 \u2014 Test Project"));
    await screen.findByText("New Invoice");
    await userEvent.click(screen.getByText("New Invoice"));
    expect(await screen.findByText("New invoice")).toBeInTheDocument();
  });

  it("shows loading state in table", async () => {
    vi.mocked(api.listProjectInvoices).mockReturnValue(new Promise(() => {}));
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText(/Loading/)).toBeInTheDocument();
  });

  it("shows error banner on project load failure", async () => {
    vi.mocked(api.listProjects).mockRejectedValue(new Error("boom"));
    await renderPage();
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });

  it("displays invoice total with formatting", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText("INV-001")).toBeInTheDocument();
    expect(screen.getByText(/11,800/)).toBeInTheDocument();
  });

  it("displays fallback invoice id when no number", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [{ ...invoice, invoice_number: null }], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText("inv1".slice(0, 8))).toBeInTheDocument();
  });

  it("syncs project from search params", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText("INV-001")).toBeInTheDocument();
  });

  it("displays all status filter options", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [], total: 0 } as never);
    await renderPage();
    const statusSelect = screen.getAllByRole("combobox")[1];
    await userEvent.click(statusSelect);
    expect(screen.getByRole("option", { name: "All status" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Draft" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Sent" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Paid" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Cancelled" })).toBeInTheDocument();
  });

  it("handles invoice without items in detail", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    vi.mocked(api.getInvoice).mockResolvedValue({ ...invoice, items: [] } as never);
    await renderPage(["/?project=p1"]);
    await screen.findByText("INV-001");
    await userEvent.click(screen.getByText("View"));
    expect(await screen.findByText("Invoice detail")).toBeInTheDocument();
  });

  it("handles invoice without project_id in detail", async () => {
    vi.mocked(api.listProjectInvoices).mockResolvedValue({ items: [invoice], total: 1 } as never);
    vi.mocked(api.getInvoice).mockResolvedValue({ ...invoice, project_id: null } as never);
    await renderPage(["/?project=p1"]);
    await screen.findByText("INV-001");
    await userEvent.click(screen.getByText("View"));
    expect(await screen.findByText("Invoice detail")).toBeInTheDocument();
    expect(screen.queryByText("Open project")).not.toBeInTheDocument();
  });
});
